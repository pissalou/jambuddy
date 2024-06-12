import mido
from mido import MidiFile, Message, MetaMessage, second2tick
from abcutils import abc2midi


def as_midi_performance(abc_notes, tempo_bpm=120, time_signature=(4, 4), transpose=0, default_velocity=64):
    tempo_bps = tempo_bpm / 60
    performance = list()  # TODO create a fixed-sized list that will contain note_on/note_off pairs
    for idx, abc_note in enumerate(abc_notes):
        note: Message = abc2midi(abc_note)
        note_duration = (note.time * time_signature[0]) / tempo_bps  # Fraction of beat to relative seconds
        performance.append(note.copy(time=0, note=note.note + transpose, velocity=default_velocity))
        performance.append(Message('note_off', channel=note.channel, note=note.note + transpose, velocity=64, time=note_duration))
    return performance


def as_midi_file(abc_notes, tempo_bpm=120, transpose=0, default_velocity=64):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    midi_tempo = mido.bpm2tempo(tempo_bpm)
    track.append(MetaMessage('set_tempo', tempo=midi_tempo))
    for midi_note in as_midi_performance(abc_notes, tempo_bpm=tempo_bpm, transpose=transpose, default_velocity=default_velocity):
        note = midi_note.copy(time=second2tick(midi_note.time, ticks_per_beat=mid.ticks_per_beat, tempo=midi_tempo))  # TODO relative seconds to absolute ticks
        track.append(note)
    track.append(MetaMessage('end_of_track'))
    return mid
