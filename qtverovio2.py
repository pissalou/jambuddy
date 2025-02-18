import sys
from typing import Any
import mido
from PySide6 import QtWebEngineWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from abc2svg_utils import abc2svg
from qtimerutils import precise_timer
from xmlutils import foreach_node

global port  # midi out port


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
        print(str((beatcnt % 4) + 1), end='' if beatcnt % 4 != 3 else '\n')
        # metronome.click(bell=(beatcnt % 4 == 3))
        port.send(mido.Message('note_off', note=34 if beatcnt % 4 == 3 else 32, channel=9))
        port.send(mido.Message('note_on', note=34 if beatcnt % 4 == 0 else 32, channel=9))
        # TODO: see how verovio online editor is solving this
        self.svg = foreach_node(self.svg, "/svg//g[@class='note']//*[not(child::*)]",
                                lambda node: node.remove_attribute('class'))
        self.svg = foreach_node(self.svg, f"/svg//g[@class='note'][{(beatcnt % 4) + 1}]//*[not(child::*)]",
                                lambda node: node.append_attribute('class').set_value('active'))
        # TODO: in update perhaps?
        self.svg_view.setContent(bytearray(self.svg, encoding='UTF-8'), mimeType='image/svg+xml')
        self.svg_view.update()
        ##########################
        precise_timer(self, 500, lambda: self._update_beat(beatcnt + 1))  # TODO: DRY


if __name__ == "__main__":
    app = QApplication()
    main_window = JambudWindow()
    port = mido.open_output(mido.get_output_names()[0])
    # main_window.load_svg(Path('verovio-output.svg').read_bytes())
    main_window.load_abc(sys.argv[1] if len(sys.argv) > 1 else 'ABcd')
    # main_window.load_abc('AB[ceg]d') # TODO support chords
    main_window.animate(500)  # TODO support midi_tempo
    # TODO: enable_midi_playback
    # TODO: enable_midi_metronome
    main_window.show()
    sys.exit(app.exec())
