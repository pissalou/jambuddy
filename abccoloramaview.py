import threading
import signal
import time
import sys
import re
from colorama import Fore, Back, Style
from abcutils import abc2beatcount
import globals as state

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
SHARP = Fore.RED
FLAT = Fore.BLUE

interrupt_event = threading.Event()


class AbcColoramaView(threading.Thread):
    """prints melody notes and cursor instead of playing them"""

    def __init__(self, melody, bpm=120, start_position=0, stop_position=-1, repeat=0):
        """
        :param melody: one measure of the melody, it will be printed TODO: support more than one measure, validate measure is complete
        :param start_position: position relative to the start of the melody in melody_track in number of beats (TODO midi beats?) 0-based or 1-based?
        :param stop_position: position relative to the start of the melody in melody_track in number of beats (TODO midi beats?)  0-based or 1-based?
        """
        threading.Thread.__init__(self)
        self.melody = melody[:]
        self.bps = 60 / bpm  # make bpm argument a callable
        self.start_position = start_position
        self.stop_position = stop_position
        self.repeat = repeat

    def run(self):
        # start_time = time.time()
        note_count = len(self.melody) * 2  # TODO line_length is what we need
        notes = re.sub(r'\d*/*\d+', '', ' '.join(self.melody) + ' ')
        notes = re.sub(r'[\^_]', r'', notes)  # for now, we just remove any sharp or flat
        beats = '1 & 2 & 3 & 4 & '
        rpadlen = 2
        for repeatcnt in range(0, self.repeat + 1):
            for idx, note in enumerate(self.melody):
                note_duration = abc2beatcount(note) * (60 / state.current_bpm)
                idx = idx % note_count
                print(beats[0:idx * rpadlen] + Back.RESET + beats[idx * rpadlen] + Back.RESET)  # + beats[idx + 1:])
                # print(''.join(cursor_range[0:idx]) + cursor(idx) + ''.join(cursor_range[idx + 1:]))
                print(notes[0:idx * rpadlen] + Back.GREEN + notes[idx * rpadlen] + Back.RESET + notes[idx * rpadlen + 1:])
                sys.stdout.flush()
                if note_duration > 0.0 and (repeatcnt != 0 or idx > self.start_position):
                    time.sleep(note_duration)
                print(LINE_UP, end=LINE_CLEAR)
                # print(LINE_UP, end=LINE_CLEAR)
                print(LINE_UP, end=LINE_CLEAR)
                sys.stdout.flush()
                if interrupt_event.is_set():
                    exit(1)


if __name__ == '__main__':
    abc = AbcColoramaView(["E/2", "E/2", "^F/2", "E/2", "G/2", "E/2", "A/2", "^G/2"], bpm=58, start_position=2, repeat=12)
    # abc = AbcColoramaView(["E/2", "E/2", "^F/2", "E/2", "G/4", "^G/4", "E/2", "A/2", "^G/2"], bpm=76)
    signal.signal(signal.SIGINT, lambda signum, _: interrupt_event.set())  # IMPORTANT: does not work on windows
    abc.start()
    abc.join(timeout=1000)
