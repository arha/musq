import logging
from musq_modules import abstract
## TODO WARNING LOOPBACK PROTECTION


class mm_copy(abstract.mm_abstract):
    internal_name = ""
    name = ""
    description = ""
    version = ""
    settings = {}
    my_id = ""
    musq_instance = -1
    instance_name = ""
    topic = None
    thread = None
    kill_thread = False

    def __init__(self):
        self.internal_name = "copy"

    def link(self, musq_instance, settings):
        self.my_id = self.get_id()
        self.musq_instance = musq_instance
        self.settings = settings

    def on_message_received(self, topic, trigger_topic, message, config_line):
        destination_topic = self.settings.get("output")
        if destination_topic is None:
            logging.warning("Copy %s received message on %s but has no destination, add an \"output\" field in config" % (self.instance_name, trigger_topic))
        overwrite_message = self.settings.get("message")
        if overwrite_message is not None:
            message = overwrite_message
        else:
            message = message.payload.decode('UTF-8')

        self.musq_instance.raw_publish(self, message, destination_topic)