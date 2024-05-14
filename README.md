See https://mido.readthedocs.io/en/stable/


Play a arpeggio in C:
---------------------

import mido
import time
port = mido.open_output(mido.get_output_names()[0])
for note in [60, 64, 67, 72]:
    port.send(mido.Message('note_on', note=note))
    time.sleep(mido.tick2second(480, 480, mido.bpm2tempo(120)))
    port.send(mido.Message('note_off', note=note))
port.close()

Read MIDI file:
---------------
import mido
from mido import MidiFile
from time import gmtime, strftime
port = mido.open_output(mido.get_output_names()[0])
mid = MidiFile('mozk331c.mid')
meta_msgs = [msg for msg in list(mid) if msg.is_meta]
print('Track Name: ' + [meta_msg.name for meta_msg in meta_msgs if meta_msg.type == 'track_name'][0])
print('BPM: ' + str(mido.tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])))
time_signature = [meta_msg for meta_msg in meta_msgs if meta_msg.type == 'time_signature'][0]
print('Signature: ' + str(time_signature.numerator) + '/' + str(time_signature.denominator))
print('Playback duration: ' + strftime("%M:%S", gmtime(mid.length)))
#mid.print_tracks()
#mid.tracks[0].clear()
mid._merged_track = mido.merge_tracks(mid.tracks[1:2]) # keep only Track no. 1
for msg in mid.play():
    port.send(msg)
port.close()

Panic:
------
port.panic()