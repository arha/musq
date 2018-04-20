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

        self.plug = None

    def on_message_received(self, topic, trigger_topic, message, config_line):
        m = message.payload.decode('UTF-8')

        if m  == '1':
            self.plug.turn_on()
        elif m  == '0':
            self.plug.turn_off()
        return

    def link(self, musq_instance, settings):
        super(mm_hs100, self).link(musq_instance, settings)
        logging.debug("*** hs100 linked!")

        ip = self.settings.get("ip")
        if (ip == None):
            logging.info("hs100 at %s failed to connect", ip)
            self.plug = None
            return False

        self.plug = SmartPlug(ip)
        try:
            if self.plug is None:
                self.plug = None
        except NameError:
            logging.info("hs100 at %s failed to connect", ip)
            self.plug = None
            return False

        if self.plug is not None:
            logging.debug("*** connected to hs100 plug at %s", self.settings['ip'])
            logging.debug("Plug name (alias): %s" % self.plug.alias) 
            logging.debug("Hardware: %s" % self.plug.hw_info) 
            logging.debug("Sysinfo: %s" % self.plug.hw_info)
            logging.debug("Plug time=[%s], timezone=[%s]" % (self.plug.time, self.plug.timezone))

    """
    def main(self):
        while True and not self.kill_thread:
            sleep(0.5)
            ts = time.time()
        logging.debug("Thread finished on hs100")

    def run(self):
        # this should
        logging.debug("thread start")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()
        """
