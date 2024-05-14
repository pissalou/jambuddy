import mido
from mido.ports import MultiPort


midi_port_out = mido.open_output(mido.get_output_names()[0])
print(mido.get_input_names())

# multi = MultiPort(mido.get_input_names())
# for msg in multi:
#     print(msg)


with mido.open_input('TinyUSB Device 0') as midi_port_in:
    for msg in midi_port_in:
        print(msg)
        midi_port_out.send(msg)  # forward message to output
