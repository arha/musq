#!/usr/bin/python3 

import paho.mqtt.client as mqtt
import subprocess, os, yaml, shlex
from time import sleep
import pprint 


from glue_classes import input_glue_script, output_glue_pipe, output_glue
#testaa

class musq():
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # client.subscribe("/topic/arha/#", 2)
        self.mqtt_client.subscribe("/test/#", 0)
        self.mqtt_client.subscribe("test/#", 0)

    def on_message(self, client, userdatanp, msg):
        print("Received message on topic: " + msg.topic+" "+str(msg.payload))

        inputs = self.load_inputs()
        for key, i in inputs.items():
            i.execute(msg.topic, msg)


        if False:
            topics = self.get_topic_matches( msg.topic)
            if (topics != None):
                for key, value in topics.items():
                    print("TOPIC = " + key)
                    for call in value:
                        print("CALL = " + call)
                        parts = shlex.split(call)
                        # check for $, replace with message
                        for index, part in enumerate(parts):
                            if (part == '$'):
                                parts[index] = msg.payload.decode('UTF-8')
                        my_env = os.environ.copy()

                        # add per message environment vars
                        my_env["MUSQ_TOPIC_IN"] = msg.topic
                        my_env["MUSQ_SUB_TRIGGER"] = key
                        my_env["MUSQ_PAYLOAD"] = msg.payload
                        print("------ BEGIN SCRIPT EXEC -----")
                        subprocess.call(parts, env=my_env)
                        print("------- DONE SCRIPT EXEC -----")

    def on_glue_output_pub(self, glue_class, topic, payload):
        #print("Publish event from glue_class: " + glue_class.name + " to topic " + topic + " with pyload " + payload)
        self.mqtt_client.publish(topic, payload, 2)
        

    def load_inputs_simple(self):
        a = yaml.load(open("/home/arha/musq/input.conf"))
        return a

    def load_inputs(self):
        a = yaml.load(open("/home/arha/musq/input.conf"))
        a = a['inputs']

        inputs = {}
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(a)

        for key, i in a.items():
            if ('scripts' in i.keys()):
                glue_class = input_glue_script(key, i['topic'], i['scripts'])
                glue_class.set_creator(self)
                
                inputs[key] = glue_class;
        
        # pp.pprint(inputs)
        return inputs
        

    def load_pipes(self):
        a = yaml.load(open("/home/arha/musq/output.conf"))
        pipes = {}
        for key, output in a['outputs'].items():
            if (output['type'] == 'pipe'):
                pipes[key] = output
        return pipes

    def load_outputs(self):
        a = yaml.load(open("/home/arha/musq/output.conf"))
        pipes = {}

        for key, output in a['outputs'].items():
            if (output['type'] == 'pipe'):
                pipes[key] = output

        print("Load outputs: pipes")
        print (pipes)
        return a

    def get_topic_matches(self, check_topic):
        inputs = self.load_inputs()
        result = {}
        for key, value in inputs.items():
            if self.topic_matches_sub(key, check_topic):
                result[key] = value
        return result

    def topic_matches_sub(self, sub, topic):
        result = True
        multilevel_wildcard = False
        slen = len(sub)
        tlen = len(topic)
        if slen > 0 and tlen > 0:
            if (sub[0] == '$' and topic[0] != '$') or (topic[0] == '$' and sub[0] != '$'):
                return False

        spos = 0
        tpos = 0
        while spos < slen and tpos < tlen:
            if sub[spos] == topic[tpos]:
                if tpos == tlen-1:
                    # Check for e.g. foo matching foo/#
                    if spos == slen-3 and sub[spos+1] == '/' and sub[spos+2] == '#':
                        result = True
                        multilevel_wildcard = True
                        break

                spos += 1
                tpos += 1

                if tpos == tlen and spos == slen-1 and sub[spos] == '+':
                    spos += 1
                    result = True
                    break
            else:
                if sub[spos] == '+':
                    spos += 1
                    while tpos < tlen and topic[tpos] != '/':
                        tpos += 1
                    if tpos == tlen and spos == slen:
                        result = True
                        break

                elif sub[spos] == '#':
                    multilevel_wildcard = True
                    if spos+1 != slen:
                        result = False
                        break
                    else:
                        result = True
                        break
                else:
                    result = False
                    break

        if not multilevel_wildcard and (tpos < tlen or spos < slen):
            result = False

        return result
            
    def main(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("localhost", 1883, 12)
        self.mqtt_client.loop_start()
        pipes_data = self.load_pipes()

        glue = {}
        for key, p in pipes_data.items():
            glue_class = output_glue_pipe(key, p['path'], p['topics'])
            glue_class.open()
            glue_class.set_creator(self)
            glue[key] = glue_class

        print(glue)
        while True:
            sleep(0.1)
            for key, g in glue.items():
                g.loop()
            
        print("-")

m = musq()
m.main()
        

