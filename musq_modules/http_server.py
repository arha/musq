from musq_modules import abstract
import time
import logging
import threading
import http.server
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import parse_qs

class mm_http_server(abstract.mm_abstract):
    def __init__(self):
        self.internal_name = "http_server"
        self.last_send = time.time()
        self.last_send = 0
        self.httpd = None
        self.routes = {}

        logging.getLogger("urllib").setLevel(logging.CRITICAL)
        logging.getLogger("urllib2").setLevel(logging.CRITICAL)
        logging.getLogger("requests").setLevel(logging.CRITICAL)
        logging.getLogger("http").setLevel(logging.CRITICAL)

    def configure_routes(self):
        if self.settings.get('routes') is None:
            if self.settings.get('url') is None:
                logging.warning("No url defined for http server")
                # todo - maybe configure default everything for this instance to publish to topic
                return
            if self.settings.get('topic') is None:
                logging.warning("No topic defined for http server, nothing will be published to MQTT")
                return
        if self.settings.get('url') is not None and self.settings.get('topic') is not None:
            self.routes[self.settings.get('url').strip()] = {"topic": self.settings.get("topic").strip()}

        if self.settings.get('routes') is not None:
            for route_record in (self.settings.get('routes')):
                route_dict = {}
                for route, data in route_record.items():
                    route_dict["topic"] = data.get("topic").strip()
                    self.routes[route] = route_dict

    def on_message_received(self, topic, trigger_topic, message):
        return
        logging.warning("***")
        logging.warning("*** http_server does not accept mqtt messages. ")
        logging.warning("*** http_server accepts incoming http requests and sends mqtt messages")
        logging.warning("*** if you want an mqtt message to trigger a HTTP request, use the http_client module")
        logging.warning("***")

    def link(self, musq_instance, settings):
        super(mm_http_server, self).link(musq_instance, settings)
        self.configure_routes()
        logging.debug("http_server linked!")
        return True

    def main(self):
        port = int(self.settings.get("port")) or 8000
        handler = MusqHTTPRequestHandler
        # eugh, can't use "with" unless running python 3.6
        # https://stackoverflow.com/questions/46396575/cannot-run-python3-httpserver-on-arm-processoru
        self.httpd = http.server.HTTPServer(("", port), handler)
        self.httpd.parent = self
        if self.settings.get("certificate") is not None:
            cert = self.settings.get("certificate")
            import ssl
            certkey = None
            if self.settings.get("keyfile") is not None:
                certkey = self.settings.get("keyfile")
            self.httpd.socket = ssl.wrap_socket(self.httpd.socket, certfile=cert, keyfile=certkey, server_side=True)
            logging.info("HTTPS configured succesfully")
        logging.info("Starting musq HTTP server on 0.0.0.0:%d", port)
        self.httpd.musq_instance = self.musq_instance
        self.httpd.serve_forever()
        logging.debug("Thread finished on HTTP server")
        return

    def perform_route(self, handler):
        path = handler.path
        method = handler.command
        headers = handler.headers
        ip = handler.client_address

        logging.info("HTTP request: %s:%s - %s %s " % (ip[0], ip[1], method, path))
        query_str = urlparse(path).query
        query_path = urlparse(path).path
        if query_path in self.routes:
            route = self.routes.get(query_path)
            message = "1"

            if method == "POST" or method == "PUT" or method == "DELETE":
                var_len = int(handler.headers['Content-Length'])
                post_vars = handler.rfile.read(var_len)
                post_data = urlparse.parse.parse_qs(post_vars)
                if post_data.get(b"value") is not None:
                    message = (post_data.get(b"value")[0]).decode("UTF-8")
                else:
                    logging.warning("HTTP server %s: POST variable 'value' is expected." % self.instance_name)
            elif method == "GET":
                get_vars = parse_qs(query_str)
                print(get_vars)
                if get_vars.get("value") is not None:
                    message = (get_vars.get("value")[0])

            topic = route.get("topic")
            if topic is not None:
                qos = 2
                retain = False
                self.musq_instance.raw_publish(self, message, topic, qos, retain)
                # todo return code, improve checking based on methods
                response = "<pre>ok\r\n" + method + "\r\n\r\n" + str(headers) + "\r\n"

                handler.wfile.write(response.encode("UTF-8"))
                return 200
            else:
                logging.warning("HTTP server received call for route [%s], but points to invalid topic.")
        else:
            return 404

    def run(self):
        logging.debug("thread start for http_server")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def signal_exit(self):
        super(mm_http_server, self).signal_exit()
        self.httpd.shutdown()


class MusqHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # TODO there's some connection close/hanging issue, ie: request from firefox, request from curl, for some reason it hangs
    # now do ^C, request from firefox again and I get, on windows
    # ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine
    # no idea what triggers this, yet

    parent = None
    protocol_version = "HTTP/1.0"

    def _set_headers(self):
        server_version = "musq/" + self.server.musq_instance.__version__
        self.server_version = server_version
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        #self.send_header('Connection', 'close')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        result = self.server.parent.perform_route(self)

    def do_POST(self):
        self._set_headers()
        result =  self.server.parent.perform_route(self)

    def do_PUT(self):
        self._set_headers()
        result = self.server.parent.perform_route(self)

    def do_DELETE(self):
        self._set_headers()
        result = self.server.parent.perform_route(self)
        self.done_processing(result)

    def done_processing(self, result):
        print("HTTP connection closing...")
        self.finish()
        self.close_connection()
        print("HTTP connection closed")

    def log_message(self, format, *args):
        return
