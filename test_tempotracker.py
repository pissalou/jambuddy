from fractions import Fraction
import copy

import state
from tempo import TempoTracker
from test_utils import as_midi_file
from abcutils import abc2beatcount
from pytest import approx

DEFAULT_MELODY = ["E/2", "E/2", "^F/2"]
DEFAULT_RHYTHM = [abc2beatcount(note) for note in DEFAULT_MELODY]


def test_melody_wrap():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    tempo_tracker = TempoTracker(DEFAULT_RHYTHM, tempo_bpm=116)
    for note in as_midi_file(played_melody + played_melody, tempo_bpm=116).play():
        tempo_tracker.process(note)
    assert tempo_tracker.rhythm_idx == 6  # melody was played twice


def test_melody_played_as_expected():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    tempo_tracker = TempoTracker(DEFAULT_RHYTHM, tempo_bpm=116)
    for note in as_midi_file(played_melody, tempo_bpm=116).play():
        tempo_tracker.process(note)
    assert tempo_tracker.rhythm_idx == 3  # all notes have been received
    assert approx(tempo_tracker.current_bps * 60, 0.01) == 116


def test_melody_played_faster():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    played_melody[1] = 'E31/64'  # was 'E/2'
    tempo_tracker = TempoTracker(DEFAULT_RHYTHM, tempo_bpm=116)
    for note in as_midi_file(played_melody, tempo_bpm=116).play():
        tempo_tracker.process(note)
    assert tempo_tracker.rhythm_idx == 3  # all notes have been received
    assert approx(tempo_tracker.current_bps * 60, 0.01) == 120  # a bit faster!


def test_melody_played_slower():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    played_melody[1] = 'E33/64'  # was 'E/2'
    tempo_tracker = TempoTracker(DEFAULT_RHYTHM, tempo_bpm=116)
    for note in as_midi_file(played_melody, tempo_bpm=116).play():
        tempo_tracker.process(note)
    assert tempo_tracker.rhythm_idx == 3  # all notes have been received
    assert approx(tempo_tracker.current_bps * 60, 0.01) == 112  # a bit slower!


def test_melody_played_way_too_slow():
    state.bpm = 116
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    played_melody[1] = 'E3/4'  # was 'E/2'
    tempo_tracker = TempoTracker(DEFAULT_RHYTHM, tempo_bpm=116, allowed_tempo_deviation=0.05)
    tempo_map = []  # tempo map is a list!
    for note in as_midi_file(played_melody, tempo_bpm=116).play():
        tempo_bps = tempo_tracker.process(note)
        if tempo_bps is not None:
            tempo_map.append(tempo_bps)
    assert tempo_tracker.rhythm_idx == 3  # all notes have been received
    assert len(tempo_map) == 3
    tempo_deviation = (tempo_map[2] - tempo_map[1]) / tempo_map[1]
    assert abs(tempo_deviation) > 0.3
    # assert approx(tempo_tracker.current_bps * 60, 0.01) == 116  # TODO how to check no change in bpm, must be a bad note


def test_chord_does_not_raise_divisionbyzero():
    played_melody = copy.deepcopy(DEFAULT_MELODY)
    played_melody[1] = 'E/9999'  # was 'E/2'
    tempo_tracker = TempoTracker(DEFAULT_RHYTHM, tempo_bpm=116, allowed_tempo_deviation=0.05)
    for note in as_midi_file(played_melody, tempo_bpm=116).play():
        _ = tempo_tracker.process(note)
    assert tempo_tracker.rhythm_idx == 2  # 3 notes have been received but only 2 count as part of the rhythm
