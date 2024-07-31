import logging
import threading
import keyboard
import mido
import os
from midiplayback import MidiPlayback
from performance import PerformanceTracker
from abccoloramaview import AbcColoramaView
import state
from state import barrier

# IMPORTANT plug a midi keyboard at this point
print(f'Output devices: {mido.get_output_names()}')
port_out = mido.open_output(mido.get_output_names()[-1])
print(f'Input devices: {mido.get_input_names()}')
port_in = mido.open_input(mido.get_input_names()[0]) if len(mido.get_input_names()) else None

logger = logging.getLogger(__name__)


mid = MidiPlayback("test/The Blues Brothers-Peter Gunn Theme.mid", melody_track=1, start_position=1)  # beat #2 is position 1
# melody = ["E/2", "E/2", "^F/2", "E/2", "G/4", "^G/4", "E/2", "A/2", "^G/2"]
# melody = ["E/2", "E/2", "E/2", "E/2", "E/2", "E/2", "E/2", "E/2"]  # Super simplified melody
melody = ["E/2", "E/2", "^F/2", "E/2", "G/2", "E/2", "A/2", "^G/2"]  # Simplified melody
view = AbcColoramaView(melody, start_position=2, repeat=19)  # 3rd beat is position 2


def playback():
    global barrier
    absolute_time = 3840 + 480  # from _first_note_times + one beat
    prev_abs_time = -1
    for msg in mid.play(meta_messages=True):
        # TODO avoid all this converting from tick to seconds and back
        absolute_time += msg.time  # mido.second2tick(msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=mido.bpm2tempo(state.current_bpm))
        # absolute_time = round(absolute_time / 120) * 120  # quantize
        logger.debug(f'tick {absolute_time}')
        if absolute_time % (mid.ticks_per_beat * 4) == 0 and absolute_time != prev_abs_time:
            logger.debug(f"waiting on tick {absolute_time} - measure {absolute_time / (mid.ticks_per_beat * 4)}")
            barrier.wait()  # TODO: set a timeout equivalent to the permitted tempo deviation for example
            prev_abs_time = absolute_time
        logger.debug('-> %s', msg)
        if not isinstance(msg, mido.MetaMessage):
            logger.debug('-> %s', msg)
            port_out.send(msg)


def midi_message_received_callback(self: PerformanceTracker):
    if self.melody_note_idx == 3 and not self.playback_started:
        self.playback_started = True
        view.daemon = True
        view.start()
        playback_thread = threading.Thread(target=playback)
        playback_thread.start()


keyboard.add_hotkey('ctrl+c', lambda: os._exit(0))
performance_tracker = PerformanceTracker(expected_melody=melody, tempo_bpm=state.current_bpm, port_in=port_in, port_out=port_out, midi_message_received_callback=midi_message_received_callback)
performance_tracker.daemon = True
performance_tracker.start()
performance_tracker.join()
view.join()
