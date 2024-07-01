import threading
# TODO rename file main.py
import mido
from mido import MidiFile, Message, second2tick, tempo2bpm, bpm2tempo, tick2second
from performance import PerformanceTracker
import time
from time import strftime, gmtime
from fractions import Fraction
from abcutils import midi2abc
import globals


class TimeStretchableMidiFile(MidiFile):

    def __iter__(self):
        absolute_time = 0
        for msg in self.merged_track:
            # Convert message time from absolute time in ticks to relative time in seconds.
            if msg.time > 0:
                delta = tick2second(msg.time, self.ticks_per_beat, bpm2tempo(globals.current_bpm))
            else:
                delta = 0
            absolute_time += msg.time
            # print('\r%5.2f'% (absolute_time / self.ticks_per_beat), end='')
            yield msg.copy(skip_checks=True, time=delta)
            # yield MetaMessage(**vars(msg)) if msg.is_meta else Message(**(vars(msg) | {'data': absolute_time}))

            # if msg.type == 'set_tempo':
            #     globals.current_bpm = tempo2bpm(msg.tempo)


# IMPORTANT plug a midi keyboard at this point
print(f'Output devices: {mido.get_output_names()}')
port_out = mido.open_output(mido.get_output_names()[-1])
# load midi file
mid = TimeStretchableMidiFile("C:\\Users\\mazars\\Downloads\\The Blues Brothers-Peter Gunn Theme.mid")
# display some information about the midi file
meta_msgs = [msg for msg in list(mid) if msg.is_meta]
print('Track Names: ' + ','.join([meta_msg.name for meta_msg in meta_msgs if meta_msg.type == 'track_name']))
original_bpm = mido.tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])
print('Original BPM: ' + str(round(original_bpm)))
time_signature = [meta_msg for meta_msg in meta_msgs if meta_msg.type == 'time_signature'][0]
print('Signature: ' + str(time_signature.numerator) + '/' + str(time_signature.denominator))
# print('Key: ' + [meta_msg.key for meta_msg in meta_msgs if meta_msg.type == 'key_signature'][0])
print('Playback duration: ' + strftime("%M:%S", gmtime(mid.length)))
# print notes in track 1

# note times are in fractions of a quarter note (to be more compliant with ABC notation)
# melody = ["E/2", "E/2", "^F/2", "E/2", "G/4", "^G/4", "E/2", "A/2", "^G/2"]
melody = ["E/2", "E/2", "E/2", "E/2"]  # Super simplified melody
melody_start = 3840  # in ticks


print(f'Input devices: {mido.get_input_names()}')
port_in = mido.open_input(mido.get_input_names()[0])


def filtered_receive(port, message_types=['note_on', 'note_off']):
    received_event = port.process()
    if received_event.type in message_types:
        return received_event
    return port.process()


def playback():
    for msg in mid.play():
        port_out.send(msg)


# Poor man's play_at_beat
mid._merged_track = mid._merged_track[81:]  # TODO: calculate where to find beat no. 2 of the riff
mid._merged_track = mido.merge_tracks(mid.tracks[2:])  # Remove Track no. 1


melody_note_idx = 0
previous_time = 0
calculated_tempo_bps = original_bpm / 60
playback_started = False


def fraction2second(fraction: Fraction) -> float:
    return fraction / calculated_tempo_bps


def midi_message_received_callback(self):
    if self.melody_note_idx == 3 and not self.playback_started:
        self.playback_started = True
        playback_thread = threading.Thread(target=playback)
        playback_thread.start()


performance_tracker = PerformanceTracker(expected_melody=melody, tempo_bpm=globals.current_bpm, port_in=port_in, port_out=port_out, midi_message_received_callback=midi_message_received_callback)
performance_tracker.start()
