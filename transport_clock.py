import datetime
import io
import sys
import threading
import time


def second2beat(second, bpm):
    return (second * bpm) / 60


def beat2second(beat, bpm):
    return beat / (bpm / 60)


class TransportClock(threading.Thread):
    def __init__(self, bpm=120, time_signature=(4, 4)):
        self.bpm = bpm
        self.beats_per_measure = time_signature[0] * (time_signature[1] / 4)
        self.beats = 0  # zero-based in the code, one-based when printing
        self._start = None
        threading.Thread.__init__(self)

    def run(self):
        self._start = time.time()
        while True:
            # print('\r%d.%3.2f' % (self.beats / 4 + 1, self.beats % 4 + 1), end='')
            # sys.stdout.flush()
            # self.beats += second2beat(time.time() - self._start, self.bpm)
            time_passed = time.time() - self._start
            # print('\r' + datetime.datetime.fromtimestamp(time_passed).strftime('%M:%S.%f'), end='')
            # sys.stdout = io.TextIOWrapper(open(sys.stdout.fileno(), 'wb+', 0), write_through=True)
            # print('\r%3.f' % (time_passed * 2), end='')
            beats = second2beat(time_passed, self.bpm)
            sys.stdout.write('\r%d:%.2f' % ((beats / self.beats_per_measure) + 1, (beats % self.beats_per_measure) + 1))
            # sys.stdout.write('\r%f' % beat2second(beats, self.bpm))
            sys.stdout.flush()


tc = TransportClock(120, time_signature=(4, 4))
tc.daemon = True
tc.start()
while True:
    time.sleep(10)  # wait forever
