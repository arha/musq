from musq_modules import abstract
import logging

class mm_dummy(abstract.mm_abstract):
    def __init__(self):
        self.internal_name = "dummy"

    def test(self): 
        pass

    def link(self, musq_instance, settings):
        super(mm_dummy, self).link(musq_instance, settings)
        logging.debug("dummy linked!")

    def on_message_received(self, topic, trigger_topic, message):
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)

    def run(self):
        """ dummy module, does nothing """
