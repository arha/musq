#!/usr/bin/env python
from musq_modules import abstract
import logging
import time, threading
from time import sleep


from pyA20.gpio import gpio
from pyA20.gpio import port

class mm_opi_one(abstract.mm_abstract):


    def __init__(self):
        prefix="opi_one"
        self.last_send = 0
        gpio.init()
        gpio.setcfg(port.PG7, gpio.INPUT)
        gpio.pullup(port.PG7, gpio.PULLUP)
        gpio.setcfg(port.PG6, gpio.INPUT)
        gpio.pullup(port.PG6, gpio.PULLUP)
        self.__load_pinmap()

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
            "PXa":  port.POWER_LED,
            "PXb":  port.STATUS_LED
            }

    # /example/opi/... 
    # /example/opi/led/red ...
    def call(self, topic, trigger_topic, message, config_line): 
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)
        
        topic_p=trigger_topic.split('/')
        print(topic_p)
        if (len(topic_p) < 4):
            logging.debug("Invalid opi_one topic: " + trigger_topic)
        else:
            m=message.payload.decode('UTF-8')

            if (topic_p[3] == 'led'):
                if (topic_p[4] == 'red' or topic_p[4] == "green"):
                    if (m == "0" or m == "1"):
                        with open("/sys/class/leds/" + topic_p[4] + "_led/brightness", "w") as file:
                            file.write(m)
            if (topic_p[3] == 'gpio'):
                # /example/opi/gpio/read/PG7
                if (topic_p[4] == 'read' or topic_p[4] == 'pullup' or topic_p[4] == 'pulldown'
                    or topic_p[4] =='write' or topic_p[4] == 'output'):
                    pin = topic_p[5]
                    if (pin in self.pinmap):
                        if (topic_p[4] == 'pullup'):
                            logging.debug("Setting pullup pin %s", pin)
                            gpio.pullup(self.pinmap[pin], gpio.PULLUP)
                        if (topic_p[4] == 'output'):
                            logging.debug("Setting output pin %s=%s", pin, m)
                            pindir = gpio.INPUT
                            if (m == "1"):
                                pindir = gpio.OUTPUT
                            gpio.setcfg(self.pinmap[pin], pindir)
                        if (topic_p[4] == 'write'):
                            logging.debug("Write value %s to %s", m, pin)
                            logging.debug("Current dir: %s to %s", pin, gpio.getcfg(self.pinmap[pin]))
                            pinval = gpio.LOW
                            if (m == "1"):
                                pinval = gpio.HIGH
                            gpio.output(self.pinmap[pin], pinval)
                        if (topic_p[4] == 'read'):
                            data = gpio.input(self.pinmap[pin])
                            logging.debug("Reading pin %s = %s", pin, data)
                            message = {}
                            message['type']='pub'
                            message['topic']='/example/opi/gpio/pin/' + pin + '/value'
                            message['payload']=str(data).encode('UTF-8')
                            self.creator.bug(self, message)



    def link(self, creator, settings):
        super(  mm_opi_one, self).link(creator, settings)
        logging.debug("opi_one linked!")

    def set_creator(self, creator):
        self.creator = creator

    def main(self):
        # entry point for the thread
        while True:
            sleep (1)
            ts = time.time()
            if (ts - self.last_send > 120):
                logging.debug("opi_one thread: reading temperature")
                data = "-1" 
                # /sys/devices/virtual/thermal/thermal_zone{0,1}/temp
                with open("/etc/armbianmonitor/datasources/soctemp", "r") as file:
                    data=file.readline()
                message = {}
                message['type']='pub'
                message['topic']='/example/opi/temperature/soc'
                message['payload']=str(data).encode('UTF-8')
                self.creator.bug(self, message)
                self.last_send=ts
        logging.debug("Thread finished on thread_test")

    def run(self):
        logging.debug("thread start")
        t1 = threading.Thread(target=self.main)
        t1.start()

    def set_creator(self, creator):
        self.creator = creator
