import mido
import time


NOTE_METRONOME_CLICK = 32
NOTE_METRONOME_BELL = 34
CHANNEL_PERCUSSION = 9
port = mido.open_output(mido.get_output_names()[0])


def play_beat(bpm, beatnumber, total_beats=4):
    port.send(mido.Message('note_off', note=NOTE_METRONOME_CLICK, channel=CHANNEL_PERCUSSION))
    print(f'\rPlaying {beatnumber + 1}/{total_beats}', end='')
    port.send(mido.Message('note_on', note=NOTE_METRONOME_CLICK, channel=CHANNEL_PERCUSSION))
    time.sleep(60 / bpm)


tempo = 120
time_signature = (4, 4)
beat_cnt = 0
total_beats = time_signature[0]
while True:
    play_beat(tempo, beat_cnt, total_beats)
    beat_cnt = (beat_cnt + 1) % total_beats
