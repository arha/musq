from musq_modules import abstract
import logging
from urllib.request import urlopen

class mm_http_request(abstract.mm_abstract):
    def __init__(self):
        prefix="http_request"

    def call(self, topic, trigger_topic, message, config_line):
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)
        logging.debug("id = %s", self.my_id)



        if (self.settings.get('url') != None):
            url = self.settings.get('url')
            if url[0:7] != "http://":
                url = "http://" + url
            f = urlopen( url )
            print ( f.read() )

    def link(self, creator, settings):
        super(  mm_http_request, self).link(creator, settings)