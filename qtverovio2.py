import sys
from typing import Optional
from threading import Thread
import mido
from PySide6 import QtWebEngineWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from abcutils import abc2midi
from abc2svg_utils import abc2svg
from qtimerutils import precise_timer
from xmlutils import foreach_node
import ticker

global midi_in_port
global midi_out_port


class JambudWindow(QMainWindow):
    svg_view: QtWebEngineWidgets.QWebEngineView
    svg: str  # store xml doc instead?

    def __init__(self):
        """ """
        super().__init__()
        super().setWindowTitle('Visual MIDI Player [bpm=120]')
        self.svg_view = QtWebEngineWidgets.QWebEngineView()
        scaling_factor = 5
        self.svg_view.setGeometry(0, 0, 210 * scaling_factor, 297 * scaling_factor)
        self.setCentralWidget(self.svg_view)

    def load_svg(self, data: bytes):
        self.svg = data.decode('utf-8')
        self.svg_view.setContent(data, mimeType='image/svg+xml')

    def load_abc(self, abc: str):
        self.load_svg(abc2svg(abc))

    def animate(self, msec: int):
        """ show active beat
         :msec the refresh rate
         """
        precise_timer(self, msec, lambda: self._update_beat(0))

    def _update_beat(self, beatcnt: int):
        # print(str((beatcnt % 4) + 1), end='' if beatcnt % 4 != 3 else '\n')
        # metronome.click(bell=(beatcnt % 4 == 3))
        midi_out_port.send(mido.Message('note_off', note=34 if beatcnt % 4 == 3 else 32, channel=9))
        midi_out_port.send(mido.Message('note_on', note=34 if beatcnt % 4 == 0 else 32, channel=9))
        # TODO: see how verovio online editor is solving this
        self.svg = foreach_node(self.svg, "/svg//g[@class='note']//*[not(child::*)]",
                                lambda node: node.remove_attribute('class'))
        self.svg = foreach_node(self.svg, f"/svg//g[@class='note'][{(beatcnt % 4) + 1}]//*[not(child::*)]",
                                lambda node: node.append_attribute('class').set_value('active'))
        # TODO: in update perhaps?
        self.svg_view.setContent(bytearray(self.svg, encoding='UTF-8'), mimeType='image/svg+xml')
        self.svg_view.update()
        # print(ticker.get_ticks())
        ##########################
        precise_timer(self, 500, lambda: self._update_beat(beatcnt + 1))  # TODO: DRY


def midi_event_listener(abc_melody: str, tempo: int = 500000):  # midi_tempo in us per quarter note
    print(f"Listening on {midi_in_port}..." if midi_in_port is not None else "Unable to listen: no input MIDI device detected")
    previous_note = None
    while True:
        idx: int = int(ticker.get_ticks() / 480) % 4  # TODO how to calculate 480
        expected_note = abc_melody[idx]
        expected_midi: mido.Message = abc2midi(expected_note)
        if expected_note != previous_note:
            print(f"Expecting {expected_note} (#{expected_midi.note})...", end="\n")
            previous_note = expected_note
        if midi_in_port is not None:
            msg: mido.Message = midi_in_port.receive()
            print(f"Received {msg.note} " + ("\u2705" if expected_midi.note == msg.note else "\u274C"))


if __name__ == "__main__":
    app = QApplication()
    main_window = JambudWindow()
    midi_in_port: Optional[mido.ports.BaseInput] = mido.open_input(mido.get_input_names()[0]) if len(mido.get_input_names()) > 0 else None
    midi_out_port = mido.open_output(mido.get_output_names()[0])
    print(f"MIDI output device: {midi_out_port.name}")
    # main_window.load_svg(Path('verovio-output.svg').read_bytes())
    abc_melody = sys.argv[1] if len(sys.argv) > 1 else 'ABcd'
    main_window.load_abc(abc_melody)
    ticker_thread = Thread(target=ticker.increment_ticks)
    listener = Thread(target=midi_event_listener, kwargs={'abc_melody': abc_melody})
    listener.daemon = True
    listener.start()
    ticker_thread.daemon = True
    ticker_thread.start()
    # main_window.load_abc('AB[ceg]d') # TODO support chords
    main_window.animate(500)  # TODO support midi_tempo
    # TODO: enable_midi_playback
    # TODO: enable_midi_metronome
    main_window.show()
    # listener.join(); ticker_thread.join() # where to join?
    sys.exit(app.exec())
