import mido
import sys


class MidiDebug(mido.MidiFile):
    def __init__(self, filename, filter_msgtype=None, filter_ticks=(0, sys.maxsize)):
        """
        :param filename: the name of the midifile
        """
        super().__init__(filename)
        self.delta = 0
        self.tempo = 500000  # default tempo in microseconds per beat (quarter note).
        self.filter_msgtype = filter_msgtype
        self.filter_ticks = filter_ticks

    def __iter__(self):
        for msg in self.merged_track:
            # Convert message time from absolute time
            # in ticks to relative time in seconds.
            if msg.time > 0:
                self.delta += msg.time
            if (self.filter_msgtype is None or msg.type in self.filter_msgtype) and self.filter_ticks[0] < self.delta < self.filter_ticks[1]:
                yield msg.copy(skip_checks=True, time=self.delta)
            if msg.type == 'set_tempo':
                self.tempo = msg.tempo


# Print midi events with absolute time
start = 13200 - 240
stop = 13680 - 240
mid = MidiDebug('.\\test\\The Blues Brothers-Peter Gunn Theme.mid', filter_ticks=(start, stop))
# TODO solve the problem with 2 tracks having the same channel
mid.print_tracks(meta_only=True)
for msg in mid:
    print(f'{msg!r}')
