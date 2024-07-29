import threading
import time
# Sync threads so they wait for each other before printing a newline
barrier = threading.Barrier(parties=2)
#########################################################
# static variables shared between Thread_A and Thread_B #
bpm = 120                                               #
beatcnt = 0                                             #
#########################################################


class BeatCounterThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global beatcnt, bpm, barrier   # use global here
        while True:
            print("%d" % ((beatcnt % 4) + 1), end='')
            time.sleep(60 / bpm)
            beatcnt = beatcnt + 1
            if beatcnt % 4 == 3:
                barrier.wait()


class TempoHastenerThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global bpm, barrier  # use global here
        while True:
            barrier.wait()
            print("")  # print new line
            time.sleep((4 * 60) / bpm)
            bpm = bpm + 5


a = BeatCounterThread("counting1to4")
b = TempoHastenerThread("increaseBpmWith5EveryMeasure")

b.start()
a.start()

a.join()
b.join()
