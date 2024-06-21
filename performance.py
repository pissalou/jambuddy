import threading
import time
import typing
from fractions import Fraction
from mido import Message
from tempo import TempoTracker
from abcutils import abc2beatcount
from midiplayback import MidiPlayback
import mido


def filtered_receive(port, message_types=('note_on', 'note_off')):
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
        self.tempo_tracker = TempoTracker([abc2beatcount(note) for note in expected_melody], tempo_bpm)

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
        calculated_tempo_bps, tempo_deviation = self.tempo_tracker.process(midi_msg)
        print(f' {calculated_tempo_bps * 60:.2f} deviation {tempo_deviation * 100}%', end='')
        self.current_bps = calculated_tempo_bps
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
            msg = self.port_in.receive()
            self.process(msg)
