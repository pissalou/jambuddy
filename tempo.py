import logging
import time
import threading
from mido import Message
from fractions import Fraction


class TempoTracker(threading.Thread):
    """
    Track tempo fluctuations throughout a performance.
    The assumption made here is that the melody received is played without any omission or insertion.
    """

    def __init__(self, expected_rhythm, tempo_bpm=120, allowed_tempo_deviation=1, port_in=None, port_out=None):
        """ Rhythm is a list of fractions """
        super().__init__()
        self.rhythm = expected_rhythm
        self.tempo_bps = tempo_bpm / 60  # TODO: rename original_tempo_bps maybe?
        self.current_bps = self.tempo_bps
        self.allowed_tempo_deviation = allowed_tempo_deviation
        self.port_in = port_in
        self.port_out = port_out
        self.previous_time = None
        self.previous_calculated_tempo_bps = -1  # TODO: keep a tempo map (check how reaper does it)
        self.previous_tempo_deviation = -1
        self.rhythm_idx = 0

    def process(self, midi_msg: Message):
        if midi_msg.type != 'note_on':
            return self.previous_calculated_tempo_bps, self.previous_tempo_deviation  # a note_off typically
        calculated_tempo_bps = 0
        tempo_deviation = 0
        if self.rhythm_idx != 0 and self.previous_time is not None:
            previous_note_expected_length = self.rhythm[self.rhythm_idx % len(self.rhythm) - 1]  # length is a fraction
            previous_note_expected_duration = self._fraction2second(previous_note_expected_length)  # time in seconds
            seconds_since_previous_note = time.time() - self.previous_time
            if seconds_since_previous_note == 0:
                return 0, 1
            calculated_tempo_bps = (previous_note_expected_length / seconds_since_previous_note)
            logging.debug(f'Calculated tempo: {round(calculated_tempo_bps * 60)}bpm')
            tempo_deviation = abs(self.current_bps - calculated_tempo_bps) / self.current_bps if self.current_bps != 0 else 0
            logging.debug(f'Tempo deviation: {round(tempo_deviation * 100)}%')
            if tempo_deviation <= self.allowed_tempo_deviation:
                self.current_bps = calculated_tempo_bps
        # prepare for the next iteration
        self.previous_time = time.time()
        self.rhythm_idx += 1
        self.previous_calculated_tempo_bps = calculated_tempo_bps
        self.previous_tempo_deviation = tempo_deviation
        return calculated_tempo_bps, tempo_deviation

    def _fraction2second(self, fraction: Fraction) -> float:
        return fraction / self.current_bps

    def run(self):
        while True:
            self.process(self.port_in.process())
