import os, shlex
import subprocess, os, yaml, shlex

class output_glue:
    name = ""
    __type = ""
    creator = None

    def set_creator(self, creator):
        self.creator = creator

class output_glue_pipe(output_glue):
    path = ""
    create = True
    topics = []
    __pipe = None
    publish_event = None

    def __init__(self, name, path, topics, create=True):
        self.name = name
        self.__type = "pipe"
        self.path = path
        self.topics = topics

    def open(self):
        print("glue pipe opening " + self.path)
        self.__pipe = os.fdopen(os.open(self.path, os.O_RDONLY|os.O_NONBLOCK))
        print("glue pipe " + self.name + " init done")


    def loop(self):
        if (self.__pipe != None):
            data = (self.__pipe.read())
            if (data != ""):
                self.creator.on_glue_output_pub(self, self.topics[0], data)

class input_glue:
    name = ""
    topic = ""
    scripts = []
    __type = ""
    creator = None

    def __init__():
        pass

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

class input_glue_script(input_glue):
    def __init__ (self, name, topic, scripts):
        self.name=name
        self.topic=topic
        self.scripts=scripts
        self.__type="script"

    def set_creator(self, creator):
        self.creator = creator
    
    def execute(self, topic_received, msg):
        if (self.topic != None and self.topic_matches_sub(self.topic, topic_received)):
            for call in self.scripts:
                print("CALL = " + call)
                parts = shlex.split(call)
                # check for $, replace with message
                for index, part in enumerate(parts):
                    if (part == '$'):
                        parts[index] = msg.payload.decode('UTF-8')
                my_env = os.environ.copy()

                # add per message environment vars
                my_env["MUSQ_TOPIC_IN"] = msg.topic
                my_env["MUSQ_SUB_TRIGGER"] = self.topic
                my_env["MUSQ_PAYLOAD"] = msg.payload
                print("------ BEGIN GLUE SCRIPT EXEC -----")
                subprocess.call(parts, env=my_env)
                print("------- DONE GLUE SCRIPT EXEC -----")
