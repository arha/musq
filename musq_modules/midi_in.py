from collections import namedtuple
import pygame
import pygame.midi
import time
import logging
import threading
from enum import Enum
from musq_modules import abstract
from time import sleep

MidiInRoute = namedtuple("MidiInRoute", 'midi_command channel note min_velocity max_velocity cc channel_matrix')

class midi_command(Enum):
    note_off = 0x80
    note_on = 0x90
    aftertouch = 0xA0
    controller = 0xB0
    patch_change = 0xC0
    channel_pressure = 0xD0
    pitch_bend = 0xE0
    system = 0xF0

class mm_midi_in(abstract.mm_abstract):
    midi_interface = None
    routes = []

    def __init__(self):
        self.internal_name="midi_in"

    def on_message_received(self, topic, trigger_topic, message, config_line):
        pass

    def load_routes(self):
        routes = self.settings.get("routes")
        if routes is None:
            logging.warning("midi in (%s) has no routes configured" % self.instance_name)
            return False
        for route_data in routes:
            route = self.create_route(route_data)
            if route is not None:
                self.routes.append(route)

    def create_route(self, route_data):
        topic = list(route_data.keys())[0]
        settings = route_data.get(topic)

        if settings.get("command") is None:
            logging.warning("Midi_in (%s), route [%s] has no midi command assigned. This route will not work unless you add a \"command\" parameter"
                % (self.instance_name, topic) )
            return None
        command = settings.get("command")

        r = {"topic": topic}
        if command == "note_on":
            r["midi_command"] = midi_command.note_on
            note = settings.get("note")
            if note is None:
                logging.warning("midi in %s, route %s: no note configured. Add a note." % (self.instance_name, topic))
                return None
            r["note"] = note
            r["min_velocity"] = settings.get("min_velocity") or 0
            r["max_velocity"] = settings.get("max_velocity") or 127
            r["channel"] = settings.get("channel") or 0
            message = settings.get("message") or ""
            r["message"] = message
            return r

        elif command == "note_off":
            r["midi_command"] = midi_command.note_off
            note = settings.get("note")
            if note is None:
                logging.warning("midi in %s, route %s: no note configured. Add a note." % (self.instance_name, topic))
                return None
            r["note"] = note
            r["min_velocity"] = settings.get("min_velocity") or 0
            r["max_velocity"] = settings.get("max_velocity") or 127
            r["channel"] = settings.get("channel") or 0
            message = settings.get("message") or ""
            r["message"] = message
            return r

        elif command == "cc":
            r["midi_command"] = midi_command.controller
            cc = settings.get("cc")
            if cc is None:
                logging.warning("midi in %s, route %s: no cc configured. Add a cc." % (self.instance_name, topic))
                return None
            r["cc"] = cc
            r["min_data"] = settings.get("min_data") or 0
            r["max_data"] = settings.get("max_data") or 127
            r["channel"] = settings.get("channel") or 0
            message = settings.get("message") or ""
            r["message"] = message
            return r

    def match_routes_for_midi_input(self, midi_command, channel, note=0, cc=0, velocity=0):
        result = []
        for route in self.routes:
            if route["midi_command"] != midi_command:
                continue
            if route["midi_command"] == midi_command.controller:
                route_cc = route["cc"]
                min_data = route["min_data"]
                max_data = route["max_data"]
                route_channel = route.get("channel")
                if route_channel != channel:
                    continue
                if velocity < min_data:
                    continue
                if velocity > max_data:
                    continue
                if route_cc != cc:
                    continue
                result.append(route)
            elif route["midi_command"] == midi_command.note_on:
                # todo add C1 D#3 note parsing over midi note numbers
                # todo: match on more than single note: note range, advanced note range (C3-F3, E6, F#7) and a binary notemap
                route_note = route["note"]
                min_velocity = route["min_velocity"]
                max_velocity = route["max_velocity"]
                route_channel = route.get("channel")
                if channel != route_channel:
                    continue
                if note != route_note:
                    continue
                if velocity < min_velocity:
                    continue
                if velocity > max_velocity:
                    continue
                result.append(route)
            elif route["midi_command"] == midi_command.note_off:
                # todo same as note_on
                route_note = route["note"]
                min_velocity = route["min_velocity"]
                max_velocity = route["max_velocity"]
                route_channel = route.get("channel")
                if channel != route_channel:
                    continue
                if note != route_note:
                    continue
                if velocity < min_velocity:
                    continue
                if velocity > max_velocity:
                    continue
                result.append(route)
        return result

    def run(self):
        logging.debug("midi_in start")
        self.thread = threading.Thread(target=self.main)
        self.thread.start()

    def main(self):
        vice_id = self.settings.get("device") or 0
        vice_name = ""
        logging.debug("Initializing midi device %s (%s)" % (vice_id, vice_name))
        self.midi_interface = midi_interface()
        self.midi_interface.device_select(vice_id)

        self.midi_interface.callback_note_on = self._on_note_on
        self.midi_interface.callback_note_off = self._on_note_off
        self.midi_interface.callback_cc = self._on_cc

        while True and not self.kill_thread:
            new_data = self.midi_interface.process_input()
            if not new_data:
                sleep(0.01)
                continue
            # at this point callbacks should have fired
        logging.debug("Thread finished on thread_test")
        self.midi_interface.exit()

    def link(self, musq_instance, settings):
        super(mm_midi_in, self).link(musq_instance, settings)
        logging.debug("midi_in (%s) linked!", self.my_id)
        if not self.load_routes():
            return False

    def signal_exit(self):
        super(mm_midi_in, self).signal_exit()

    def _on_note_on(self, timestamp, note, channel, velocity):
        #logging.debug("midi in note on: ts=%s, note=%s, channel=%s, velocity=%s " % (timestamp, note, channel, velocity))
        routes = self.match_routes_for_midi_input(midi_command.note_on, channel, note=note-4, velocity=velocity)
        if routes:
            self.publish_note_onoff(routes, note, channel, velocity)

    def _on_note_off(self, timestamp, note, channel, velocity):
        #logging.debug("midi in note off change: ts=%s, note=%s, channel=%s, velocity=%s " % (timestamp, note, channel, velocity))
        routes = self.match_routes_for_midi_input(midi_command.note_off, channel, note=note-4, velocity=velocity)
        if routes:
            self.publish_note_onoff(routes, note, channel, velocity)

    def _on_cc(self, timestamp, cc, channel, data):
        #logging.debug("midi in cc change: ts=%s, cc=%s, channel=%s, velocity=%s " % (timestamp, cc, channel, velocity))
        routes = self.match_routes_for_midi_input(midi_command.controller, channel, cc=cc, velocity=data)
        if routes:
            self.publish_cc(routes, cc, channel, data)

    def publish_cc(self, routes, cc, channel, data):
        for route in routes:
            topic = route["topic"]
            message = str(route["message"])
            message = message.replace("$value", str(data))
            message = message.replace("$channel", str(channel))
            message = message.replace("$cc", str(cc))
            topic = topic.replace("$value", str(data))
            topic = topic.replace("$channel", str(channel))
            topic = topic.replace("$cc", str(cc))
            self.musq_instance.raw_publish(self, message, topic)

    def publish_note_onoff(self, routes, note, channel, velocity):
        for route in routes:
            topic = route["topic"]
            message = str(route["message"])
            message = message.replace("$velocity", str(velocity))
            message = message.replace("$channel", str(channel))
            message = message.replace("$note", str(note))
            topic = topic.replace("$velocity", str(velocity))
            topic = topic.replace("$channel", str(channel))
            topic = topic.replace("$note", str(note))
            self.musq_instance.raw_publish(self, message, topic)

class midi_interface:
    midi_input = None
    callback_note_on = None
    callback_note_off = None
    callback_cc = None

    def __init__(self):
        pygame.init()
        pygame.midi.init()
        self.callback_note_on = self.dummy_note_on
        self.callback_note_off = self.dummy_note_off
        self.callback_note_cc = self.dummy_cc

    def exit(self):
        pygame.midi.quit()

    def device_list(self):
        num = pygame.midi.get_count()
        for i in range(num):
            (interface, name, m_input, m_output, opened) = pygame.midi.get_device_info(i)
            direction = ""
            if m_input:
                direction = "IN  "
            elif m_output:
                direction = "OUT "
            print("%s %s" % (direction, name))

    def device_select(self, device_id):
        self.midi_input = pygame.midi.Input(device_id, 4)

    def process_input(self):
        if not self.midi_input.poll():
            return False

        midi_in_raw = self.midi_input.read(1)
        #print(midi_in_raw)
        for data in midi_in_raw:
            bytes = data[0]
            timestamp = data[1]
            command = bytes[0] & 0xF0
            channel = bytes[0] & 0x0F
            if command == midi_command.controller.value:
                controller = bytes[1]
                velocity = bytes[2]
                self.callback_cc(timestamp, controller, channel, velocity)
            elif command == midi_command.note_on.value:
                note = bytes[1]
                velocity = bytes[2]
                if velocity > 0:
                    self.callback_note_on(timestamp, note, channel, velocity)
                else:
                    self.callback_note_off(timestamp, note, channel, 0)
            elif command == midi_command.note_off.value:
                note = bytes[1]
                velocity = bytes[2]
                self.callback_note_off(timestamp, note, channel, velocity)
        return True

    def dummy_note_on(self, timestamp, note, channel, velocity):
        pass

    def dummy_note_off(self, timestamp, note, channel, velocity):
        pass

    def dummy_cc(self, timestamp, cc, channel, velocity):
        pass

    def read_loop(self):
        cont = True
        while cont:
            if not self.midi_input.poll():
                time.sleep(0.01)
                continue

            midi_events_raw = self.midi_input.read(4)
            #print (midi_events_raw)
            #midi_events = pygame.midi.midis2events(midi_events, self.midi_input.device_id)
            midi_events = self.midis2events(midi_events_raw, self.midi_input.device_id)
            for midi_event in midi_events:
                print(midi_event)

    def midis2events(self, midis, device_id):
        COMMANDS = {0: "NOTE_OFF",
                    1: "NOTE_ON",
                    2: "KEY_AFTER_TOUCH",
                    3: "CONTROLLER_CHANGE",
                    4: "PROGRAM_CHANGE",
                    5: "CHANNEL_AFTER_TOUCH",
                    6: "PITCH_BEND"}
        # Incomplete listing: this is the key to CONTROLLER_CHANGE events data1
        CONTROLLER_CHANGES = {1: "MOD WHEEL",
                              2: "BREATH",
                              4: "FOOT",
                              5: "PORTAMENTO",
                              6: "DATA",
                              7: "VOLUME",
                              10: "PAN",
                              }
        evs = []
        for midi in midis:

            ((status, data1, data2, data3), timestamp) = midi
            if status == 0xFF:
                # pygame doesn't seem to get these, so I didn't decode
                command = "META"
                channel = None
            else:
                try:
                    command = COMMANDS[ (status & 0x70) >> 4]
                except:
                    command = status & 0x70
                channel = status & 0x0F
            e = pygame.event.Event(pygame.midi.MIDIIN,
                                   status=status,
                                   command=command,
                                   channel=channel,
                                   data1=data1,
                                   data2=data2,
                                   timestamp=timestamp,
                                   vice_id=device_id)
            evs.append(e)
        return evs


if __name__ == "__main__":
    m = midi_interface()
    m.device_list()
    m.device_select("a")
    m.read_loop()
