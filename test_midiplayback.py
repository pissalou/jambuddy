import globals
from midiplayback import MidiPlayback
from midiutils import extract_bpm
import mido
from unittest.mock import Mock, call


def test_midi_playback_sixth_measure_first_beat():
    mid = MidiPlayback('.\\test\\The Blues Brothers-Peter Gunn Theme.mid', melody_track=1, start_position=16, stop_position=17)
    # globals.current_bpm = mid.original_bpm
    assert mid.start_position == mid.ticks_per_beat * 24  # other melody starts at measure 6
    assert mid.stop_position == mid.ticks_per_beat * 25  # & we play only 1 beat of measure 6
    # the melody track is muted (messages are removed from the merged_tracks)
    # the other melody used for assertions starts 4 measures later
    port_mock = Mock(spec=mido.ports.BaseOutput)
    for msg in mid.play():
        port_mock.send(msg)
    port_mock.send.assert_has_calls([
        call(mido.Message('note_on', channel=0, note=62, velocity=96, time=0)),
        call(mido.Message('note_off', channel=9, note=40, velocity=64, time=0)),
        call(mido.Message('note_on', channel=9, note=49, velocity=80, time=0)),
        call(mido.Message('note_on', channel=9, note=36, velocity=80, time=0)),
        call(mido.Message('note_off', channel=9, note=49, velocity=64, time=0.25)),
        call(mido.Message('note_off', channel=9, note=36, velocity=64, time=0)),
        call(mido.Message('note_on', channel=9, note=42, velocity=80, time=0))
    ])


def test_midi_playback_seventh_measure_first_beat():
    mid = MidiPlayback('.\\test\\The Blues Brothers-Peter Gunn Theme.mid', melody_track=1, start_position=20, stop_position=21)
    assert mid.start_position == mid.ticks_per_beat * 28  # other melody starts at measure 6
    assert mid.stop_position == mid.ticks_per_beat * 29  # & we play only 1 beat of measure 6
    # the melody track is muted (messages are removed from the merged_tracks)
    # the other melody used for assertions starts 4 measures later
    port_mock = Mock(spec=mido.ports.BaseOutput)
    for msg in mid.play():
        port_mock.send(msg)
    port_mock.send.assert_has_calls([
        call(mido.Message('note_on', channel=0, note=59, velocity=96, time=0)),
        call(mido.Message('note_off', channel=9, note=40, velocity=64, time=0)),
        call(mido.Message('note_on', channel=9, note=49, velocity=80, time=0)),
        call(mido.Message('note_on', channel=9, note=36, velocity=80, time=0)),
        call(mido.Message('note_off', channel=9, note=49, velocity=64, time=0.25)),
        call(mido.Message('note_off', channel=9, note=36, velocity=64, time=0)),
        call(mido.Message('note_on', channel=9, note=42, velocity=80, time=0))
    ])


def test_midi_playback_start_third_beat():
    pass
