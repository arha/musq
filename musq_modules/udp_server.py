from musq_modules import abstract
import time
import logging
import threading
import socketserver

class mm_udp_server(abstract.mm_abstract):
    """ a udp server to allow UDP datagrams to be published to mqtt. can be instanced multiple times, as per the config
    file this allows multiple topics to be subscribed to multiple ports.

    why use a UDP server as an IOT device endpoint?
    1. power savings: local networks are reliable anyway. skipping on SYN/ACK and protocol based pub/sub (think MQTT
    on ESP8266/nodemcu, yields in less packets transmitted and less modem uptime.

    2. some devices, like the ethernet igor plug or the ethertiny transmit using only the TX pair of a hacked ethernet
    cable, with a very cheap and tiny mcu like t2313 or t85. This used to be a popular method, along with PoE to make
    cheap sensors connected to the ethernet. There is no RX present and they keep broadcasting (flooding) the network
    with UDP packets. It's shitty, but it works. and it's incredibly cheap.
    (https://web.archive.org/web/20140326211127/http://cesko.host.sk/IgorPlugUDP/IgorPlug-UDP%20(AVR)_eng.htm)
    https://hackaday.com/2014/08/29/bit-banging-ethernet-on-an-attiny85/ and  https://github.com/cnlohr/ethertiny
    https://www.youtube.com/watch?v=mwcvElQS-hM&feature=youtu.be

    3. CoAP and MQTT-SN are still a mess:
    https://stackoverflow.com/questions/27560549/when-mqtt-sn-should-be-used-how-is-it-different-from-mqtt
    """
    def __init__(self):
        self.internal_name="udp_server"
        self.last_send=time.time()
        self.last_send=0
        self.qos = 0
        self.retain = False
        self.topic = None

    def on_message_received(self, topic, trigger_topic, message):
        logging.warning(topic, trigger_topic, message, "aaa")
        return

    def link(self, musq_instance, settings):
        super(mm_udp_server, self).link(musq_instance, settings)
        logging.debug("udp_server linked!")
        return True

    def main(self):
        self.port = int(self.settings.get("port"))
        if self.port is None:
            logging.warning("No listening port configured, will default to 7070 but a second udp server will be unable to use 7070")
            self.port = 7070
        if not self.settings.get("ip"):
            logging.warning("No listening IP configured for udp server, defaulting to 0.0.0.0")
            ip = "0.0.0.0"
        else:
            ip = self.settings.get("ip")
        handler = MusqUDPHandler
        self.topic = self.settings.get("topic")
        self.qos = self.settings.get("qos") or 0
        self.retain = self.settings.get("retain") or False

        if self.qos != 0 and self.qos != 1 and self.qos != 2:
            self.qos = 0
            logging.warning("Invalid value QOS=%s for UDP server, defaulting to 0" % self.qos)

        if self.retain != True and self.retain != False:
            self.retain = False

        if not self.topic:
            logging.warning("No UDP topic configured, will default to /musq/%s/udp/%s" % ( self.musq_instance.musq_id, self.get_id()  ) )
            self.topic = ["/musq/%s/udp/%s" %  ( self.musq_instance.musq_id, self.get_id())]

        with socketserver.UDPServer(("", self.port), handler) as udpd:
            udpd.parent = self
            logging.info("Starting musq UDP server on 0.0.0.0:%d", self.port)
            udpd.serve_forever()
        logging.debug("Thread finished on UDP server")
        return

    def process_message(self, handler):
        ip = handler.client_address[0]
        datagram = handler.rfile.readline().strip()
        logging.debug("Received UDP message, ip=%s: %s" % (ip, datagram))

        self.musq_instance.raw_publish(self, datagram, self.topic, self.qos, self.retain)

    def run(self):
        logging.debug("thread start for udp_server")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def signal_exit(self):
        super(mm_udp_server, self).signal_exit()
        self.httpd.shutdown()


class MusqUDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        self.server.parent.process_message(self)
        # self.wfile.write("Hello UDP Client! I received a message from you!".encode())

    def log_message(self, format, *args):
        return
