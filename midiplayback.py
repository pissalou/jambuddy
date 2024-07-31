from mido import MidiFile, MidiTrack, MetaMessage, tick2second, bpm2tempo, tempo2bpm, merge_tracks
import sys
import state
from clock import highres_sleep as sleep

def _first_note_time(track: MidiTrack):
    absolute_time = 0  # in ticks
    for msg in track:
        absolute_time += msg.time  # accumulate all the delta until the first note is reached
        if not msg.is_meta and msg.type == 'note_on':
            return absolute_time


class MidiPlayback(MidiFile):

    def __init__(self, filename, melody_track=0, start_position=0, stop_position=-1):
        """
        :param filename: the name of the midifile
        :param melody_track: the index of the track to use for melody reference, it will be muted during playback
        :param start_position: position relative to the start of the melody in melody_track in number of beats (TODO midi beats?) 0-based or 1-based?
        :param stop_position: position relative to the start of the melody in melody_track in number of beats (TODO midi beats?)  0-based or 1-based?
        """
        super().__init__(filename)
        self._merged_track = merge_tracks(self.tracks[:melody_track] + self.tracks[melody_track + 1:])  # mute the melody_track
        # ticks_per_beat is the same as PPQ pulse per quarter-note
        first_note_time = _first_note_time(self.tracks[melody_track])
        self.start_position = (start_position * self.ticks_per_beat) + first_note_time
        self.stop_position = (stop_position * self.ticks_per_beat) + first_note_time if stop_position > start_position else sys.maxsize
        # self.original_bpm = midiutils.extract_bpm(self)

    def __iter__(self):
        absolute_time = 0
        first_note_encountered = False
        for msg in self.merged_track:
            absolute_time += msg.time
            if absolute_time < self.start_position:  # in ticks
                continue  # skip to next iteration
            if absolute_time >= self.stop_position:
                return
            if absolute_time >= self.start_position and not first_note_encountered:
                msg.time = self.start_position - absolute_time  # recalculate delta from start pos instead of previous note
                first_note_encountered = True
            # Convert message time from absolute time in ticks to relative time in seconds.
            # if msg.time > 0:
            #     delta = tick2second(msg.time, self.ticks_per_beat, bpm2tempo(state.current_bpm))
            # else:
            #     delta = 0
            # print('\r%5.2f'% (absolute_time / self.ticks_per_beat), end='')
            yield msg.copy(skip_checks=True)
            # yield MetaMessage(**vars(msg)) if msg.is_meta else Message(**(vars(msg) | {'data': absolute_time}))

            # TODO: support tempo changes relative to the current tempo
            # if msg.type == 'set_tempo':
            #     current_bpm = tempo2bpm(msg.tempo)

    def play(self, meta_messages=False, now=lambda: 0):
        start_time = now()
        input_time = 0.0

        for msg in self:
            input_time += msg.time

            playback_time = now() - start_time
            duration_to_next_event = input_time - playback_time

            if duration_to_next_event > 0.0:
                sleep(tick2second(msg.time, self.ticks_per_beat, bpm2tempo(state.current_bpm)))

            if isinstance(msg, MetaMessage) and not meta_messages:
                continue
            else:
                yield msg
