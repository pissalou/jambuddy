from collections import deque
import keyboard
import mido
import threading
from mido import MidiFile, Message, MetaMessage, tick2second, bpm2tempo, tempo2bpm
from time import gmtime, strftime, time

KEY_MAP = {
    57: 'play/pause',  # Space bar -> Play/pause
    72: 'incr_pitch',  # Arrow Up -> Pitch +6.25 cents
    75: 'decr_tempo',  # Arrow Left -> Tempo -5 bpm
    77: 'incr_tempo',  # Arrow Right -> Tempo +5 bpm
    80: 'decr_pitch',  # Arrow Down -> Pitch -6.25 cents
    20: 'tap_tempo'   # letter T -> Tap tempo from the latest 2 taps
}

current_bpm = 120
current_pitch = 0
tap_events = deque(maxlen=3)
TAP_RESET_AFTER_MS = 1200


class TimeStretchableMidiFile(MidiFile):

    def __iter__(self):
        global current_bpm
        absolute_time = 0
        for msg in self.merged_track:
            # Convert message time from absolute time in ticks to relative time in seconds.
            if msg.time > 0:
                delta = tick2second(msg.time, self.ticks_per_beat, bpm2tempo(current_bpm))
            else:
                delta = 0
            absolute_time += msg.time
            print('\r%5.2f' % (absolute_time / self.ticks_per_beat), end='')
            yield msg.copy(skip_checks=True, time=delta)
            # yield MetaMessage(**vars(msg)) if msg.is_meta else Message(**(vars(msg) | {'data': absolute_time}))

            if msg.type == 'set_tempo':
                current_bpm = tempo2bpm(msg.tempo)

    def play_from_beat(self, beat=1, meta_messages=False, now=time):
        idx = 1
        for idx, msg in enumerate(self):
            # if hasattr(msg, 'data') and msg.data > ((beat - 1) / (current_bpm / 60)):
            if msg.absolute_time > ((beat - 1) / (current_bpm / 60)):
                return
        self._merged_track = self._merged_track[idx - 1:]
        return self.play(meta_messages=meta_messages, now=now)


port = mido.open_output(mido.get_output_names()[-1])
mid = TimeStretchableMidiFile('test/mozk331c.mid', debug=False)
meta_msgs = [msg for msg in list(mid) if msg.is_meta]
print('Track Name: ' + [meta_msg.name for meta_msg in meta_msgs if meta_msg.type == 'track_name'][0])
print('BPM: ' + str(mido.tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])))
time_signature = [meta_msg for meta_msg in meta_msgs if meta_msg.type == 'time_signature'][0]
print('Signature: ' + str(time_signature.numerator) + '/' + str(time_signature.denominator))
print('Playback duration: ' + strftime("%M:%S", gmtime(mid.length)))
# Initialize some variables
current_pitch = 0  # standard concert pitch 440Hz
current_bpm = mido.tempo2bpm([meta_msg.tempo for meta_msg in meta_msgs if meta_msg.type == 'set_tempo'][0])


def key_callback(key_event):
    global current_pitch
    global current_bpm
    try:
        if key_event.event_type == 'down':
            key_action = KEY_MAP[key_event.scan_code]
            if key_action == 'play/pause':
                keyboard.wait(57)
            if key_action == 'tap_tempo':
                now = time()
                if len(tap_events) == 0 or (1000 * (now - tap_events[-1])) < TAP_RESET_AFTER_MS:
                    tap_events.append(now)
                if len(tap_events) == tap_events.maxlen:
                    current_bpm = 60 / (((tap_events[2] - tap_events[1]) + (tap_events[1] - tap_events[0])) / 2)
            elif key_action == 'incr_pitch':
                port.send(mido.Message('pitchwheel', pitch=max(-8192, min(current_pitch + round(4096 / 32), 8191))))
                current_pitch = max(-8192, min(current_pitch + round(4096 / 32), 8191))
            elif key_action == 'decr_pitch':
                port.send(mido.Message('pitchwheel', pitch=max(-8192, min(current_pitch + round(4096 / 32), 8191))))
                current_pitch = max(-8192, min(current_pitch - round(4096 / 32), 8191))
            elif key_action == 'incr_tempo':
                current_bpm = max(10, min(current_bpm + 5, 250))
            elif key_action == 'decr_tempo':
                current_bpm = max(10, min(current_bpm - 5, 250))
            print("Current pitch:", current_pitch)
            print("Current BPM:", current_bpm)
    except KeyError:
        print("Scan code:", key_event.scan_code)
        print("Event type:", key_event.event_type)


keyboard.hook(key_callback, suppress=True)
keyboard_input_thread = threading.Thread(target=keyboard.wait, args=('ctrl+c',))
keyboard_input_thread.start()
# mid.print_tracks()
# mid.tracks[0].clear()
mid._merged_track = mido.merge_tracks(mid.tracks[1:2])  # keep only Track no. 1
# mid._merged_track = mid._merged_track[int(len(mid._merged_track)/2):]  # TODO: start at beat
for msg in mid.play():
    port.send(msg)
port.close()
keyboard_input_thread.join()
