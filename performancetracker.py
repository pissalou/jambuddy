import threading

import mido
from mido import MidiFile, Message, second2tick, tempo2bpm, bpm2tempo, tick2second
import time
from time import strftime, gmtime
from fractions import Fraction
from abcutils import midi2abc

current_bpm = 116


class TimeStretchableMidiFile(MidiFile):

    def __iter__(self):
        global current_bpm
        absolute_time = 0
        for msg in self.merged_track:
            # Convert message time from absolute time in ticks to relative time in seconds.
            if msg.time > 0:
                delta = tick2second(msg.time, self.ticks_per_beat, bpm2tempo(current_bpm))
            else:
                delta = 0
            absolute_time += msg.time
            # print('\r%5.2f'% (absolute_time / self.ticks_per_beat), end='')
            yield msg.copy(skip_checks=True, time=delta)
            # yield MetaMessage(**vars(msg)) if msg.is_meta else Message(**(vars(msg) | {'data': absolute_time}))

            if msg.type == 'set_tempo':
                current_bpm = tempo2bpm(msg.tempo)


# IMPORTANT plug a midi keyboard at this point
print(f'Output devices: {mido.get_output_names()}')
port_out = mido.open_output(mido.get_output_names()[-1])
# load midi file
mid = TimeStretchableMidiFile("C:\\Users\\mazars\\Downloads\\The Blues Brothers-Peter Gunn Theme.mid")
# display some information about the midi file
meta_msgs = [msg for msg in list(mid) if msg.is_meta]
print('Track Names: ' + ','.join([meta_msg.name for meta_msg in meta_msgs if meta_msg.type == 'track_name']))
original_bpm = mido.tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])
print('BPM: ' + str(round(original_bpm)))
time_signature = [meta_msg for meta_msg in meta_msgs if meta_msg.type == 'time_signature'][0]
print('Signature: ' + str(time_signature.numerator) + '/' + str(time_signature.denominator))
# print('Key: ' + [meta_msg.key for meta_msg in meta_msgs if meta_msg.type == 'key_signature'][0])
print('Playback duration: ' + strftime("%M:%S", gmtime(mid.length)))
# print notes in track 1

# note times are in fractions of a quarter note (to be more compliant with ABC notation)
melody = [Message('note_on', channel=0, note=40, velocity=80, time=Fraction('1/2')),
          Message('note_on', channel=0, note=40, velocity=80, time=Fraction('1/2')),
          Message('note_on', channel=0, note=42, velocity=80, time=Fraction('1/2')),
          Message('note_on', channel=0, note=40, velocity=80, time=Fraction('1/2')),
          Message('note_on', channel=0, note=43, velocity=80, time=Fraction('1/4')),
          Message('note_on', channel=0, note=44, velocity=80, time=Fraction('1/4')),
          Message('note_on', channel=0, note=40, velocity=80, time=Fraction('1/2')),
          Message('note_on', channel=0, note=45, velocity=80, time=Fraction('1/2')),
          Message('note_on', channel=0, note=44, velocity=80, time=Fraction('1/2'))]
melody_start = 3840  # in ticks


print(f'Input devices: {mido.get_input_names()}')
port_in = mido.open_input(mido.get_input_names()[0])


def filtered_receive(port, message_type='note_on'):
    received_event = port.receive()
    if received_event.type == message_type:
        return received_event
    return port.receive()


def play_back():
    for msg in mid.play():
        port_out.send(msg)


# Poor man's play_at_beat
mid._merged_track = mid._merged_track[81:]  # TODO: start at beat no. 2 of the riff
mid._merged_track = mido.merge_tracks(mid.tracks[2:])  # Remove Track no. 1


melody_note_idx = 0
previous_time = 0
calculated_tempo_bps = original_bpm / 60
playback_started = False


def fraction2second(fraction: Fraction) -> float:
    return fraction / calculated_tempo_bps


while True:
    print(f'\rExpecting {midi2abc(melody[melody_note_idx].note)}{melody[melody_note_idx].time}\tCalculated tempo: {calculated_tempo_bps * 60:.2f}', end='')
    # print(f'Expecting note {melody[melody_note_idx].note} in    {expected_note_duration if melody_note_idx != 0 else 0:.2f}s...')
    received_event = filtered_receive(port_in, message_type='note_on')
    if melody_note_idx == 0 and previous_time == 0:
        previous_time = time.time()
    else:
        previous_note_expected_length = melody[melody_note_idx - 1].time  # in fraction
        previous_note_expected_duration = fraction2second(previous_note_expected_length)  # in seconds
        seconds_since_previous_note = time.time() - previous_time
        calculated_tempo_bps = (previous_note_expected_length / seconds_since_previous_note)
        current_bpm = calculated_tempo_bps * 60 if 1.8 < calculated_tempo_bps < 2.1 else current_bpm  # TODO: TempoTracker
    # print(f'Received note  {received_event.note} after {previous_note_duration:.2f}s')
    previous_time = time.time()
    port_out.send(received_event)
    melody_note_idx = (melody_note_idx + 1) % len(melody)
    # TODO start playing the other tracks at the calculated tempo
    if melody_note_idx == 3 and not playback_started:
        # mid.play_at(melody_start + second2tick((melody[1].time + melody[2].time + melody[3].time) / tempo_bps))
        # pass
        playback_started = True
        playback_thread = threading.Thread(target=play_back)
        playback_thread.start()

for msg in melody:
    port_out.send(msg)
    time.sleep(msg.time)


for msg in mid.play():
    port_out.send(msg)
