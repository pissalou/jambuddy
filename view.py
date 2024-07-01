import time

notes = 'E E F E G E A G '
cursor = [' '] * len(notes)
loop = range(0, len(notes))

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'


def highlight(text):
    return "\033[1;40m" + "\033[1;97m" + str(text) + "\033[1;m" + "\033[1;m"


for idx in loop:
    print(''.join(cursor[0:idx]) + '|' + ''.join(cursor[idx + 1:]))
    print(notes[0:idx] + notes[idx] + notes[idx + 1:])
    time.sleep(.25)
    print(LINE_UP, end=LINE_CLEAR)
    print(LINE_UP, end=LINE_CLEAR)
