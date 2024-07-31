import asyncio
import sys
import time
import mido

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'


def _midi_clock_generator(out_port, bpm, run):
    """
    a high-accuracy low-jitter clock for music: For lower beat per minute (bpm) values, sleep is used to not waste too much power.
    The processes sleeps for 80% of the target time, and then a while loop is used to check when the final time is reached.
    Taken from https://www.reddit.com/r/learnpython/comments/15k2kow/more_accurate_function_then_timesleep/.
    :param out_port:
    :param bpm:
    :param run:
    :return:
    """
    # print(f'__name__: {__name__}')
    midi_output = mido.open_output(out_port)
    clock_tick = mido.Message('clock')
    while run.value:
        pulse_rate = 60.0 / (bpm.value * 24)
        midi_output.send(clock_tick)
        t1 = time.perf_counter()
        if bpm.value <= 3000:
            time.sleep(pulse_rate * 0.8)  # sleep for 80% of the time
        t2 = time.perf_counter()
        while (t2 - t1) < pulse_rate:  # wait for time to expire
            t2 = time.perf_counter()


def highres_sleep(seconds: float):
    t1 = time.perf_counter()
    time.sleep(seconds * 0.8)  # sleep for 80% of the time
    t2 = time.perf_counter()
    while (t2 - t1) < seconds:  # wait for time to expire
        t2 = time.perf_counter()


async def asyncio_sleep(seconds: float):
    await asyncio.sleep(seconds)

# TODO: test with await asyncio.sleep(delay)

if __name__ == '__main__':
    bpm = 116
    while True:
        for beat in range(1, 5):
            print(LINE_CLEAR + str(beat), end='')
            sys.stdout.flush()
            # time.sleep(60 / bpm)
            # highres_sleep(60 / bpm)
            asyncio.run(asyncio_sleep(60 / bpm))
        print('', end=LINE_CLEAR)
