import re
import time
from threading import Event, Lock, Thread
from colorama import Fore, Back, Style
from mido import bpm2tempo, second2tick, tick2second
from abcutils import abc2beatcount, measure_to_beats

# create an event to shut down all running tasks
playback_stop_event = Event()

# create a lock to protect tick counter
lock = Lock()

melody = ["E/2", "E/2", "^F/2", "E/2", "G/2", "E/2", "A/2", "^G/2"]
bpm = 118.0
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
WHITESPACE = ' '
HIDE_CURSOR_SIGN = '\033[?25l'


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


def print_staff(melody: list, refresh_rate: int = ppqn, repeat: int = 0, start_position: int = 0):
    """
    Prints a transport clock, bpm, beat counter and melody as such:
    1.1.00 bpm: 118.0
    |1
    |A B C D :|
    :param melody: the melody to print in an ABC-formatted note list
    :param refresh_rate: how often we should reprint the staff (0 or negative means no refresh)
    :param repeat: how many times the melody is repeated (0 or negative means play just once)
    :param start_position: which beat to start the highlight on (0 or negative means first beat)
    """
    notes = re.sub(r'\d*/*\d+', '', ' '.join(melody) + ' ')
    notes = re.sub(r'[\^_]', r'', notes)  # for now, we just remove any sharp or flat
    # shortest_note_length =  1/2  # TODO find shortest note length from melody
    beats = measure_to_beats(melody)  # TODO rename beat_chant, TODO: melody needs to be 1 measure only
    rpadlen = 2
    repeatcnt = -1
    idx = 0
    print(HIDE_CURSOR_SIGN, end='')
    while repeatcnt < repeat or (repeatcnt == repeat and idx <= len(melody)):
        repeatcnt = int(ticks / tpqn / 4)  # TODO: what if the melody is multiple measures?
        idx = (int(2 * ticks / tpqn) % len(melody))  # 2 is the melody time subdivision , also = 1 / shortest_note_length
        # print(f"idx={idx}", end="")
        if playback_stop_event.is_set():
            return
        print(f'{int(ticks / tpqn / 4) + 1}.{(int(ticks / tpqn) % 4) + 1}.{int((ticks % 480) / ticks_per_pulse):02d} bpm: {bpm:05.1f} \n'
              + BAR_LINE + beats[0:idx * rpadlen] + Back.RESET + beats[idx * rpadlen] + Back.RESET + WHITESPACE * (len(beats) - idx * rpadlen - 1) + "\n"
              + BAR_LINE + notes[0:idx * rpadlen] + Back.GREEN + notes[idx * rpadlen] + Back.RESET + notes[idx * rpadlen + 1:] + (REPEAT_SIGN * (repeat - repeatcnt)) + BAR_LINE)
        if refresh_rate > 0:
            time.sleep(tick2second(tpqn / refresh_rate, 480, bpm2tempo(bpm)))
            print(LINE_UP + LINE_UP + LINE_UP, end=LINE_CLEAR)
        else:
            break


if __name__ == "__main__":
    ticker = Thread(target=increment_ticks)
    ticker.daemon = True
    ticker.start()

    staff_printer = Thread(target=print_staff, kwargs={'melody': melody, 'refresh_rate': 24, 'repeat': 12, 'start_position': 0})
    staff_printer.daemon = True
    staff_printer.start()
    time.sleep(25)
    print('\nStopping playback...')
    playback_stop_event.set()
    ticker.join(timeout=0)
    staff_printer.join(timeout=1)
    # print('Restarting playback...')
    # playback_stop_event.clear()
