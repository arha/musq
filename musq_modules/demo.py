from musq_modules import abstract
import logging
import os,binascii

class mm_demo(abstract.mm_abstract):
    def __init__(self):
        prefix="demo"
        self.__id=binascii.b2a_hex(os.urandom(4))

    def call(self, topic, trigger_topic, message, config_line):
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)
        logging.debug("id = %s", self.__id)
        logging.debug("ip = %s", self.__settings['ip'])

    def link(self):
        logging.debug("demo (%s) linked!", self.__id)

    def set_creator(self, creator):
        self.creator = creator

    def set_settings(self, settings):
        self.__settings = settings
