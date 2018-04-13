from musq_modules import abstract
import time
import logging
import threading
import datetime
from time import sleep

class mm_log_file(abstract.mm_abstract):
    def __init__(self):
        self.internal_name="log_file"
        self.last_send=time.time()
        self.last_send=0

        self.__sp = ""
        self.file_ptr = None

    def on_message_received(self, topic, trigger_topic, message, config_line):
        m=message.payload.decode('UTF-8')
        if (self.file_ptr != None):
            log_str = ("%s, topic [%s]: %s\n" % (self.musq_instance.formatted_time(), trigger_topic, m))

            target_file = self.settings.get("filename")
            self.file_ptr = open(target_file, 'ba+')
            self.file_ptr.write(bytes(log_str, "UTF-8"))
            self.file_ptr.close()

            logging.debug("log_file output: " + log_str)
        return

    def link(self, musq_instance, settings):
        super(mm_log_file, self).link(musq_instance, settings)
        logging.debug("*** log_file linked!")

        target_file = self.settings.get("filename")
        logging.debug("target file " + target_file)
        self.file_ptr = open(target_file, 'ba+')
        #self.file_ptr.write(bytes("init\n", "UTF-8"))
        #self.file_ptr.write(bytes("init\n", "UTF-8"))


        return True

    def main(self):
        # doesn't need threading
        pass
