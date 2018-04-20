#!/usr/bin/env python
from musq_modules import abstract
import logging
import time, threading, subprocess
from os.path import isfile, join
from time import sleep
from pyA20.gpio import gpio
from pyA20.gpio import port

class mm_opione(abstract.mm_abstract):
    def __init__(self):
        self.internal_name="opione"
        self.last_send = 0
        gpio.init()
        # gpio.setcfg(port.PG7, gpio.INPUT)
        # gpio.pullup(port.PG7, gpio.PULLUP)
        # gpio.setcfg(port.PG6, gpio.INPUT)
        # gpio.pullup(port.PG6, gpio.PULLUP)
        self.__load_pinmap()
        self.pintarget = "PA13"

    def __load_pinmap(self):
        self.pinmap={
            "PA1":  port.PA1, 
            "PA2":  port.PA2, 
            "PA3":  port.PA3, 
            "PA6":  port.PA6,
            "PA7":  port.PA7,
            "PA9":  port.PA9,
            "PA10": port.PA10,
            "PA11": port.PA11, 
            "PA12": port.PA12, 
            "PA13": port.PA13, 
            "PA14": port.PA14,
            "PA18": port.PA18,
            "PA19": port.PA19,
            "PA20": port.PA20,
            "PA21": port.PA21,
            "PC0":  port.PC0, 
            "PC1":  port.PC1, 
            "PC2":  port.PC2, 
            "PC3":  port.PC3,
            "PC4":  port.PC4,
            "PC7":  port.PC7,
            "PD14": port.PD14,
            "PG6":  port.PG6, 
            "PG7":  port.PG7,
            "PG8":  port.PG8,
            "PG9":  port.PG9,
            # "PL10":  port.PL10,         # power, green
            # "PA15":  port.PA15          # status, red
            }

    # /example/opi/... 
    # /example/opi/led/red ...
    def is_topic_relevant(self, trigger_topic):
        return True

    def split_topic(self, trigger_topic, topic):
        if self.autotopic != None and trigger_topic.startswith(self.autotopic):
            # print ("autotopic (%s) found matching message on topic (%s)" % (self.autotopic, trigger_topic))        
            subtopic = trigger_topic[ len(self.autotopic) : ]
            parts = subtopic.split("/")
            if (parts[0].strip() == ""):
                del (parts[0])
            return { "matching_topic": "autotopic", "parts": parts }
        elif topic != None and trigger_topic.startswith(topic):
            print ("config topic")
            return { "matching_topic": "config", "parts": None }

    def on_message_received(self, topic, trigger_topic, message, config_line):
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        # logging.debug("message=" + message.payload.decode('UTF-8'))
        # logging.debug("config_line=" + config_line)
        if self.is_topic_relevant(trigger_topic):
            t = self.split_topic(trigger_topic, topic)
            topic_mode = t['matching_topic']
            p = t['parts']
            m = message.payload.decode("UTF-8")

            if p[0].lower() == "gpio":
                if p[1].lower() == "target":
                    if self.pin_id(m) != None:
                        pin = self.clean_pin_name(m)
                        logging.debug("Setting target pin to %s" % pin)
                        self.pintarget = pin
                    else:
                        logging.debug("Invalid pin target: %s" % m)

                if p[1].lower() == 'write':
                    if (self.pintarget == None):
                        logging.debug("Cannot write, invalid pin targeted: %s. Write to %s a correct pin" % (self.pintarget, self.autotopic + "/gpio/target"))
                    else:
                        self.pin_write(self.pintarget, m)

                if p[1].upper() in self.pinmap:
                    # user is doing a direct write, without specifying a target
                    logging.debug("Fast GPIO %s: %s" % (p[1].upper(), m))
                    self.pin_write(p[1].upper(), m)
                
    def pin_id(self, pin_name):
        pin = pin_name.upper().strip()
        if pin[0:1] != "P":
            # try to find the pin anyway, if the user types just A0 instead of pa0
            pin = "P" + pin
        if pin in self.pinmap:
            return self.pinmap[pin]
        else:
            return None

    def clean_pin_name(self, pin_name):
        pin = self.pin_id(pin_name)
        for key, val in self.pinmap.items():
            if val == pin:
                return key
        return None

    def pin_write(self, pin_name, value):
        # verilog like: U, X, 0, 1, Z, W, L, H, -

        m = value.lower()
        pin = self.pin_id(pin_name)
        if (pin == None):
            logging.warning("Could not write, invalid pin name %s" % pin_name)

        if (m == 'h' or m == '1' or m == 'hi' or m == 'high' or m == 'on'):
            gpio.setcfg(pin, gpio.OUTPUT)
            gpio.output(pin, gpio.HIGH)
            logging.debug("Set pin %s to 1 (output, strong high)" % pin_name)
        if (m == 'l' or m == '0' or m == 'lo' or m == 'low' or m == 'off' or m == 'of'):
            gpio.setcfg(pin, gpio.OUTPUT)
            gpio.output(pin, gpio.LOW)
            logging.debug("Set pin %s to 0  (output, strong low)" % (pin_name))
        if (m == 'z' or m == 'tri' or m == 'in' or m == 'input'):
            # this should clear pullups and pulldowns
            gpio.setcfg(pin, gpio.INPUT)
            gpio.output(pin, gpio.LOW)
            gpio.pullup(pin, gpio.INPUT)
            logging.debug("Set pin %s to high z (input, no pullup, no pulldown)" % (pin_name))
        if (m == 'w0' or m == 'wlo' or m == 'z0'):
            gpio.setcfg(pin, gpio.INPUT)
            gpio.output(pin, gpio.LOW)
            gpio.pullup(pin, gpio.PULLDOWN)
            logging.debug("Set pin %s to weak low (input, pulldown)" % (pin_name))
        if (m == 'w1' or m == 'whi' or m == 'z1'):
            gpio.setcfg(pin, gpio.INPUT)
            gpio.output(pin, gpio.LOW)
            gpio.pullup(pin, gpio.PULLUP)
            logging.debug("Set pin %s to weak hi (input, pullup)" % (pin_name))

    def link(self, musq_instance, settings):
        super(mm_opione, self).link(musq_instance, settings)
        logging.debug("opione linked!")
        self.musq_instance.get_env_data()
        self.autotopic = "/musq/dev/" + self.musq_instance.musq_id
        return True

    def setup_autotopic(self):
        logging.debug("Setting up autotopic for %s (id=%s)" % (self.internal_name, self.my_id))
        messages = []

        e = self.musq_instance.get_env_data()
        messages.append( { 'message': self.musq_instance.formatted_time(), 'topic': 'time_init', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['serial'], 'topic': 'serial_number', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['hostname'], 'topic': 'hostname', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['uptime'], 'topic': 'uptime', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['cpu'], 'topic': 'cpu', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['hw'], 'topic': 'hardware', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['ip'], 'topic': 'ip', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['temp'], 'topic': 'temp', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['temp1'], 'topic': 'temp1', 'qos': 2, 'retained': True} )
        messages.append( { 'message': e['temp2'], 'topic': 'temp2', 'qos': 2, 'retained': True} )
        for m in messages:
            self.musq_instance.self_publish(self, m['message'], m['topic'], m['qos'], m['retained'])
    
    def delete_autotopic(self):
        topics = ['time_init', 'serial_number', 'hostname', 'uptime', 'cpu', 'hardware', 'ip', 'temp', 'temp1', 'temp2', 'gpio/target', 'gpio/write', 'gpio/read']
        # for key, val in self.pinmap.items():
        #    topics.append('GPIO/' + key)
        for m in topics:
            self.musq_instance.self_publish(self, '', m, qos=2, retain=True)
    
    def signal_exit(self):
        super(  mm_opione, self).signal_exit()
        logging.debug("removing autotopic")
        self.delete_autotopic()

    def main(self):
        # entry point for the thread
        self.setup_autotopic()
        while True:
            sleep (1)
            ts = time.time()
            if (ts - self.last_send > self.thread_sleep):
                logging.debug("opione thread: spin busy loop thread")
                data = "-1" 
                with open("/etc/armbianmonitor/datasources/soctemp", "r") as file:
                    data=file.readline()
                data = self.musq_instance.get_first_line("/etc/armbianmonitor/datasources/soctemp", strip=True)
                self.last_send=ts
                self.musq_instance.heartbeat()
                self.musq_instance.self_publish(self, data, 'temp', qos=2, retain=True)
        logging.debug("Thread finished on thread_test")

    def run(self):
        if (self.musq_instance == -1):
            logging.error("*** Error in %s (id=%s), object not linked, refusing thread start." % (self.internal_name, self.my_id))
            return

        self.thread_sleep = int(self.settings.get("thread_sleep")) or 10
        logging.debug("thread start with thread_sleep=%s (id=%s)" % (self.thread_sleep, self.my_id))
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    ## other misc stuff
