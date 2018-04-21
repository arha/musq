from musq_modules import abstract
import logging
import sys
import time
import threading
import re

from musq_libs.serialbox.serialbox import Serialbox

class mm_serial(abstract.mm_abstract):
    def __init__(self):
        self.internal_name="serial"
        self.serialbox = None
        self.patterns = []

    def on_message_received(self, topic, trigger_topic, message):
        try:
            self.serialbox.write(message.payload)
        except:
            logging.debug("Serial error: %s" % sys.exc_info())

    def on_serial_packet(self, data):
        logging.debug("Rxed serial data: %s" % data)
        self.find_matching_pattern(data.decode("UTF-8"))

    def find_matching_pattern(self, data):
        for p in self.patterns:
            pattern = p.get("pattern")

            match_object = re.search(pattern, data)
            if match_object:
                #print("OK!! Check [%s] against [%s]" % (pattern, data))
                #print(match_object, match_object.groups())
                message = p.get("message") or ""
                # replace resulting capture groups with requested once, unmatched ones will remain as $x
                group_id = 1
                for group in match_object.groups():
                    message = message.replace("$" + str(group_id), group)
                    group_id += 1
                    #print("Replaced %s with %s" % (str(group_id), group))
                topic = p.get("output")
                if topic is not None:
                    self.musq_instance.raw_publish(self, message, topic)
            else:
                pass
                #print ("FAIL Check [%s] against [%s]" % (pattern, data))

    def link(self, musq_instance, settings):
        super(mm_serial, self).link(musq_instance, settings)
        try:
            self.serialbox = Serialbox("COM6", 115200, packetReceivedCallbackFunc=self.on_serial_packet)
            self.serialbox.connect()
        except:
            exc = str(sys.exc_info())
            logging.debug("Serial failed to connect: %s" % exc)
            return False

        for dict_message in self.settings.get("patterns"):
            for message, data in dict_message.items():
                message_conf = data
                if message_conf.get("pattern") is None:
                    logging.warning("No pattern defined in serial (%s)" % self.instance_name)
                    continue
                if message_conf.get("output") is not None:
                    self.patterns.append(message_conf)
                else:
                    logging.warning("serial (%s), pattern %s has no output topic. add a \"topic\" where the incoming message will be sent." % (self.instance_name, message_conf.get("pattern") ))

        logging.debug("serial (%s) linked!", self.instance_name)
        return True

    def signal_exit(self):
        super(mm_serial, self).signal_exit()
        self.serialbox.close()