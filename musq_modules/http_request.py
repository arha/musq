from musq_modules import abstract
import logging
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError: # Python 2
    from urllib import urlencode
    from urllib2 import urlopen

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
            logging.info("Sending http request %s" % url)
            f = urlopen( url )
            result = ( f.read() )
            print ( result )

            publish_result = self.settings.get('publish_result')
            if publish_result != None and publish_result != trigger_topic:
                logging.info("Publishing result to %s" % publish_result)
                publish_qos = self.settings.get('publish_qos') or "0"
                publish_retain = self.settings.get("publish_retain") or False
                self.creator.raw_publish(self, result, publish_result, publish_qos, publish_retain )

    def link(self, creator, settings):
        super(  mm_http_request, self).link(creator, settings)