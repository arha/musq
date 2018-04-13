from musq_modules import abstract
import logging
#!/usr/bin/env python
import time
import unicornhat as unicorn

class mm_unicorn(abstract.mm_abstract):
    def __init__(self):
        prefix="unicorn"
        unicorn.set_layout(unicorn.AUTO)
        unicorn.rotation(0)
        unicorn.brightness(1)
        width,height=unicorn.get_shape()

    def on_message_received(self, topic, trigger_topic, message, config_line):
        logging.debug("topic=" + topic)
        logging.debug("trigger_topic=" + trigger_topic)
        logging.debug("message=" + message.payload.decode('UTF-8'))
        logging.debug("config_line=" + config_line)
        
        topic_p=trigger_topic.split('/')
        if (len(topic_p) < 4):
            logging.debug("Invalid unicorn topic: " + trigger_topic)
        else:
            m=message.payload.decode('UTF-8')
            logging.debug("unicorn...")

            if (topic_p[len(topic_p)-1] == 'all'):
                if (m[0] == '#'):
                    r = int(m[1:3], 16)
                    g = int(m[3:5], 16)
                    b = int(m[5:7], 16)
                else:
                    (r,g,b) = m.split(' ')
                    r = int(r)
                    b = int(b)
                    g = int(g)
                if (r != None and b != None and g != None):
                    for x in range(0,8):
                        for y in range (0,8):
                            unicorn.set_pixel(x,y,r,g,b)
                unicorn.show()
            if (topic_p[len(topic_p)-1] == 'led'):
                (x,y,r,g,b) = m.split(' ')
                x = int(x)
                y = int(y)
                r = int(r)
                b = int(b)
                g = int(g)
                if (x!= None and y != None and r != None and b != None and g != None):
                    unicorn.set_pixel(x,y,r,g,b)
                    unicorn.show()

    def link(self, musq_instance, settings):
        super(mm_unicorn, self).link(musq_instance, settings)
        logging.debug("unicorn linked!")
