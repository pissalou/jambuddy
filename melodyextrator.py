import json
import itertools
import random
import re
import time
import mido
from fractions import Fraction
from mido import MidiFile, MetaMessage
from mingus.core import chords
from time import gmtime, strftime
from utils import midi2name, name2midi


def search_note_off_for(track, note, index):
    """ search for the note release/note_off message """
    tuples = [(idx, msg) for idx, msg in enumerate(track[index:]) if not isinstance(msg, MetaMessage) and msg.note == note and (msg.type == 'note_off' or msg.velocity == 0)]
    return index + tuples[0][0]


def time_delta_between_indices(track, idx1, idx2):
    """ give the length of a note by summing the deltas between note_on and note_off """
    return sum([msg.time for msg in track[idx1:idx2]])


def quantize_time(ticks, ticks_per_beat, division=32):
    """ default quantize ticks to 1/64th notes """
    ticks_per_division = ticks_per_beat / division
    return int(round(ticks / ticks_per_division) * ticks_per_division)


def simplify(notes, key='C'):
    """ return the fundamental for a list of tuple notes """
    octave = str(int(re.search(r'[0-9$]', notes[0][0]).group()) + 0)
    note_map = {note[0]: note for note in notes}
    if len(notes) == 1:
        return notes[0]
    unpitched_notes = list(map(lambda x: re.sub(r'[0-9]', '', x[0]), notes))
    reoccuring_note = next(iter([pitch for pitch, occurrence in {note: unpitched_notes.count(note) / len(notes) for note in
                                                                 unpitched_notes}.items() if (occurrence > 0.5 and len(notes) > 2) or occurrence >= 0.5]), None)
    if reoccuring_note:
        # return note_map[reoccuring_note + octave]
        return (reoccuring_note + octave, notes[1][1], notes[1][2])  # therefore return a new tuple
    if len(notes) == 2:  # TODO: prepend or append key when chord is a dyad
        return notes.append((key, 0, 0))
    # if more than half the notes are the same, we keep that note
    shorthand_chord_name = chords.determine([re.sub(r'[0-9]', '', note[0]) for note in notes], shorthand=True)
    if shorthand_chord_name:
        # return note_map[re.search("^[A-G]#?", shorthand_chord_name[0]).group() + octave]  # TODO the octave could be wrong
        return (re.search("^[A-G]#?", shorthand_chord_name[0]).group() + octave, notes[1][1], notes[1][2])  # therefore return a new tuple
    full_chord_name = chords.determine([re.sub(r'[0-9]', '', note[0]) for note in notes])
    if full_chord_name:
        return note_map[re.search("^[A-G]#?", full_chord_name[0]).group() + octave]
    random.shuffle(notes)
    return simplify(notes, key)


# open first available port
port = mido.open_output(mido.get_output_names()[0])
# load midi file
mid = MidiFile('test/mozk331c.mid')
# display some information about the midi file
meta_msgs = [msg for msg in list(mid) if msg.is_meta]
print('Track Name: ' + [meta_msg.name for meta_msg in meta_msgs if meta_msg.type == 'track_name'][0])
print('BPM: ' + str(mido.tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])))
time_signature = [meta_msg for meta_msg in meta_msgs if meta_msg.type == 'time_signature'][0]
print('Signature: ' + str(time_signature.numerator) + '/' + str(time_signature.denominator))
print('Key: ' + [meta_msg.key for meta_msg in meta_msgs if meta_msg.type == 'key_signature'][0])
print('Playback duration: ' + strftime("%M:%S", gmtime(mid.length)))
# print notes in track 1
track = mid.tracks[1]
ticks_per_beat = mid.ticks_per_beat
notes = [(midi2name(msg.note),
         str(Fraction(quantize_time(time_delta_between_indices(track, idx + 1, search_note_off_for(track, msg.note, idx) + 1), ticks_per_beat)) / ticks_per_beat),
         quantize_time(time_delta_between_indices(track, 1, search_note_off_for(track, msg.note, idx) + 1), ticks_per_beat))
         for idx, msg in enumerate(track) if not msg.is_meta and msg.type.startswith('note_o')]
# notes are tuples (name, duration, position)
# simplify step 1: remove ghost notes (less than an 1/8th note)
notes = [note for note in notes if Fraction(note[1]) > Fraction(1 / 8)]
# simplify step 2: replace chords by their fundamental f0
positional_map = {pos: list(note) for pos, note in itertools.groupby(notes, lambda n: n[2])}
for pos, chord in positional_map.items():
    positional_map[pos] = simplify(chord) if len(chord) > 1 else chord[0]
notes = list(positional_map.values())
notes = ''.join([note[0] for note in notes])  # keep only the pitches
# TODO extract fundamental from chords
RIFF_REGEX = r'(.{16,}?)\1+'   # 8 notes at least
riffs = re.findall(RIFF_REGEX, notes)
print(f'Found {len(riffs)} riffs')
melody_dict = {melody: len(re.findall(fr"(?={melody})", notes)) for melody in re.findall(RIFF_REGEX, notes)}
# sort melodies from most recurring to least
melody_dict = dict(sorted(melody_dict.items(), key=lambda item: item[1], reverse=True))
print(json.dumps(melody_dict, indent=2))
# play each melody


def play_notes(midi_notes):
    print('Playing ' + ','.join([midi2name(midi_note) for midi_note in midi_notes]))
    for note in midi_notes:
        port.send(mido.Message('note_on', note=note))
        time.sleep(mido.tick2second(96 * 2, 480, mido.bpm2tempo(120)))
        port.send(mido.Message('note_off', note=note))


for melody in melody_dict.keys():
    play_notes([name2midi(notename) for notename in re.split(r'(?=[A-G][b#]?\d)', melody)[1:]])

port.close()
