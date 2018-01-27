from musq_modules import abstract
import logging
#!/usr/bin/env python
import time

class mm_pizero(abstract.mm_abstract):
    def __init__(self):
        prefix="pizero"

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



    def link(self):
        logging.debug("pizero linked!")

    def set_creator(self, creator):
        self.creator = creator
