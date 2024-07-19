import logging
import time
import threading
import typing

from mido import Message
from fractions import Fraction


logger = logging.getLogger(__name__)


# TODO create a Tempo class that can be represented in BPM and contain BPS internally

class TempoTracker(threading.Thread):
    """
    Track tempo fluctuations throughout a performance.
    The assumption made here is that the melody received is played without any omission or insertion.
    """
    def __init__(self, expected_rhythm, tempo_bpm=120, allowed_tempo_deviation=None, port_in=None, port_out=None):
        """ Rhythm is a list of fractions """
        super().__init__()
        self.rhythm = expected_rhythm
        self.original_bpm = tempo_bpm
        self.current_bps = tempo_bpm / 60
        self.port_in = port_in
        self.port_out = port_out
        self.previous_time = None
        self.rhythm_idx = 0

    def process(self, midi_msg: Message) -> typing.Optional[float]:
        """
        Process incoming MIDI message to determine tempo
        :param midi_msg the MIDI message to process
        :return a float containing the BPS if applicable or None
        """
        if midi_msg.type != 'note_on':
            # logger.info('%s: %d %f%%', self, round(self.previous_tempo_deviation * 60))
            return None
        calculated_tempo_bps = 0
        if self.rhythm_idx != 0 and self.previous_time is not None:
            previous_note_expected_length = self.rhythm[self.rhythm_idx % len(self.rhythm) - 1]  # length is a fraction
            seconds_since_previous_note = time.time() - self.previous_time
            if seconds_since_previous_note == 0:
                logger.info('%s: %d', self, 0)
                return 0.0
            calculated_tempo_bps = (previous_note_expected_length / seconds_since_previous_note)
            self.current_bps = calculated_tempo_bps
        # prepare for the next iteration
        self.previous_time = time.time()
        self.rhythm_idx += 1
        logger.info('%s: %d', self, round(calculated_tempo_bps * 60))
        return calculated_tempo_bps

    def _fraction2second(self, fraction: Fraction) -> float:
        return fraction / self.current_bps

    def __str__(self):
        return f"Tempo(original_bpm={self.original_bpm}, current_bpm={round(self.current_bps*60)})"

    def run(self):
        while True:
            self.process(self.port_in.process())
