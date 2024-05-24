import re
import mido
from fractions import Fraction


def abc2beatcount(txt, note_length=1) -> float:
    """
        count the number of beats in an ABC note sequence
    :param txt:
    :return:
    """
    notes = re.findall(r'[A-Ga-gz][,\']*\d*/*\d*', txt)
    # print(f'Notes: {notes}')
    for idx, __ in enumerate(notes):
        notes[idx] = re.sub(r'/+$', '/' + str(notes[idx].count('/') * 2), notes[idx])
        notes[idx] = re.sub(r'[A-Ga-gz][,\']*(?!\d)', '1', notes[idx])
        notes[idx] = re.sub(r'[A-Ga-gz][,\']*(?=\d)', '', notes[idx])
    expr = '+'.join(notes)
    # print(f'Evaluating "{expr}"')
    return eval(expr)


ACCIDENTALS_TO_SCALE = {
    7: '^B ^C ^^C ^D ^^D ^E ^F ^^F ^G ^^G ^A =B',
    6: '^B ^C ^^C ^D =E ^E ^F ^^F ^G ^^G ^A B',
    5: '^B ^C ^^C ^D E ^E ^F ^^F ^G =A ^A B',
    4: '^B ^C =D ^D E ^E ^F ^^F ^G A ^A B',
    3: '^B ^C D ^D E ^E ^F =G ^G A ^A B',
    2: '=C ^C D ^D E ^E ^F G ^G A ^A B',
    1: 'C ^C D ^D E =F ^F G ^G A ^A B',
    0: 'C ^C D ^D E F ^F G ^G A _B =B',
    -1: 'C ^C D _E =E F ^F G ^G A _B =B',
    -2: 'C ^C D _E =E F ^F G _A =A _B =B',
    -3: 'C _D =D _E =E F ^F G _A =A _B =B',
    -4: 'C _D =D _E =E F _G =G _A =A _B =B',
    -5: '=C _D =D _E =E F _G =G _A =A _B _C',
    -6: '=C _D =D _E _F =F _G =G _A =A _B _C',
    -7: '=C _D =D _E _F =F _G =G _A __B _B _C', }


# TODO: eventually return a tuple note_on/note_off
def abc2midi(txt, accidentals=0, unit_note_length=Fraction(1, 4), time_signature=(4, 4)) -> mido.Message:
    """ txt is a single note in ABC notation [https://abcnotation.com/] """
    key = re.findall(r"[^_]*[A-G]", txt, flags=re.IGNORECASE)[0]  # eg C, ^D, __E
    octave_up = len(re.findall(r"'", txt))   # eg C''
    octave_down = len(re.findall(r",", txt))  # eg C,,
    try:
        pos = ACCIDENTALS_TO_SCALE[accidentals].split(' ').index(key.upper())
        octave = 4 + octave_up - octave_down
        octave = octave + 1 if key.islower() else octave  # it seems counterintuitive but it is how abc notations work
    except IndexError:
        raise ValueError('The key is not valid', key)
    return mido.Message(type='note_on', note=pos + 12 * (int(octave) + 1), time=(Fraction(abc2beatcount(txt)) * unit_note_length.denominator) / time_signature[1])


# TODO: dynamics2velocity
# https://en.wikipedia.org/wiki/Dynamics_(music)

# TODO: replace array of accidentals with key
def midi2abc(note: int, key_accidentals=[1, 0, 0, 0, 0, 0, 0], cur_accidentals=None) -> str:
    """check out https://github.com/jwdj/EasyABC/blob/master/midi2abc.py"""
    if cur_accidentals is None:
        cur_accidentals = key_accidentals[:]
    n_accidentals = sum(key_accidentals)
    accidentals_to_scale = {
        7: '^B ^C ^^C ^D ^^D ^E ^F ^^F ^G ^^G ^A =B',
        6: '^B ^C ^^C ^D =E ^E ^F ^^F ^G ^^G ^A B',
        5: '^B ^C ^^C ^D E ^E ^F ^^F ^G =A ^A B',
        4: '^B ^C =D ^D E ^E ^F ^^F ^G A ^A B',
        3: '^B ^C D ^D E ^E ^F =G ^G A ^A B',
        2: '=C ^C D ^D E ^E ^F G ^G A ^A B',
        1: 'C ^C D ^D E =F ^F G ^G A ^A B',
        0: 'C ^C D ^D E F ^F G ^G A _B =B',
        -1: 'C ^C D _E =E F ^F G ^G A _B =B',
        -2: 'C ^C D _E =E F ^F G _A =A _B =B',
        -3: 'C _D =D _E =E F ^F G _A =A _B =B',
        -4: 'C _D =D _E =E F _G =G _A =A _B =B',
        -5: '=C _D =D _E =E F _G =G _A =A _B _C',
        -6: '=C _D =D _E _F =F _G =G _A =A _B _C',
        -7: '=C _D =D _E _F =F _G =G _A __B _B _C', }

    scale = accidentals_to_scale[n_accidentals].split()
    notes = [n.lower().translate(str.maketrans('', '', '_=^'))
             for n in scale]  # for semitone: the name of the note
    # for semitone: 0 if white key, -1 or -2 if flat, 1 or 2 if sharp
    accidentals = [n.count('^') - n.count('_') for n in scale]

    note_scale = 'CDEFGAB'
    MIDDLE_C = 60
    octave_note = (note - MIDDLE_C) % 12

    n = notes[octave_note].upper()
    accidental_num = accidentals[octave_note]
    accidental_string = ''
    scale_number = note_scale.index(n)
    if cur_accidentals[scale_number] != accidental_num:
        cur_accidentals[scale_number] = accidental_num
        accidental_string = {-1: '_', -2: '__',
                             0: '=', 1: '^', 2: '^^'}[accidental_num]

    octave = (note - MIDDLE_C) // 12

    # handle the border cases of Cb and B# to make sure that we use the right octave
    if octave_note == 11 and accidental_num == -1:
        octave += 1
    elif octave_note == 0 and accidental_num == 1:
        octave -= 1

    if octave > 0:
        if octave >= 1:
            n = n.lower()
        if octave > 1:
            n = n + "'" * int(octave - 1)
    elif octave < 0:
        if abs(octave) >= 1:
            n = n + "," * abs(octave)
    return accidental_string + n
