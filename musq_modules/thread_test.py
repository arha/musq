from musq_modules import abstract
import time
import logging
import threading
from time import sleep

class mm_thread_test(abstract.mm_abstract):
    def __init__(self):
        self.prefix="thread_test"
        self.last_send=time.time()
        self.last_send=0

    def call(self, topic, trigger_topic, message, config_line): 
        return
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)

    def link(self):
        logging.debug("thread_demo linked!")

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
