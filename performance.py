import threading
import time
from fractions import Fraction
from mido import Message


def filtered_receive(port, message_types=['note_on', 'note_off']):
    received_event = port.receive()
    if received_event.type in message_types:
        return received_event
    return port.receive()


class PerformanceTracker(threading.Thread):

    def __init__(self, expected_melody, tempo_bpm=120, port_in=None, port_out=None):
        super().__init__()
        self.melody = expected_melody
        self.tempo_bps = tempo_bpm / 60
        self.current_bps = self.tempo_bps
        self.port_in = port_in
        self.port_out = port_out
        self.melody_note_idx = 0
        self.previous_time = 0
        self.playback_started = False

    def _fraction2second(self, fraction: Fraction) -> float:
        return fraction / self.current_bps

    def receive(self, midi_msg: Message):
        print(f'\rExpecting {self.melody[self.melody_note_idx]}\tCalculated tempo: {self.tempo_bps * 60:.2f}', end='')
        # print(f'Expecting note {melody[melody_note_idx].note} in    {expected_note_duration if melody_note_idx != 0 else 0:.2f}s...')
        received_event = midi_msg
        if received_event.type == 'note_off':
            self.port_out.send(received_event)
            return
        if self.melody_note_idx == 0 and self.previous_time == 0:
            previous_time = time.time()
        else:
            previous_note_expected_length = self.melody[self.melody_note_idx - 1].time  # in fraction
            previous_note_expected_duration = self._fraction2second(previous_note_expected_length)  # in seconds
            seconds_since_previous_note = time.time() - self.previous_time
            calculated_tempo_bps = (previous_note_expected_length / seconds_since_previous_note)
            self.current_bps = calculated_tempo_bps if 1.8 < calculated_tempo_bps < 2.1 else self.current_bps  # TODO: TempoTracker
        # print(f'Received note  {received_event.note} after {seconds_since_previous_note:.2f}s')
        previous_time = time.time()
        self.port_out.send(received_event)
        melody_note_idx = (self.melody_note_idx + 1) % len(self.melody)
        # TODO start playing the other tracks at the calculated tempo
        if melody_note_idx == 3 and not self.playback_started:
            # mid.play_at(melody_start + second2tick((melody[1].time + melody[2].time + melody[3].time) / tempo_bps))
            # pass
            playback_started = True
            # playback_thread = threading.Thread(target=play_back)
            # playback_thread.start()

    @property
    def errors(self):
        return []
