from musq_modules import abstract
import logging

class mm_dummy(abstract.mm_abstract):
    def __init__(self):
        prefix="dummy"

    def test(self): 
        pass

    def link(self):
        logging.debug("dummy linked!")

    def call(self, topic, trigger_topic, message, config_line): 
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)

