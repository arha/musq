from musq_modules import abstract
import logging
import subprocess
import os
import traceback
import time
import threading

class  mm_script_out(abstract.mm_abstract):
    """ handles scripts inside an environment. this is the default way to interact with hardware that
    has no musq modules available yet. If you can get the hardware to output its data to stdout, or you can
    pass its data from a script, after reading some env variables ($MUSQ_MESSAGE, $MUSQ_TOPIC_IN) just
    hookup your script to the script_out module and it's now mqtt aware.

     Modes of operation
     MQTT topic in -> script (write only. run the script when a mqtt message is received)
     MQTT topic in -> script -> MQTT topic out (write and send feedback to another topic)
     timed script -> MQTT topic out (run a script every x seconds, send the output to a mqtt topic)
    """
    def __init__(self):
        self.internal_name = "script_out"
        self.scripts = []
        self.last_send = 0

    def on_message_received(self, topic, trigger_topic, message):
        msg = message.payload.decode('UTF-8')
        command = self.settings.get("script")
        command = command.replace('$value', msg)
        command = command.replace('$topic', message.topic)
        my_env = os.environ.copy()
        my_env["MUSQ_TOPIC_IN"] = message.topic
        my_env["MUSQ_MESSAGE"] = msg
        my_env["MUSQ_TRIGGER"] = "on_message"
        my_env["MUSQ_INSTANCE_NAME"] = self.instance_name
        logging.debug("%s (%s) executing script: %s" % (self.instance_name, self.internal_name, command))
        try:
            proc = subprocess.Popen(command, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            logging.debug("Process finished, exit code = %s" % exitcode)
            logging.debug("Output = %s" % out)
            self.send_result(out.decode("UTF-8"), exitcode)
        except:
            traceback.print_exc()


    def link(self, musq_instance, settings):
        super(mm_script_out, self).link(musq_instance, settings)
        logging.debug("script_out (%s) linked!", self.my_id)
        self.scripts = self.settings.get("script")
        if self.scripts is None:
            return False
        return True

    def main(self):
        repeat = self.settings.get("repeat")
        while True and not self.kill_thread:
            time.sleep(0.1)
            ts = time.time()
            if ts - self.last_send > repeat:
                self.last_send = time.time()
                command = self.settings.get("script")
                my_env = os.environ.copy()
                my_env["MUSQ_TRIGGER"] = "timed"
                my_env["MUSQ_INSTANCE_NAME"] = self.instance_name
                logging.debug("%s (%s) executing script: %s" % (self.instance_name, self.internal_name, command))
                try:
                    # subprocess.call(command, env=my_env, shell=True)
                    proc = subprocess.Popen(command, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = proc.communicate()
                    exitcode = proc.returncode
                    logging.debug("Process finished, exit code = %s" % exitcode)
                    logging.debug("Output = %s" % out)
                    self.send_result(out.decode("UTF-8"), exitcode)
                except:
                    traceback.print_exc()
        logging.debug("Thread finished on script_out")

    def run(self):
        if self.settings.get("repeat") is None or self.settings.get("repeat") == 0 or self.settings.get("repeat") == "0":
            logging.debug("Auto-repeat set to none; script will only be invoked from mqtt")
            return
        logging.debug("thread start for script_out")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def send_result(self, out, exitcode):
        if self.settings.get("topic_out") is not None:
            t = self.settings.get("topic_out")
            self.musq_instance.raw_publish(self, out, t)
        if self.settings.get("topic_out_exitcode") is not None:
            t = self.settings.get("topic_out_exitcode")
            self.musq_instance.raw_publish(self, exitcode, t)
