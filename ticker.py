import re
import time
from threading import Event, Lock, Thread

# create an event to shut down all running tasks
playback_stop_event = Event()

# create a lock to protect tick counter
lock = Lock()

bpm = 120  # TODO: configurable
ticks = 0


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
