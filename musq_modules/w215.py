from musq_modules import abstract
import time
import logging
import threading
from pyW215.pyW215 import SmartPlug, ON, OFF
from time import sleep

class mm_w215(abstract.mm_abstract):
    def __init__(self):
        self.internal_name = "w215"
        self.last_send  =time.time()
        self.last_send = 0
        self.__sp = ""

    def on_message_received(self, topic, trigger_topic, message, config_line):
        m = message.payload.decode('UTF-8')
        if m  == '0':
            self.sp.state = OFF
        elif m  == '1':
            self.sp.state = ON
        return

    def link(self, musq_instance, settings):
        super(mm_w215, self).link(musq_instance, settings)

        ip = self.settings.get("ip")
        pin = self.settings.get("pin")
        if ip is None or pin is None:
            if ip is None:
                logging.info("w215 is missing ip")
            if pin is None:
                logging.info("w215 is missing PIN code. You can find it on the plug itself, printed on a label")
            self.sp = None
            return False

        self.sp = None
        try:
            self.sp = SmartPlug(ip, str(pin))
            if self.sp is None:
                self.sp = None
        except NameError:
            logging.info("w215 at %s with pin %s failed to connect", ip, pin)
            self.sp = None
            return False
        except Exception:
            logging.info("w215 at %s with pin %s failed to connect", ip, pin)
            self.sp = None
            return False

        if self.sp is not None and self.sp._error_report is not False:
            logging.info("w215 at %s with pin %s failed to connect", ip, pin)
            return False

        if self.sp is not None:
            logging.debug("*** connected to w215 plug at %s", self.settings['ip'])
            logging.debug("*** w215 (%s) linked!", self.my_id)

    def main(self):
        while True:
            sleep (0.25)
            ts = time.time()
            if ts - self.last_send > 5:
                self.last_send=ts
        logging.debug("Thread finished on thread_test")

    def run(self):
        logging.debug("thread start")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()