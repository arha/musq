from musq_modules import abstract
import time
import logging
import threading
from time import sleep
import http.server
import socketserver

class mm_http_server(abstract.mm_abstract):
    def __init__(self):
        self.internal_name="http_server"
        self.last_send=time.time()
        self.last_send=0

        logging.getLogger("urllib").setLevel(logging.CRITICAL)
        logging.getLogger("urllib2").setLevel(logging.CRITICAL)
        logging.getLogger("requests").setLevel(logging.CRITICAL)
        logging.getLogger("http").setLevel(logging.CRITICAL)

    def configure_routes(self):
        self.routes = {}
        if (self.settings.get('routes') == None):
            if self.settings.get('url') == None:
                logging.warning("No url defined for http server")
                # todo - maybe configure default everything for this instance to publish to topic
                return
            if self.settings.get('topic') == None:
                logging.warning("No topic defined for http server, nothing will be published to MQTT")
                return
        if self.settings.get('url') != None and self.settings.get('topic') != None:
            self.routes[self.settings.get('url').strip()] = { "topic": self.settings.get("topic").strip() }

        if (self.settings.get('routes') != None):
            for route_record in (self.settings.get('routes')):
                route_dict={}
                for route, data in route_record.items():
                    route_dict["topic"] = data.get("topic").strip()
                    self.routes[route] = route_dict

    def on_message_received(self, topic, trigger_topic, message, config_line):
        return
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)

    def link(self, musq_instance, settings):
        super(mm_http_server, self).link(musq_instance, settings)
        self.configure_routes()
        logging.debug("http_server linked!")

    def main(self):
        PORT = int(self.settings.get("port")) or 8000
        handler = MusqHTTPRequestHandler
        # eugh, can't use with unless running python 3.6 
        # https://stackoverflow.com/questions/46396575/cannot-run-python3-httpserver-on-arm-processoru

        httpd = http.server.HTTPServer(("", PORT), handler)
        httpd.parent = self
        logging.info("Starting musq HTTP server on 0.0.0.0:%d", PORT)
        httpd.serve_forever()
        logging.debug("Thread finished on thread_test")
        return

    def perform_route(self, handler):
        path = handler.path
        method = handler.command
        headers = handler.headers
        ip = handler.client_address

        logging.error("HTTP request: %s:%s - %s %s " % ( ip[0], ip[1], method, path ))

        if path in self.routes:
            route = self.routes.get(path)
            result = "139"
            topic = route.get("topic")
            if topic != None:
                qos = 2
                retain = False
                self.musq_instance.raw_publish(self, result, topic, qos, retain )
                # todo return code, improve checking based on methods
                return 200
            else:
                logging.warning("HTTP server received call for route [%s], but points to invalid topic.")
        else:
            return 404

    def run(self):
        logging.debug("thread start for http_server")
        t1 = threading.Thread(target=self.main)
        t1.start()

class MusqHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "musq/0.1"
    parent = None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        self.server.parent.perform_route(self)
        self.wfile.write("<html><body><h1>ok.</h1></body></html>".encode("UTF-8"))

    def do_POST(self):
        self._set_headers()
        self.server.parent.perform_route(self.path, self.headers, self.client_address)
        self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode("UTF-8"))

    def do_PUT(self):
        self._set_headers()
        self.server.parent.perform_route(self.path, self.headers, self.client_address)
        self.wfile.write("<html><body><h1>PUT!!</h1></body></html>".encode("UTF-8"))

    def do_DELETE(self):
        self._set_headers()
        self.server.parent.perform_route(self.path, self.headers, self.client_address)
        self.wfile.write("<html><body><h1>DELETE!!</h1></body></html>".encode("UTF-8"))

    def log_message(self, format, *args):
        return
