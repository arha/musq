from musq_modules import abstract
import logging
import httplib2
try:
    from urllib.parse import urlencode
except ImportError: # Python 2
    from urllib import urlencode


class mm_http_client(abstract.mm_abstract):
    def __init__(self):
        self.internal_name="http_client"

    def on_message_received(self, topic, trigger_topic, message, config_line):
        input_data = message.payload.decode("UTF-8")

        if self.settings.get('url') is not None:
            url = self.settings.get('url')
            if url[0:7] != "http://":
                url = "http://" + url
            # url = ("http://www.httpbin.org/anything")
            h = httplib2.Http()

            method = (self.settings.get('method') or 'POST').upper().strip()
            if method not in ('GET', 'POST', 'PUT', 'DELETE'):
                logging.warning("Invalid method %s supplied for module %s, defaulting to POST")
                method = "POST"
            data = {"value": input_data}
            data = urlencode(data)
            logging.info("Sending http request %s via %s" % (url, method))
            (resp_headers, result) = h.request(url, method, data)

            publish_result = self.settings.get('publish_result')
            if publish_result is not None and publish_result != trigger_topic:
                logging.info("Publishing result to %s" % publish_result)
                publish_qos = self.settings.get('publish_qos') or 0
                publish_retain = self.settings.get("publish_retain") or False
                self.musq_instance.raw_publish(self, result, publish_result, publish_qos, publish_retain)
            elif publish_result == trigger_topic:
                logging.error("will *NOT* publish result of request received on [%s] to [%s] - will cause a loopback" % (trigger_topic, publish_result))

    def link(self, musq_instance, settings):
        super(mm_http_client, self).link(musq_instance, settings)
