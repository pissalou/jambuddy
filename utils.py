import re

# TODO: support abc notation
# TODO: and then migrate to abcutils.py
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi2name(midinote) -> str:
    """
    Converts the midi note value to american note name.
    """
    return NOTES_SHARP[int(midinote % 12)] + str(int(midinote / 12) - 1)


def name2midi(name) -> int:
    """ name is a string formatted like 'C#3' """
    key = re.findall(r"[A-G][#b]*", name)[0]  # eg C, Db
    octave = re.findall(r"\d+$", name)[0]   # eg 3, 4
    try:
        pos = NOTES_FLAT.index(key) if 'b' in key else NOTES_SHARP.index(key)
    except IndexError:
        raise ValueError('The key is not valid', key)
    return pos + 12 * (int(octave) + 1)
