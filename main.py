import threading
# TODO rename file main.py
import mido
from midiplayback import MidiPlayback
from performance import PerformanceTracker
from abccoloramaview import AbcColoramaView
import state


# IMPORTANT plug a midi keyboard at this point
print(f'Output devices: {mido.get_output_names()}')
port_out = mido.open_output(mido.get_output_names()[-1])
print(f'Input devices: {mido.get_input_names()}')
port_in = mido.open_input(mido.get_input_names()[0])


mid = MidiPlayback("C:\\Users\\mazars\\Downloads\\The Blues Brothers-Peter Gunn Theme.mid", melody_track=1, start_position=1)  # beat #2 is position 1
# melody = ["E/2", "E/2", "^F/2", "E/2", "G/4", "^G/4", "E/2", "A/2", "^G/2"]
# melody = ["E/2", "E/2", "E/2", "E/2"]  # Super simplified melody
melody = ["E/2", "E/2", "^F/2", "E/2", "G/2", "E/2", "A/2", "^G/2"]  # Simplified melody
view = AbcColoramaView(melody, start_position=1, repeat=24)  # beat #2 is position 1


def playback():
    for msg in mid.play():
        port_out.send(msg)


def midi_message_received_callback(self: PerformanceTracker):
    if self.melody_note_idx == 3 and not self.playback_started:
        self.playback_started = True
        view.start()
        playback_thread = threading.Thread(target=playback)
        playback_thread.start()


performance_tracker = PerformanceTracker(expected_melody=melody, tempo_bpm=state.current_bpm, port_in=port_in, port_out=port_out, midi_message_received_callback=midi_message_received_callback)
performance_tracker.start()
