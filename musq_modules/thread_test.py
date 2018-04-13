from musq_modules import abstract
import time
import logging
import threading
from time import sleep

class mm_thread_test(abstract.mm_abstract):
    def __init__(self):
        self.internal_name = "thread_test"
        self.last_send = time.time()
        self.last_send = 0

    def on_message_received(self, topic, trigger_topic, message, config_line):
        return

    def link(self, musq_instance, settings):
        super(mm_thread_test, self).link(musq_instance, settings)
        logging.debug("thread_test linked!")

    def main(self):
        # entry point for the thread
        while True:
            sleep(0.25)
            ts = time.time()
            if ts - self.last_send > 5:
                topic = '/test/module/thread/notbeat'
                message = str(ts).encode('UTF-8')
                self.musq_instance.raw_publish(self, message, topic)
                self.last_send = ts
        logging.debug("Thread finished on thread_test")

    def run(self):
        logging.debug("thread start")
        t1 = threading.Thread(target=self.main)
        t1.start()

    def set_creator(self, creator):
        self.musq_instance = creator
