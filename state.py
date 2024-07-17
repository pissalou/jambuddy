# TODO rename to state because of name collision
# global current_bpm, time_signature, song_position_pointer
current_bpm = 120
time_signature = (4, 4)
song_position_pointer = 0  # in 1/16th notes since the first note aka 'midi beats'
# TODO: search for SONGPOS in mido project
#  TODO: more song metadata like title, key etc...


class State:
    _bpm = 120

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
