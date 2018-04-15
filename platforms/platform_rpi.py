__author__ = 'arha'
from platforms import platform_abstract, platform_linux
import logging
import socket 
import fcntl
import struct    # needed to get the IPs of this device
import sys
import hashlib
import time
import threading
from enum import Enum
import RPi.GPIO as GPIO

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
        self.internal_name = "rpi"
        logging.debug("Platform init: rpi")
        self.hat = Rpi_hats.NONE
        self.hat_name = ""
        self.model_string = ""
        self.topic = []
        self.autotopic = ""
        self.kill_thread = False
        self.last_send = 0
        self.load_pin_config()
        self.target = 0

    def setup(self):
        super(  platform_rpi, self).setup()
        self.platform_detect_extended()
        self.platform_detect_hat()
        topic_prefix = "/musq/dev/" + self.musq.musq_id
        self.topic = [ topic_prefix + "/#" ]
        self.autotopic = topic_prefix

    def signal_exit(self):
        super(platform_rpi, self).setup()
        self.kill_thread = True
        GPIO.cleanup()

    def platform_detect_extended(self):
        str1 = self.musq.get_first_line("/sys/firmware/devicetree/base/model").strip()
        str2 = self.musq.get_first_line("/proc/device-tree/model").strip()
        self.model_string = str1 or str2
        self.model = Rpi_board.UNKNOWN
        # maybe using Revision numbers is better? like a02082... https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
        if "3 Model B Rev" in self.model_string:
            self.model = Rpi_board.PI3_MODEL_B
        elif "3 Model B Plus Rev" in self.model_string:
            self.model = Rpi_board.PI3_MODEL_B_PLUS
        elif "Raspberry Pi Zero W" in self.model_string:
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
        vendor          = self.musq.get_first_line(hat_path + "vendor").strip()
        product_id      = self.musq.get_first_line(hat_path + "product_id").strip()
        product_ver    = self.musq.get_first_line(hat_path + "product_ver").strip()
        product         = self.musq.get_first_line(hat_path + "product").strip()

        if "Unicorn HAT\0" == product and "0x9a17\0" == product_id:
            self.hat = Rpi_hats.PIMORONI_UNICORN_64
            self.hat_name = product.rstrip('\0')

        if self.hat != Rpi_hats.NONE:
            logging.info("Detected RPi hat: %s " % self.hat)
            self.hat_setup()

    def hat_setup(self):
        logging.debug("Setting up hat %s" % self.hat_name)

    def on_message_received(self, topic, trigger_topic, message, config_line):
        self.process_message(trigger_topic, message.payload.decode("UTF-8"))
        return

    def io_rising_callback(self, channel):
        self.musq.self_publish(self, "1", "status/" + str(channel))

    def io_falling_callback(self, channel):
        self.musq.self_publish(self, "0", "status/" + str(channel))

    def main(self):
        GPIO.setmode(GPIO.BOARD)
        last_heartbeat = time.time()
        while True and not self.kill_thread:
            time.sleep(0.25)
            ts = time.time()
            if ts - self.last_send > 0.25:
                if ts - last_heartbeat >= 60:
                    self.musq.heartbeat()
                    last_heartbeat = ts
                self.last_send = ts
        logging.debug("Thread finished on RPi platform")

    def split_topic(self, trigger_topic):
        for topic in self.topic:
            topic = topic.replace('/#', '')
            #TODO there must be a better way to manage self-generated topics and how to match them
            #print("split %s, trigger=%s" % (topic, trigger_topic))
            #print( trigger_topic.startswith(topic) )
            if topic is not None and trigger_topic.startswith(topic):
                subtopic = trigger_topic[len(topic):]
                parts = subtopic.split("/")
                if parts[0].strip() == "":
                    del (parts[0])
                return parts

    def process_message(self, topic, message):
        topic_parts = self.split_topic(topic)
        if topic_parts[0].lower() == "gpio":
            self.do_gpio(topic_parts, message)

    def do_gpio(self, topic_parts, message):
        if len(topic_parts) == 1:
            return
        command = topic_parts[1].lower().strip()

        if command == "target":
            if not self.set_target_io(message):
                return
            self.user_info("Pin %s is now the target I/O pin" % self.target)
            self.user_error("")

        elif command == "write":
            if self.set_target_io_from_topic(topic_parts) is not None:
                if message.strip != "":
                    self._io_write(self.target, message)

        elif command == "read":
            if self.set_target_io_from_topic(topic_parts) is not None:
                value = self._io_read(self.target)
                self.musq.self_publish(self, value, "status/" + str(self.target))

        elif command == "rising_event":
            if self.set_target_io_from_topic(topic_parts) is not None:
                if message == "1" or message == "":
                    try:
                        GPIO.add_event_detect(self.target, GPIO.RISING, callback=self.io_rising_callback, bouncetime=50)
                        self.user_info("Pin %s will publish rising events to /status/%s" % (self.target, self.target))
                    except RuntimeError:
                        self.user_info("Runtime error setting rising event, perhaps the falling one is already set?")
                elif message == "0":
                    GPIO.remove_event_detect(self.target)
                    self.user_info("Pin %s will not publish rising events" % self.target)

        elif command == "falling_event":
            if self.set_target_io_from_topic(topic_parts) is not None:
                if message == "1" or message == "":
                    try:
                        GPIO.add_event_detect(self.target, GPIO.FALLING, callback=self.io_falling_callback, bouncetime=50)
                        self.user_info("Pin %s will publish falling events to /status/%s" % (self.target, self.target))
                    except RuntimeError:
                        # TODO: GPIO.BOTH and some logic to allow the user to mix them however he wants
                        self.user_info("Runtime error setting falling event, perhaps the rising one is already set?")
                elif message == "0":
                    GPIO.remove_event_detect(self.target)
                    self.user_info("Pin %s will not publish falling events" % self.target)

    def set_target_io_from_topic(self, topic_parts):
        if len(topic_parts) >= 2:
            new_target = topic_parts[2]
        if self.set_target_io(new_target) is None:
            return None
        else:
            return self.target

    def set_target_io(self, message):
        try:
            target = int(message)
        except ValueError:
            self.user_error("Invalid I/O pin: %s" % message)
            return None
        if target not in self.iopins:
            self.user_error("Pin %s is not an I/O pin" % message)
            return None
        else:
            self.target = int(message)
            logging.debug("Set target pin %s from topic", self.target)
            return target

    def _io_read(self, pin):
        if pin is None or pin not in self.iopins:
            logging.warning("Could not read, invalid pin name %s" % pin)
            self.user_error("Could not read, invalid pin name %s" % pin)
            return
        try:
            value = GPIO.input(pin)
            if value or value is GPIO.HIGH:
                return "1"
            else:
                return "0"
        except RuntimeError:
            GPIO.setup(self.target, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
            try:
                value = GPIO.input(pin)
                logging.warning("Pin %s set as input" % pin)
                self.user_error("Warning: Pin %s set as input" % pin)
                if value or value is GPIO.HIGH:
                    return "1"
                else:
                    return "0"
            except RuntimeError:
                logging.warning("Could not read pin %s even after setting input" % pin)
                self.user_error("Could not read pin %s even after setting input" % pin)


    def _io_write(self, pin, value):
        # verilog like: U, X, 0, 1, Z, W, L, H, - (we're only using 0, 1, z, w, l and disregard the case)
        m = value.lower()
        if pin is None or pin not in self.iopins:
            logging.warning("Could not write, invalid pin name %s" % pin)
            self.user_error("Could not write, invalid pin name %s" % pin)
            return

        if m == '1' or m == 'on':
            GPIO.setup(self.target, GPIO.OUT, initial=GPIO.HIGH)
            log_line = "Set pin %s to 1 (output, strong high)" % pin
            self.user_info(log_line)
            logging.debug(log_line)

        if m == '0' or m == "off" or m == "of":
            GPIO.setup(self.target, GPIO.OUT, initial=GPIO.LOW)
            log_line = "Set pin %s to 1 (output, strong low)" % pin
            self.user_info(log_line)
            logging.debug(log_line)

        if m == 'z' or m == 'in':
            # no pull-up, no pulldown
            GPIO.setup(self.target, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
            log_line = "Set pin %s to high z (input, no pullup, no pulldown)" % pin
            self.user_info(log_line)
            logging.debug(log_line)

        if m == 'l' or m == 'w0' or m == 'z0':
            GPIO.setup(self.target, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            log_line = "Set pin %s to weak low (input, pulldown)" % pin
            self.user_info(log_line)
            logging.debug(log_line)

        if m == 'h' or m == 'w1' or m == 'z1':
            GPIO.setup(self.target, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            log_line = "Set pin %s to weak low (input, pullup)" % pin
            self.user_info(log_line)
            logging.debug(log_line)

    def user_error(self, message):
        if message != "":
            message = self.musq.formatted_time() + " " + message
        self.musq.self_publish(self, message, 'error', 2, False)

    def user_info(self, message):
        if message != "":
            message = self.musq.formatted_time() + " " + message
        self.musq.self_publish(self, message, 'info', 2, False)

    def run(self):
        logging.debug("RPi thread start")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def generate_musq_id(self):
        # used as a unique identifier in /musq/[id] and /musq/heartbeat/[id] so a device can be reliably identified in the mqtt topic tree
        # combines the following strings hostname : user supplied string + platform name  + cpu_serial_number + list_of_eth_macs_concatenated
        # optionally, it can prepend the hostname (so you can swap SD cards with different musq installations - making the board identify itself differently, depending on its hostname) and it can also prepend some user supplied value
        # runs it through 8 runs of md5 and grabs the first 2 bytes in hex, that's your musq id
        # this id should survive a system change
        # ids will probably clash, given enough boards...

        env = self.musq.get_env_data()
        serial = env.get("serial") or ""
        macs = []
        nics = self.get_all_if_data()
        nics = (sorted(nics, key=lambda k: (k['name']).lower() ))
        # TODO: maybe exclude bridges or check how to grab mac of components
        for nic in nics:
            if 'eth' in nic['name'] or 'br' in nic['name']:
                macs.append (nic['mac'])
        macs = (''.join(macs)).replace(":", "")
        print ("*** macs [%s]" % macs)
        input_str = ""
        if self.musq.settings.get('musq_id_salt_hostname') is not None:
            input_str = env['hostname'] + ":"
        if self.musq.settings.get('musq_id_extra_salt') is not None:
            salt = str(self.musq.settings.get('musq_id_extra_salt'))
            input_str = input_str + salt + ":"
        input_str += self.internal_name + ":" + serial + macs
        result = input_str
        for i in range(1,9):
            result = hashlib.md5(result.encode("UTF-8")).hexdigest().upper()
        result=result[0:4]
        logging.debug("Calculated system musq_id=%s from hash string \"%s\"" % (result, input_str))
        return result

    def load_pin_config(self):
        self.iopins = [3, 5, 7, 8,  10, 11, 12, 13,  15, 16, 18, 19,  21, 22, 23, 24,  26, 29, 31, 32,  33, 35, 36, 37,  38, 40]
