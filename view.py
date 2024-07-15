import time
import sys
import re
import colorama
from colorama import Fore, Back, Style

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
SHARP = Fore.RED
FLAT = Fore.BLUE
# melody = ["E/2", "E/2", "^F/2", "E/2", "G/4", "^G/4", "E/2", "A/2", "^G/2"]
melody = ["E/2", "E/2", "^F/2", "E/2", "G/2", "E/2", "A/2", "^G/2"]
note_count = len(melody) * 2  # TODO line_length is what we need
notes = re.sub(r'\d*/*\d+', '', ' '.join(melody) + ' ')
# notes = re.sub(r'\^(\w)', SHARP + r'\1' + Fore.RESET, notes) # TODO: handle sharps,flats,accidentals
# notes = re.sub(r'_(\w)', FLAT + r'\1' + Fore.RESET, notes)
notes = re.sub(r'[\^_]', r'', notes)  # for now, we just remove any sharp or flat
beats = '1 & 2 & 3 & 4 & '
# cursor_range = [' '] * len(notes)
loop = range(0, note_count * 10)


def highlight(text):
    return "\033[1;40m" + "\033[1;97m" + str(text) + "\033[1;m" + "\033[1;m"


def cursor(index):
    if index % 4 == 0:
        return '|'
    elif index % 4 == 2:
        return '.'
    return ' '


colorama.init()
# print(Fore.RED + 'some red text')
# print(Back.GREEN + 'and with a green background')
# print(Style.DIM + 'and in dim text')
# print(Style.RESET_ALL + 'back to normal now')
for idx in loop:
    idx = idx % note_count
    print(beats[0:idx] + Back.RESET + beats[idx] + Back.RESET)  # + beats[idx + 1:])
    # print(''.join(cursor_range[0:idx]) + cursor(idx) + ''.join(cursor_range[idx + 1:]))
    print(notes[0:idx] + Back.GREEN + notes[idx] + Back.RESET + notes[idx + 1:])
    sys.stdout.flush()
    time.sleep(.15)
    print(LINE_UP, end=LINE_CLEAR)
    # print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)
    sys.stdout.flush()
