import sys
import types
import mido
import pytest
from importlib import reload
from unittest.mock import Mock


@pytest.fixture(scope='module')
def setup(monkeypatch):
    ...
    # monkeypatch.setattr(sys, 'platform', 'emscripten')
    # module = __import__('mido_webmidi_backend')
    # sys.modules['mido_webmidi_backend'] = module


def test_get_devices_none(monkeypatch):
    mock_js_module = types.ModuleType('mock_js')
    mock_js_module.navigator = Mock()
    mock_js_module.navigator.requestMIDIAccess.sideeffect = lambda success, error: None
    mock_js_module.globalThis = Mock()
    sys.modules['js'] = mock_js_module
    mock_js_module.globalThis.hasOwnProperty.sideeffet = lambda propname: True
    mock_midiaccess = Mock()
    mock_midiaccess.inputs.values.side_effect = lambda: []
    mock_midiaccess.outputs.values.side_effect = lambda: []
    # TODO rewrite this bit, we should not need to mock twice the same object
    monkeypatch.setattr(sys, 'platform', 'emscripten')
    import mido_webmidi_backend
    reload(mido_webmidi_backend)
    monkeypatch.setattr(mido_webmidi_backend, '_midiaccess', mock_midiaccess)
    mock_js_module.globalThis.__midiAccess = mock_midiaccess
    mido.set_backend('mido_webmidi_backend')
    assert mido.backend.module.__name__ == 'mido_webmidi_backend'
    assert mido.get_input_names() == []
    # mock_js_module.navigator.requestMIDIAccess.assert_called_once()


def test_get_devices_input_output_same_name(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'emscripten')
    mock_js_module = types.ModuleType('mock_js')
    mock_js_module.navigator = Mock()
    mock_js_module.navigator.requestMIDIAccess.sideeffect = lambda success, error: None
    mock_js_module.globalThis = Mock()
    mock_js_module.globalThis.hasOwnProperty.sideeffet = lambda propname: True
    sys.modules['js'] = mock_js_module
    mock_midiaccess = Mock()
    mock_midiaccess.inputs.values.side_effect = lambda: [type('MidiInput', (object,),
                                                              {'id': 'input-0',
                                                               'name': 'Oxygen 69',
                                                               'manufacturer': 'Midiwoman',
                                                               'state': 'disconnected',
                                                               'connection': 'closed'})]
    mock_midiaccess.outputs.values.side_effect = lambda: [type('MidiOutput', (object,),
                                                               {'id': 'output-0',
                                                                'name': 'Oxygen 69',
                                                                'manufacturer': 'Midiwoman',
                                                                'state': 'disconnected',
                                                                'connection': 'closed'})]
    # TODO rewrite this bit, we should not need to mock twice the same object
    monkeypatch.setattr(sys, 'platform', 'emscripten')
    import mido_webmidi_backend
    reload(mido_webmidi_backend)
    monkeypatch.setattr(mido_webmidi_backend, '_midiaccess', mock_midiaccess)
    mock_js_module.globalThis.__midiAccess = mock_midiaccess
    mido.set_backend('mido_webmidi_backend')
    assert len(mido_webmidi_backend.get_devices()) == 2
    assert mido.get_input_names() == ['Oxygen 69']
    assert mido.get_output_names() == ['Oxygen 69']
    assert mido.get_ioport_names() == ['Oxygen 69']


def test_open_input(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'emscripten')
    mock_js_module = types.ModuleType('mock_js')
    mock_js_module.navigator = Mock()
    mock_js_module.navigator.requestMIDIAccess.sideeffect = lambda success, error: None
    mock_js_module.globalThis = Mock()
    mock_js_module.globalThis.hasOwnProperty.sideeffet = lambda propname: True
    sys.modules['js'] = mock_js_module
    mock_midiaccess = Mock()
    mock_midiaccess.inputs.values.side_effect = lambda: [type('MidiInput', (object,),
                                                              {'id': 'input-0',
                                                               'name': 'Oxygen 69',
                                                               'manufacturer': 'Midiwoman',
                                                               'state': 'disconnected',
                                                               'connection': 'closed'})]
    mock_midiaccess.outputs.values.side_effect = lambda: [type('MidiOutput', (object,),
                                                               {'id': 'output-0',
                                                                'name': 'Oxygen 69',
                                                                'manufacturer': 'Midiwoman',
                                                                'state': 'disconnected',
                                                                'connection': 'closed'})]
    # TODO rewrite this bit, we should not need to mock twice the same object
    monkeypatch.setattr(sys, 'platform', 'emscripten')
    import mido_webmidi_backend
    reload(mido_webmidi_backend)
    monkeypatch.setattr(mido_webmidi_backend, '_midiaccess', mock_midiaccess)
    mock_js_module.globalThis.__midiAccess = mock_midiaccess
    mido.set_backend('mido_webmidi_backend')
    port = mido.open_input('Oxygen 69')
    assert port is not None
    assert port.is_input
    assert port.name == 'Oxygen 69'
    with pytest.raises(ValueError, match="a callback is set for this port"):
        port._check_callback()
    # raise OSError(f"{dir(port)}")
