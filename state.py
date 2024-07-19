import contextlib


# TODO rename to state because of name collision
# global current_bpm, time_signature, song_position_pointer
current_bpm: float = 120.0  # TODO not assume a default tempo, perhaps float is unnecessary
time_signature = (4, 4)
song_position_pointer = 0  # in 1/16th notes since the first note aka 'midi beats'
# TODO: search for SONGPOS in mido project
#  TODO: more song metadata like title, key etc...


@contextlib.contextmanager
def constant_bpm(bpm):
    """
    For testing purpose
    :param bpm: the bpm under test
    :return: the value from the input
    """
    global current_bpm
    old_bpm = None
    try:
        old_bpm = current_bpm
        current_bpm = bpm
        yield bpm
    finally:
        current_bpm = old_bpm


class State:
    _bpm = 120  # TODO not assume a default tempo

    @property
    def bpm(self):
        return self.get_bpm()

    def get_bpm(self):
        return self._bpm

    @bpm.setter
    def bpm(self, value):
        self.set_bpm(value)

    def set_bpm(self, value):
        if 15 < value < 300:
            self._bpm = value
        else:
            raise ValueError(f'Trying to set BPM outside of [15-300]: {value}')


current = State()

if __name__ == '__main__':
    current.bpm = 123
    print(current.get_bpm.__call__())
