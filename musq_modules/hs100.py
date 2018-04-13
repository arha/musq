from musq_modules import abstract
import time
import logging
import threading
from time import sleep
from pyHS100 import SmartPlug

class mm_hs100(abstract.mm_abstract):
    def __init__(self):
        self.internal_name = "hs100"
        self.last_send = time.time()
        self.last_send = 0

        self.sp = None

    def on_message_received(self, topic, trigger_topic, message, config_line):
        m = message.payload.decode('UTF-8')

        if m  == '1':
            self.sp.turn_on()
        elif m  == '0':
            self.sp.turn_off()
        return

    def link(self, musq_instance, settings):
        super(mm_hs100, self).link(musq_instance, settings)
        logging.debug("*** hs100 linked!")

        ip = self.settings.get("ip")
        if (ip == None):
            logging.info("hs100 at %s failed to connect", ip)
            self.sp = None
            return False

        self.sp = SmartPlug(ip)
        try:
            if self.sp is None:
                self.sp = None
        except NameError:
            logging.info("hs100 at %s failed to connect", ip)
            self.sp = None
            return False

        if self.sp is not None:
            logging.debug("*** connected to hs100 plug at %s", self.settings['ip'])

    def main(self):
        while True:
            sleep(0.25)
            ts = time.time()
            if ts - self.last_send > 5:
                pass
        logging.debug("Thread finished on thread_test")

    def run(self):
        logging.debug("thread start")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()
