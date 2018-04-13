import os,binascii
import logging

class mm_abstract:
    internal_name = ""
    name = ""
    description = ""
    version = ""
    settings = {}
    my_id = "DEADBEEF"
    musq_instance = -1
    instance_name = ""

    def __init__(self):
        self.internal_name="abstract"
        logging.error("initted abstract musq module")

    def link(self, musq_instance, settings):
        self.my_id = self.get_id()
        self.musq_instance = musq_instance
        self.settings = settings
        # logger.debug("*** LINKING id=%s, object=%s, creator=%s, settings=%s" % (self.my_id, self, self.creator, self.settings))

    def get_id(self):
        my_id=( "%08X" % (id(self)))
        return my_id

    def signal_exit(self):
        logging.debug("Requesting graceful exit for %s id=%s" % (self.internal_name, self.my_id))
