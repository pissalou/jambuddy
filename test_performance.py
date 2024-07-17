import mido
from mido import MidiFile, Message, MetaMessage, second2tick
from abcutils import abc2midi
import copy
from performance import PerformanceTracker
from unittest.mock import Mock, call

DEFAULT_MELODY = ["E/2", "E/2", "^F/2", "E/2", "G/4", "^G/4", "E/2", "A/2", "^G/2"]


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


def test_midifile_play_as_expected():
    mid = MidiFile('.\\test\\The Blues Brothers-Peter Gunn Theme.mid')
    mid._merged_track = mido.merge_tracks(mid.tracks[0:2])  # keep only track #1 with tempo and #2 with the riff
    mid._merged_track = mid._merged_track[8:26]  # keep just the main riff melody
    mid._merged_track[0].time = 0  # remove any start offset
    assert mid._merged_track == mido.merge_tracks(as_midi_file(DEFAULT_MELODY, tempo_bpm=116, transpose=-24, default_velocity=80).tracks)[1:-1]  # TODO make test less cryptic


def test_midi_performance_as_expected():
    mid = MidiFile('.\\test\\The Blues Brothers-Peter Gunn Theme.mid')
    mid._merged_track = mido.merge_tracks(mid.tracks[0:2])  # keep only track #1 with tempo and #2 with the riff
    mid._merged_track = mid._merged_track[8:26]  # keep just the main riff melody
    mid._merged_track[0].time = 0  # remove any start offset
    # at this point, meta_msg set_tempo is lost, the tempo will be set to the default 120 bpm
    port_mock = Mock(spec=mido.ports.BaseOutput)
    for msg in mid.play():
        port_mock.send(msg)
    port_mock.send.assert_has_calls([call(midi_msg) for midi_msg in as_midi_performance(DEFAULT_MELODY, tempo_bpm=120, transpose=-24, default_velocity=80)])


def test_melody_played_as_expected():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    performance_tracker = PerformanceTracker(DEFAULT_MELODY, tempo_bpm=116)
    port_mock = Mock(spec=mido.ports.BaseOutput)
    performance_tracker.port_out = port_mock
    for note in as_midi_file(played_melody).play():
        performance_tracker.process(note)
    assert len(performance_tracker.errors) == 0
    port_mock.send.assert_has_calls([call(midi_msg) for midi_msg in as_midi_performance(played_melody)])


def test_melody_played_with_omission():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    played_melody[4] = 'G/2'  # was 'G/4'
    played_melody.pop(5)  # was '^G/4'
    performance_tracker = PerformanceTracker(DEFAULT_MELODY, tempo_bpm=116)
    port_mock = Mock(spec=mido.ports.BaseOutput)
    performance_tracker.port_out = port_mock
    for note in as_midi_file(played_melody).play():
        performance_tracker.process(note)
    port_mock.send.assert_has_calls([call(midi_msg) for midi_msg in as_midi_performance(played_melody)])
    assert len(performance_tracker.errors) == 1
    assert performance_tracker.errors[0].error_type == 'note_omission'  # error type is one of omission, insertion, substitution
    assert performance_tracker.errors[0].expected_note == abc2midi('G^/4')  # G^/4
    assert performance_tracker.errors[0].expected_time == 1234  # in ticks
