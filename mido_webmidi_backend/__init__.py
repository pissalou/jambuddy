import sys
from mido.ports import BaseInput, BaseOutput, BasePort
from mido.backends._parser_queue import ParserQueue

if sys.platform != 'emscripten':
    raise OSError('This backend is only available in a browser')
try:
    import js
except ImportError as e:
    raise RuntimeError(e.msg if "pyodide" in sys.modules else "Pyodide not found in modules")


_midiaccess = None
async def init():
    def onmidiaccesssuccess(midiaccess):
        print(f'Received midi access {midiaccess}. It is available in JS via globalThis.__midiAccess and in Python via mido.backend.module._midiaccess')
        js.globalThis.__midiAccess = midiaccess
        global _midiaccess
        _midiaccess = midiaccess

    if js.navigator.requestMIDIAccess:
        print('Requesting MIDI access...')
        await js.navigator.requestMIDIAccess().then(onmidiaccesssuccess, lambda: print('MIDI support rejected, MIDI will not be available'))


class PortCommon(BasePort):
    """
    Mixin with common things for input and output ports.
    """

    def __init__(self, name, **kwargs):
        print(f'Opening port {name}({kwargs})...')
        self.portinfo = [device for device in get_devices() if device['name'] == name][0]

    def _open(self, **kwargs):
        if kwargs.get('virtual'):
            raise ValueError('virtual ports are not supported')
        elif kwargs.get('callback'):
            raise ValueError('callbacks are not supported')
        print(f'Opening port {self.portinfo["name"]} with kwargs {kwargs}...')
        if self.portinfo['is_input']:
            global _midiaccess
            self.port = _midiaccess.inputs.get(self.portinfo['id'])
            self._queue = ParserQueue()  # for storing msgs between calls to Input.receive()
            def onmidimessage(msg_bytes: [int]):
                print(f'Received msg {msg_bytes}@{type(msg_bytes)}...')
                self._queue.put_bytes(msg_bytes)
                print(f'Enqueued msg into {self._queue}.')
            self.port.onmidimessage = lambda msg: onmidimessage(msg.data)
        self.closed = False

    def _receive(self, block=True):
        if block:
            return self._queue.get()
        else:
            return self._queue.poll()

    def _poll(self):
        return self._queue.poll()

    async def _close(self):
        del self._queue


class Input(PortCommon, BaseInput):
    def __init__(self, name,  **kwargs):
        PortCommon.__init__(self, name, **kwargs)
        BaseInput.__init__(self, name, **kwargs)


class Output(PortCommon, BaseOutput):
    def _send(self, msg):
        self.midiport.send(msg)


def get_devices(**kwargs):
    """Return a list of devices as dictionaries."""
    while not js.globalThis.hasOwnProperty('__midiAccess'):
        print('Wait for MIDI access...')
        init()
    if js.globalThis.hasOwnProperty('__midiAccess'):
        _midiaccess = js.globalThis.__midiAccess
        inputs = [{'id': port.id, 'name': port.name, 'manufacturer': port.manufacturer, 'state': port.state,
                   'connection': port.connection, 'is_input': True, 'is_output': False } for port in _midiaccess.inputs.values()]
        outputs = [{'id': port.id, 'name': port.name, 'manufacturer': port.manufacturer, 'state': port.state,
                    'connection': port.connection, 'is_input': False, 'is_output': True } for port in _midiaccess.outputs.values()]
        results = inputs
        results.extend(outputs)
        # print(f'Devices found: {results}')
        return results
    print('No MIDI access. Returning empty device list')
    return []
    # minimal working example result
    # return [{
    #    'name': 'Some MIDI Input Port',
    #    'is_input': True,
    #    'is_output': False,
    # }]


# import * is broken unless we explicitly define `__all__`
#  __all__ = ['get_devices', 'Input', 'Output']