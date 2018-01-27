from musq_modules import abstract
import logging
#!/usr/bin/env python
import time
import threading
from time import sleep

class mm_pizero(abstract.mm_abstract):
    def __init__(self):
        prefix="pizero"
        self.last_send=0

    def call(self, topic, trigger_topic, message, config_line): 
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)
        
        topic_p=trigger_topic.split('/')
        if (len(topic_p) < 4):
            logging.debug("Invalid pizero topic: " + trigger_topic)
        else:
            m=message.payload.decode('UTF-8')

            if (topic_p[len(topic_p)-1] == 'led'):
                # reverse logic
                if (m == "1"):
                    with open("/sys/class/leds/led0/brightness", "w") as file:
                        file.write("0")
                if (m == "0"):
                    with open("/sys/class/leds/led0/brightness", "w") as file:
                        file.write("1")
    def main(self):
        # entry point for the thread
        while True:
            sleep (1)
            ts = time.time()
            if (ts - self.last_send > 10):
                logging.debug("opi_one thread: reading temperature")
                data = "-1" 
                # /sys/devices/virtual/thermal/thermal_zone{0,1}/temp
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
                    data=file.readline()
                    data = round(float(data) / 1000, 1)
                message = {}
                message['type']='pub'
                message['topic']='/example/pizero/temperature'
                message['payload']=str(data).encode('UTF-8')
                self.creator.bug(self, message)
                self.last_send=ts
        logging.debug("Thread finished on thread_test")

    def run(self):
        logging.debug("thread start")
        t1 = threading.Thread(target=self.main)
        t1.start()

    def link(self):
        logging.debug("pizero linked!")

    def set_creator(self, creator):
        self.creator = creator
