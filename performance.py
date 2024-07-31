import threading
import time
import typing
from fractions import Fraction
from mido import Message
from tempo import TempoTracker
from abccoloramaview import AbcColoramaView
from abcutils import abc2beatcount
import state

import logging
logging.basicConfig(filename='latestperformance.log', filemode='w', format='%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def filtered_receive(port, message_types=('note_on', 'note_off')):
    received_event = port.process()
    if received_event.type in message_types:
        return received_event
    return port.process()


class PerformanceTracker(threading.Thread):

    def __init__(self, expected_melody, tempo_bpm=120, port_in=None, port_out=None, midi_message_received_callback: typing.Optional[typing.Callable] = None):
        super().__init__()
        self.melody = expected_melody
        self.tempo_bps = tempo_bpm / 60
        self.current_bps = self.tempo_bps
        self.port_in = port_in
        self.port_out = port_out
        self.melody_note_idx = 0
        self.playback_started = False
        self.midi_message_received_callback = midi_message_received_callback
        self.tempo_tracker = TempoTracker([abc2beatcount(note) for note in expected_melody], tempo_bpm)

    def _fraction2second(self, fraction: Fraction) -> float:
        return fraction / self.current_bps

    def process(self, midi_msg: Message):
        logger.debug('<- %s', midi_msg)
        print(f'\rExpecting {self.melody[self.melody_note_idx]}\tCalculated tempo: {self.current_bps * 60:.2f}', end='')
        # print(f'Expecting note {melody[melody_note_idx].note} in    {expected_note_duration if melody_note_idx != 0 else 0:.2f}s...')
        received_event = midi_msg
        if received_event.type == 'note_off':
            self.port_out.send(received_event)
            # print(f' {self.current_bps * 60:.2f}', end='')
            return
        calculated_tempo_bps = self.tempo_tracker.process(midi_msg)
        tempo_deviation = (state.current_bpm - calculated_tempo_bps * 60) / state.current_bpm
        print(f' -- {round(calculated_tempo_bps * 60):0=3}bpm - deviation {round(tempo_deviation * 100):0=+5}%', end='')
        if abs(tempo_deviation) < 0.3:  # TODO make allowed_tempo_deviation configurable
            self.current_bps = calculated_tempo_bps
        # start playing the other tracks at the calculated tempo
        state.current_bpm = self.current_bps * 60
        logger.info('current.bpm: %f', state.current_bpm)
        self.port_out.send(received_event)  # TODO: reorder lines of code to improve UX?
        self.melody_note_idx = (self.melody_note_idx + 1) % len(self.melody)
        if self.midi_message_received_callback is not None:
            self.midi_message_received_callback(self)

    @property
    def errors(self):
        return []

    def run(self):
        while True:
            if self.port_in is not None:
                msg = self.port_in.receive()
                self.process(msg)
            else:  # trigger playback at 120bpm
                self.process(Message(type="note_on", note=52, velocity=1, time=0.25))
                time.sleep(0.25)
