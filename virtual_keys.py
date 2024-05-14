import keyboard
import mido

KEY_MAP = {
    30: 60,  # A -> C4
    17: 61,  # W -> C#4
    31: 62,  # S -> D4
    18: 63,  # E -> D#4
    32: 64,  # D -> E4
    33: 65,  # F -> F4
    20: 66,  # T -> F#4
    34: 67,  # G -> G4
    21: 68,  # Y -> G#4
    35: 69,  # H -> A4
    22: 70,  # U -> A#4
    36: 71,  # J -> B4
    37: 72,  # K -> C5
    38: 74,
}


def key_callback(key_event):
    try:
        note = KEY_MAP[key_event.scan_code]
        port.send(mido.Message('note_on' if key_event.event_type == 'down' else 'note_off', note=note))
    except KeyError:
        print("Scan code for unknown event:", key_event.scan_code)
        print("Event type:", key_event.event_type)


# open first available port
port = mido.open_output(mido.get_output_names()[0])
keyboard.hook(key_callback, suppress=True)

# Block forever, so that the program won't automatically finish,
# preventing you from typing and seeing the printed output
keyboard.wait('ctrl+c')
