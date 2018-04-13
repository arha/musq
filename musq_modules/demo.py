from musq_modules import abstract
import logging

class mm_demo(abstract.mm_abstract):
    def __init__(self):
        prefix="demo"

    def on_message_received(self, topic, trigger_topic, message, config_line):
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)
        logging.debug("id = %s", self.my_id)

    def link(self, musq_instance, settings):
        super(mm_demo, self).link(musq_instance, settings)
        logging.debug("demo (%s) linked!", self.my_id)
