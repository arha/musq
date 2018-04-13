__author__ = 'arha'
from platforms import platform_abstract, platform_linux
import logging
import socket, fcntl, struct    # needed to get the IPs of this device
import sys, hashlib
from enum import Enum

# TODO: leds pi zero w:
# root@rpi-zero-arha:/sys/class/leds/led0# echo "1" > /sys/class/leds/led0/brightness
# root@rpi-zero-arha:/sys/class/leds/led0# echo "0" > /sys/class/leds/led0/brightness

class Rpi_board(Enum):
    UNKNOWN = 0
    PI_MODEL_A = 1
    PI_MODEL_B = 2
    PI_MODEL_B_PLUS = 3
    PI_COMPUTE = 4
    PI2_MODEL_B = 5
    PI_ZERO = 6
    PI_ZERO_W = 7
    PI3_MODEL_B = 8
    PI3_MODEL_B_PLUS = 9

class Rpi_hats(Enum):
    NONE = 0
    PIMORONI_UNICORN_64=100


class platform_rpi(platform_linux.platform_linux):
    def __init__(self):
        super(  platform_rpi, self).__init__()
        self.name = "rpi"
        logging.debug("Platform init: rpi")

    def setup(self):
        super(  platform_rpi, self).setup()
        self.platform_detect_extended()
        self.platform_detect_hat()

    def signal_exit(self):
        super(  platform_rpi, self).setup()

    def platform_detect_extended(self):
        str1 = self.musq.get_first_line("/sys/firmware/devicetree/base/model").strip()
        str2 = self.musq.get_first_line("/proc/device-tree/model").strip()
        self.model_string = str1 or str2
        self.model = Rpi_board.UNKNOWN
        # maybe using Revision numbers is better? like a02082... https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
        if ("3 Model B Rev" in self.model_string):
            self.model = Rpi_board.PI3_MODEL_B
        elif ("3 Model B Plus Rev" in self.model_string):   # eeeh... idk
            self.model = Rpi_board.PI3_MODEL_B_PLUS
        elif ("Raspberry Pi Zero W" in self.model_string):
            self.model = Rpi_board.PI_ZERO_W

        logging.debug("RPi model: %s (%s)" % (self.model, self.model_string))

    def get_env_data(self):
        result = super(  platform_rpi, self).get_env_data()
        result.update({"platform": "raspberry pi"})
        return result

    def platform_detect_hat(self):
        # https://www.raspberrypi.org/forums/viewtopic.php?t=108134
        # https://raspberrypi.stackexchange.com/questions/39153/how-to-detect-what-kind-of-hat-or-gpio-board-is-plugged-in-if-any
        
        hat_path = "/proc/device-tree/hat/"
        vendor      = self.musq.get_first_line(hat_path + "vendor").strip()
        product_id  = self.musq.get_first_line(hat_path + "product_id").strip()
        product_ver = self.musq.get_first_line(hat_path + "product_ver").strip()
        product     = self.musq.get_first_line(hat_path + "product").strip()

        self.hat = Rpi_hats.NONE
        if ("Unicorn HAT\0" == product and "0x9a17\0" == product_id):
            self.hat = Rpi_hats.PIMORONI_UNICORN_64
            self.hat_name = product.rstrip('\0')

        if (self.hat != Rpi_hats.NONE):
            logging.info("Detected RPi hat: %s " % self.hat)
            self.hat_setup()

    def hat_setup(self):
        logging.debug("Setting up hat %s" % self.hat_name)

    def get_all_if_data(self):
        nic = []
        for ix in socket.if_nameindex():
            name = ix[1]
            record = self.get_data_for_if(name
            if (record != None):
                nic.append(record)
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
