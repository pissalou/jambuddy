import re
import time
from threading import Event, Lock, Thread
from colorama import Fore, Back, Style
from mido import bpm2tempo, second2tick, tick2second
from abcutils import abc2beatcount

# create an event to shut down all running tasks
playback_stop_event = Event()

# create a lock to protect tick counter
lock = Lock()

melody = ["E/2", "E/2", "^F/2", "E/2", "G/2", "E/2", "A/2", "^G/2"]
bpm = 30
ppqn = 24  # pulses per quarter-note
tpqn = 480  # ticks per quarter-note
ticks_per_pulse = tpqn / ppqn
ticks = 0

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
SHARP = Fore.RED
FLAT = Fore.BLUE
BAR_LINE = '|'
REPEAT_SIGN = ':'


def get_ticks():
    global ticks
    return ticks


def increment_ticks():
    global ticks
    while True:
        if playback_stop_event.is_set():
            return
        time.sleep((60 / bpm) / 24)  # 0.021551724137931036
        with lock:
            ticks += 24
        # print(ticks)
        # print(f'\r{int(ticks / tpqn / 4) + 1}.{(int(ticks / tpqn) % 4) + 1}.{int((ticks % 480) / ticks_per_pulse):02d}', end='')


ticker = Thread(target=increment_ticks)
ticker.daemon = True
ticker.start()


def print_staff(melody: list, repeat: int = 0, start_position: int = 0):
    notes = re.sub(r'\d*/*\d+', '', ' '.join(melody) + ' ')
    notes = re.sub(r'[\^_]', r'', notes)  # for now, we just remove any sharp or flat
    beats = '1 & 2 & 3 & 4 & '
    rpadlen = 2
    tickcnt = 0
    for repeatcnt in range(0, repeat + 1):
        for idx, note in enumerate(melody):
            # print(f"idx={idx}", end="")
            if playback_stop_event.is_set():
                return
            print(BAR_LINE + beats[0:idx * rpadlen] + Back.RESET + beats[idx * rpadlen] + Back.RESET)  # + beats[idx + 1:])
            # print(''.join(cursor_range[0:idx]) + cursor(idx) + ''.join(cursor_range[idx + 1:]))
            print(BAR_LINE + notes[0:idx * rpadlen] + Back.GREEN + notes[idx * rpadlen] + Back.RESET + notes[idx * rpadlen + 1:] + (
                        REPEAT_SIGN * (repeat - repeatcnt)) + BAR_LINE)
            note_duration_sec = abc2beatcount(note) * (60 / bpm)
            tickcnt += second2tick(note_duration_sec, ticks_per_beat=480, tempo=bpm2tempo(bpm))
            if note_duration_sec > 0.0 and (repeatcnt != 0 or idx >= start_position):
                while get_ticks() < tickcnt:
                    # print(f'z {get_ticks()}', end='\r')
                    time.sleep(0)
            print(LINE_UP, end=LINE_CLEAR)
            print(LINE_UP, end=LINE_CLEAR)
            print(LINE_UP, end=LINE_CLEAR)
            print(f'\r{int(ticks / tpqn / 4) + 1}.{(int(ticks / tpqn) % 4) + 1}.{int((ticks % 480) / ticks_per_pulse):02d}', end=' ')
            print('bpm: %05.1f' % bpm)


staff_printer = Thread(target=print_staff, args=[melody, 12, 0])
staff_printer.daemon = True
staff_printer.start()
time.sleep(30)
print('\nStopping playback...')
playback_stop_event.set()
ticker.join(timeout=0)
staff_printer.join(timeout=1)
# print('Restarting playback...')
# playback_stop_event.clear()
