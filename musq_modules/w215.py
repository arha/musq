from musq_modules import abstract
import time
import logging
import threading
from pyW215.pyW215 import SmartPlug, ON, OFF
from time import sleep

class mm_w215(abstract.mm_abstract):
    def __init__(self):
        self.prefix="w215"
        self.last_send=time.time()
        self.last_send=0

        self.__sp = ""

    def call(self, topic, trigger_topic, message, config_line): 
        
        m=message.payload.decode('UTF-8')

        if (m  == '0'):
            self.sp.state = OFF
        elif (m  == '1'):
            self.sp.state = ON
        return

    def link(self, creator, settings):
        super(  mm_w215, self).link(creator, settings)
        logging.debug("*** w215 (%s) linked!", self.my_id)

        ip = self.settings.get("ip")
        pin = self.settings.get("pin")
        if (ip == None or pin == None):
            if (ip == None):
                logging.info("w215 is missing ip")
            if (pin == None):
                logging.info("w215 is missing pin")
            self.sp = None
            return False

        self.sp = SmartPlug(ip, str(pin))
        try:
            if (self.sp is None):
                self.sp = None
        except NameError:
            logging.info("w215 at %s with pin %s failed to connect", ip, pin)
            self.sp = None
            return False

        if (self.sp != None and self.sp._error_report != False):
            logging.info("w215 at %s with pin %s failed to connect", ip, pin)
            return False


        if (self.sp != None):
            logging.debug("*** connected to w215 plug at %s", self.settings['ip'])

    def main(self):
        # entry point for the thread
        while True:
            sleep (0.25)
            ts = time.time()
            if (ts - self.last_send > 5):
                message = {}
                message['type']='pub'
                message['topic']='/test/module/thread/notbeat'
                message['payload']=str(ts).encode('UTF-8')
                self.creator.bug(self, message)
                self.last_send=ts
        logging.debug("Thread finished on thread_test")

    def run(self):
        logging.debug("thread start")
        t1 = threading.Thread(target=self.main)
        t1.start()

    def set_creator(self, creator):
        self.creator = creator
