from musq_modules import abstract
import time
import logging
import threading
from time import sleep
import http.server
import socketserver

class mm_http_server(abstract.mm_abstract):
    def __init__(self):
        self.prefix="http_server"
        self.last_send=time.time()
        self.last_send=0

    def call(self, topic, trigger_topic, message, config_line): 
        return
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)

    def link(self, creator, settings):
        super(  mm_http_server, self).link(creator, settings)
        logging.debug("http_server linked!")

    def main(self):
        PORT = int(self.settings.get("port")) or 8000
        handler = MusqHTTPRequestHandler
        #handler = self.musq_handler_factory()
        with http.server.HTTPServer(("", PORT), handler) as httpd:
            httpd.parent = self
            logging.info("Starting musq HTTP server on 0.0.0.0:%d", PORT)
            httpd.serve_forever()
        logging.debug("Thread finished on thread_test")
        return


    def route(self, path, headers, client_address):
        logging.info("HTTP requestline: %s" % path)

    def run(self):
        logging.debug("thread start for http_server")
        t1 = threading.Thread(target=self.main)
        t1.start()

    def set_creator(self, creator):
        self.creator = creator

class MusqHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    parent = None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        self.server.parent.route(self.path, self.headers, self.client_address)
        logging.info(self.requestline)
        self.wfile.write("<html><body><h1>hi!</h1></body></html>".encode("UTF-8"))

    def do_POST(self):
        self._set_headers()
        self.server.parent.route(self.path, self.headers, self.client_address)
        self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode("UTF-8"))

    def do_PUT(self):
        self._set_headers()
        self.server.parent.route(self.path, self.headers, self.client_address)
        self.wfile.write("<html><body><h1>PUT!!</h1></body></html>".encode("UTF-8"))

    def do_DELETE(self):
        self._set_headers()
        self.server.parent.route(self.path, self.headers, self.client_address)
        self.wfile.write("<html><body><h1>DELETE!!</h1></body></html>".encode("UTF-8"))
