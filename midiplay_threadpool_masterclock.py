import time
from time import sleep
from threading import Event, Lock, Thread
from concurrent.futures import ThreadPoolExecutor
from mido import MidiFile, MidiTrack, MetaMessage
import mido

# create an event to shut down all running tasks
playback_stop_event = Event()

# create a lock to protect tick counter
lock = Lock()

mid = MidiFile("test/The Blues Brothers-Peter Gunn Theme.mid")
bpm = 116
ppqn = 24  # pulses per quarter-note
tpqn = 480  # ticks per quarter-note
ticks_per_pulse = tpqn / ppqn
port = mido.open_output(mido.get_output_names()[-1])
print(f'Opening {port.name}....')
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
        print(f'\r{int(ticks / tpqn / 4) + 1}.{(int(ticks / tpqn) % 4) + 1}.{int((ticks % 480) / ticks_per_pulse):02d}', end='')


ticker = Thread(target=increment_ticks)
ticker.daemon = True
ticker.start()


# play each track on a separate thread
def play_track(midi_track: MidiTrack, meta_messages: bool = False):
    print(f'Playing track "{midi_track.name}" [{len(midi_track)}]...')
    tickcnt = 0
    for msg in midi_track:
        # check the status of the flag
        if playback_stop_event.is_set():
            return
        ticks_to_next_event = msg.time
        tickcnt += msg.time
        if ticks_to_next_event > 0:
            time.sleep(mido.tick2second(0.999 * ticks_to_next_event, mid.ticks_per_beat, bpm))
            while get_ticks() < tickcnt:
                # print('z', end='\r')
                time.sleep(0)
        if not isinstance(msg, MetaMessage):
            # print(msg)
            port.send(msg)  # sending a meta message will fail


def playback_exec_pool():
    executor = ThreadPoolExecutor(len(mid.tracks))
    executor.map(play_track, mid.tracks)
    executor.shutdown(wait=True)


jam_band = Thread(target=playback_exec_pool)
jam_band.daemon = True
jam_band.start()
sleep(10)
print('\nStopping playback...')
playback_stop_event.set()
port.panic()
ticker.join(timeout=0)
jam_band.join(timeout=1)
# print('Restarting playback...')
# playback_stop_event.clear()
