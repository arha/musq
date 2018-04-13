__author__ = 'arha'
from platforms import platform_abstract
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib

class platform_linux(platform_abstract.platform_abstract):
    def __init__(self):
        super(  platform_linux, self).__init__()
        self.name = "x86_linux"
        logging.debug("Platform init: x86_linux")

    def setup(self):
        super(  platform_linux, self).setup()

    def signal_exit(self):
        super(  platform_linux, self).setup()


    def get_all_if_data(self):
        nic = []
        for ix in socket.if_nameindex():
            name = ix[1]
            record = self.get_data_for_if( name )
            if (record != None):
                nic.append( record )

        return (nic)

    def get_all_ips(self):
        # TODO: /sys/class/net/<iface>/address
        nic = []

        for ix in socket.if_nameindex():
            name = ix[1]
            result = self.get_data_for_if( name )
            if (result != None and result.get('ip') != None):
                ip = result['ip']
                if (ip[0:4] != "127."):
                    nic.append( ip )

        return (', '.join(nic))

    def get_data_for_if( self, ifname):
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
            if ('eth' in nic['name'] or 'br' in nic['name']):
                macs.append (nic['mac'])
        macs = (''.join(macs)).replace(":", "")

        input_str = ""
        if (self.musq.settings.get('musq_id_salt_hostname') != None):
            input_str = env['hostname'] + ":"
        if (self.musq.settings.get('musq_id_extra_salt') != None):
            salt = str(self.musq.settings.get('musq_id_extra_salt'))
            input_str = input_str + salt + ":"
        input_str += self.name + ":" + serial + macs
        result = input_str
        for i in range(1,9):
            # print (result)
            result = hashlib.md5(result.encode("UTF-8")).hexdigest().upper()
        result=result[0:4]
        logging.debug("Calculated system musq_id=%s from hash string \"%s\"" % (result, input_str))
        return result