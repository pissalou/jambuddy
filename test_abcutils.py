from abcutils import abc2beatcount, abc2midi
from mido import Message
from fractions import Fraction


def test_abc2beatcount():
    assert abc2beatcount('a') == 1.0
    assert abc2beatcount('a1') == 1.0
    assert abc2beatcount('a/') == 0.5
    assert abc2beatcount('a/2') == 0.5
    assert abc2beatcount('a/4') == 0.25
    assert abc2beatcount('a//') == 0.25
    assert abc2beatcount('a3/4') == 0.75

    assert abc2beatcount('abc') == 3.0
    assert abc2beatcount('a,bc\'') == 3.0
    assert abc2beatcount('a1b2c3') == 6.0
    assert abc2beatcount('a/1b/2c/4') == 1.75
    assert abc2beatcount('ab/2c3/4') == 2.25
    assert abc2beatcount('ab/c//') == 1.75

    assert abc2beatcount('(ab) c') == 3.0
    assert abc2beatcount('a2b2 | c') == 5.0
    assert abc2beatcount('a2zz | c') == 5.0


QUARTER_NOTE = Fraction(1, 4)


def test_abc2midi():
    """ Test abc notes with default note length first """
    assert abc2midi('C') == Message(type="note_on", note=60, time=QUARTER_NOTE)  # C4
    assert abc2midi('c') == Message(type="note_on", note=72, time=QUARTER_NOTE)  # C5
    assert abc2midi('C\'') == Message(type="note_on", note=72, time=QUARTER_NOTE)  # C5
    assert abc2midi('c\'') == Message(type="note_on", note=84, time=QUARTER_NOTE)  # C6
    assert abc2midi('C,') == Message(type="note_on", note=48, time=QUARTER_NOTE)  # C3
    assert abc2midi('C,,') == Message(type="note_on", note=36, time=QUARTER_NOTE)  # C2
    assert abc2midi('^C') == Message(type="note_on", note=61, time=QUARTER_NOTE)  # C#4
    assert abc2midi('=B,') == Message(type="note_on", note=59, time=QUARTER_NOTE)  # Cb4


def test_abc2midi_with_length():
    """ Test abc notes with different note lengths """
    assert abc2midi('C1') == Message(type="note_on", note=60, time=Fraction('1/4'))  # C4 quarter note
    assert abc2midi('C2') == Message(type="note_on", note=60, time=Fraction('1/2'))  # C4 half note
    assert abc2midi('C4') == Message(type="note_on", note=60, time=Fraction('1/1'))  # C4 whole note, pretty confusing right?
    assert abc2midi('C1/2') == Message(type="note_on", note=60, time=Fraction('1/8'))  # C4 eighth note
    assert abc2midi('C/2') == Message(type="note_on", note=60, time=Fraction('1/8'))  # C4 eighth note, shorter syntax
    assert abc2midi('C/4') == Message(type="note_on", note=60, time=Fraction('1/16'))  # C4 sixteenth note, short syntax
