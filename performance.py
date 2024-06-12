import threading
import time
import typing
from fractions import Fraction
from mido import Message
from abcutils import abc2midi
from midiplayback import MidiPlayback
import mido


def filtered_receive(port, message_types=['note_on', 'note_off']):
    received_event = port.process()
    if received_event.type in message_types:
        return received_event
    return port.process()


class PerformanceTracker(threading.Thread):

    def __init__(self, expected_melody, tempo_bpm=120, port_in=None, port_out=None, midi_message_received_callback: typing.Callable = None):
        super().__init__()
        self.melody = expected_melody
        self.tempo_bps = tempo_bpm / 60
        self.current_bps = self.tempo_bps
        self.port_in = port_in
        self.port_out = port_out
        self.melody_note_idx = 0
        self.previous_time = 0
        self.playback_started = False
        self.midi_message_received_callback = midi_message_received_callback

    def _fraction2second(self, fraction: Fraction) -> float:
        return fraction / self.current_bps

    def process(self, midi_msg: Message):
        print(f'\rExpecting {self.melody[self.melody_note_idx]}\tCalculated tempo: {self.current_bps * 60:.2f}', end='')
        # print(f'Expecting note {melody[melody_note_idx].note} in    {expected_note_duration if melody_note_idx != 0 else 0:.2f}s...')
        received_event = midi_msg
        if received_event.type == 'note_off':
            self.port_out.send(received_event)
            return
        if self.melody_note_idx == 0 and self.previous_time == 0:
            self.previous_time = time.time()  # start measuring time
        else:
            previous_note_expected_length = abc2midi(self.melody[self.melody_note_idx - 1]).time  # time is in fraction
            previous_note_expected_duration = self._fraction2second(previous_note_expected_length)  # time in seconds
            seconds_since_previous_note = time.time() - self.previous_time
            calculated_tempo_bps = (previous_note_expected_length / seconds_since_previous_note)
            self.current_bps = calculated_tempo_bps if 1.8 < calculated_tempo_bps < 2.1 else self.current_bps  # TODO: TempoTracker
        # print(f'Received note  {received_event.note} after {seconds_since_previous_note:.2f}s')
        previous_time = time.time()
        self.port_out.send(received_event)
        self.melody_note_idx = (self.melody_note_idx + 1) % len(self.melody)
        # start playing the other tracks at the calculated tempo
        if self.midi_message_received_callback:
            self.midi_message_received_callback(self)

    @property
    def errors(self):
        return []

    def run(self):
        while True:
            msg = self.port_in.process()
            self.process(msg)
