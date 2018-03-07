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
        logging.debug("id = %s", self.__id)
        logging.debug("ip = %s", self.__settings['ip'])

    def link(self, creator, settings):
        super(  mm_demo, self).link(creator, settings)
        logging.debug("demo (%s) linked!", self.id)

    def set_creator(self, creator):
        # self.creator = creator
        pass

    def set_settings(self, settings):
        # self.__settings = settings
        pass
