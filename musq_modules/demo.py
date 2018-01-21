from musq_modules import abstract
import logging

class mm_demo(abstract.mm_abstract):
    def __init__(self):
        prefix="demo"

    def call(self, topic, trigger_topic, message, config_line): 
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)

    def link(self):
        logging.debug("demo linked!")
