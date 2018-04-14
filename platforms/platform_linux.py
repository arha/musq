__author__ = 'arha'
from platforms import platform_abstract
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib, re, subprocess

class platform_linux(platform_abstract.platform_abstract):
    def __init__(self):
        super(platform_linux, self).__init__()
        self.internal_name = "x86_linux"
        logging.debug("Platform init: x86_linux")

    def setup(self):
        super(platform_linux, self).setup()

    def signal_exit(self):
        super(platform_linux, self).setup()

    def get_env_data(self):
        env = super(  platform_linux, self).get_env_data()
        env.update({"platform": "linux generic"})
        val = (self.musq.get_from_shell("hostname")).strip()
        # val = (self.musq.get_from_shell("hostname").decode("UTF-8")).strip()
        if val == "":
            val = "unknown"
        env['hostname']  = val

        env['uptime'] = self.musq.get_from_shell(" awk '{print int($1)}' /proc/uptime")

        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).strip()
        for line in all_info.split(b"\n"):
            line = line.decode("utf-8")
            if "Processor" in line:
                env['cpu'] = (re.sub( ".*Processor.*:", "", line, 1)).strip()
            if "Hardware" in line:
                env['hw'] = (re.sub( ".*Hardware.*:", "", line, 1)).strip()
            if "Serial" in line:
                env['serial'] = (re.sub( ".*Serial.*:", "", line, 1)).strip()

        env['temp'] = self.musq.get_first_line('/etc/armbianmonitor/datasources/soctemp', strip=True)
        env['temp1'] = self.musq.get_first_line('/sys/devices/virtual/thermal/thermal_zone0/temp', strip=True)
        env['temp2'] = self.musq.get_first_line('/sys/devices/virtual/thermal/thermal_zone1/temp', strip=True)
        env['ip'] = self.get_all_ips()
        return env

    def get_all_if_data(self):
        nic = []
        for ix in socket.if_nameindex():
            name = ix[1]
            record = self.get_data_for_if(name)
            if record is not None:
                nic.append(record)
        return (nic)

    def get_all_ips(self):
        # TODO: /sys/class/net/<iface>/address
        nic = []

        for ix in socket.if_nameindex():
            name = ix[1]
            result = self.get_data_for_if( name )
            if result is not None and result.get('ip') is not None:
                ip = result['ip']
                if ip[0:4] != "127.":
                    nic.append(ip)

        return ', '.join(nic)

    def get_data_for_if(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            info = fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode("UTF-8"))
            )
            ip = socket.inet_ntoa(info[20:24])

            info = fcntl.ioctl(
                s.fileno(),
                0x8927,
                struct.pack('256s', ifname[:15].encode("UTF-8"))
            )
            mac = ':'.join(['%02x' % (char) for char in info[18:24]])
            result = {"name": ifname, "ip": ip, "mac": mac}
        except OSError:
            logging.warning("Cannot get ip/mac of interface %s, error %s: %s" % (ifname, sys.exc_info()[0], sys.exc_info()[1]))
            result = None
        return result

    def generate_musq_id(self):
        # used as a unique identifier in /musq/[id] and /musq/heartbeat/[id] so a device can be reliably identified in the mqtt topic tree
        # combines the following strings hostname : user supplied string + platform name  + cpu_serial_number + list_of_eth_macs_concatenated
        # optionally, it can prepend the hostname (so you can swap SD cards with different musq installations - making the board identify itself differently, depending on its hostname) and it can also prepend some user supplied value
        # runs it through 8 runs of md5 and grabs the first 2 bytes in hex, that's your musq id
        # this id should survive a system change
        # ids will probably clash, given enough boards...

        env = self.musq.get_env_data()
        # TODO serial number on x86
        serial = env.get("serial") or ""
        macs = []
        nics = self.get_all_if_data()
        nics = (sorted(nics, key=lambda k: (k['name']).lower() ))
        # TODO: maybe exclude bridges or check how to grab mac of components
        for nic in nics:
            if 'eth' in nic['name'] or 'br' in nic['name']:
                macs.append (nic['mac'])
        macs = (''.join(macs)).replace(":", "")

        input_str = ""
        if self.musq.settings.get('musq_id_salt_hostname') is not None:
            input_str = env['hostname'] + ":"
        if self.musq.settings.get('musq_id_extra_salt') is not None:
            salt = str(self.musq.settings.get('musq_id_extra_salt'))
            input_str = input_str + salt + ":"
        input_str += self.internal_name + ":" + serial + macs
        result = input_str
        for i in range(1, 9):
            result = hashlib.md5(result.encode("UTF-8")).hexdigest().upper()
        result = result[0:4]
        logging.debug("Calculated system musq_id=%s from hash string \"%s\"" % (result, input_str))
        return result
