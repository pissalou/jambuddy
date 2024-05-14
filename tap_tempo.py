import keyboard
import time
from collections import deque


tap_events = deque(maxlen=3)
TAP_RESET_AFTER_MS = 1200


def key_callback(key_event):
    try:
        if key_event.event_type == 'down':
            now = time.time()
            if len(tap_events) == 0 or (1000 * (now - tap_events[-1])) < TAP_RESET_AFTER_MS:
                tap_events.append(now)
            else:
                tap_events.clear()  # reset the tap event buffer
            if len(tap_events) == tap_events.maxlen:
                print('\rTap tempo: %f' % (60 / (((tap_events[2] - tap_events[1]) + (tap_events[1] - tap_events[0])) / 2)), end='')
            else:
                print('\rTap tempo:', end='')
    except KeyError:
        print("Scan code:", key_event.scan_code)
        print("Event type:", key_event.event_type)


keyboard.hook(key_callback, suppress=True)
print('\rTap tempo:', end='')

# Block forever, so that the program won't automatically finish,
# preventing you from typing and seeing the printed output
keyboard.wait('ctrl+c')
