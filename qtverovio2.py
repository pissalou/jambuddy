import dataclasses
import sys
from typing import Optional, List
from threading import Thread
import mido
from PySide6 import QtWebEngineWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PySide6.QtCore import Qt
from abcutils import abc2midi
from abc2svg_utils import abc2svg
from qtimerutils import precise_timer
from xmlutils import foreach_node
import ticker

global midi_in_port
global midi_out_port
predelay = 240  # number of ticks performance be will be tracking early notes
time_stretch_factor = 1  # debugging option: slow down


@dataclasses.dataclass
class TrackedNote:  # TODO: just store mido.Message perhaps?
    abc_note: str
    timestamp: int  # in ticks
    played: bool = False


global performance_tracker  # expected midi events

performance_tracker: List[TrackedNote] = [TrackedNote('A', timestamp=0), TrackedNote('B', timestamp=480), TrackedNote('c', timestamp=960), TrackedNote('d', timestamp=1440)]


def reset_performance(exclude: int):
    for idx, note in enumerate(performance_tracker):
        if idx != exclude:
            note.played = False


class JambudWindow(QMainWindow):
    svg_view: QtWebEngineWidgets.QWebEngineView
    svg: str  # store xml doc instead?

    def __init__(self):
        """ """
        super().__init__()
        super().setWindowTitle('Jambuddy [bpm=120]')
        self.svg_view = QtWebEngineWidgets.QWebEngineView()
        scaling_factor = 5
        self.svg_view.setGeometry(0, 0, 600, 240)  # 210 * scaling_factor, 297 * scaling_factor)
        self.setCentralWidget(self.svg_view)
        self.transport = QDockWidget("Transport", self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.transport)

    def load_svg(self, data: bytes):
        self.svg = data.decode('utf-8')
        self.svg_view.setContent(data, mimeType='image/svg+xml')

    def load_abc(self, abc: str):
        self.load_svg(abc2svg(abc))

    def animate(self, msec: int):
        """ show active beat
         :msec the refresh rate
         """
        precise_timer(self, msec, lambda: self.update())

    previous_beatcnt: int = -1

    def update(self, _=None):
        beatcnt: int = int(ticker.get_ticks() / 480) % 4  # TODO how to calculate 480
        # print(str((beatcnt % 4) + 1), end='' if beatcnt % 4 != 3 else '\n')
        # metronome.click(bell=(beatcnt % 4 == 3))
        if beatcnt != self.previous_beatcnt:
            self.previous_beatcnt = beatcnt
            midi_out_port.send(mido.Message('note_off', note=34 if beatcnt % 4 == 3 else 32, channel=9))
            midi_out_port.send(mido.Message('note_on', note=34 if beatcnt % 4 == 0 else 32, channel=9))
            # reset_performance(exclude=beatcnt)
        # TODO: see how verovio online editor is solving this
        self.svg = foreach_node(self.svg, "/svg//g[@class='note']//*[not(child::*)]",
                                lambda node: node.remove_attribute('class'))
        class_value = 'active played' if performance_tracker[beatcnt % 4].played else 'active'
        self.svg = foreach_node(self.svg, f"/svg//g[@class='note'][{(beatcnt % 4) + 1}]//*[not(child::*)]",
                                lambda node: node.append_attribute('class').set_value(class_value))
        self.svg_view.setContent(bytearray(self.svg, encoding='UTF-8'), mimeType='image/svg+xml')
        self.svg_view.update()
        # print(ticker.get_ticks())
        ##########################
        self.transport.setWindowTitle(ticker.ticks2transport(ticker.get_ticks()))
        precise_timer(self, 21 * time_stretch_factor, lambda: self.update())  # TODO: how to calculate refresh_rate 21ms


def midi_event_listener(abc_melody: str):
    print(f"Listening on {midi_in_port}..." if midi_in_port is not None else "Unable to listen: no input MIDI device detected")
    previous_note = None
    previous_ticks = 0
    while True:
        ticks = ticker.get_ticks()
        melody_idx: int = int(ticks / 480) % 4  # TODO how to calculate 480? TODO predelay
        print(f"{ticker.transport()}")
        if ticks != previous_ticks:
            # print(f"{ticks} ticks -> beat#{melody_idx + 1}")
            previous_ticks = ticks
        expected_note = abc_melody[melody_idx]
        if expected_note != previous_note:
            #while (ticks % (4 * 480)) < performance_tracker[melody_idx].timestamp - predelay:
            #    pass
            previous_note = expected_note
            print(f" Expecting {expected_note}...")
            expected_midi: mido.Message = abc2midi(expected_note)
        if midi_in_port is not None:
            msg: mido.Message = midi_in_port.receive(block=True)
            if msg.type == 'note_off':
                continue  # we just skip to the next loop iteration
            msg.time = ticks
            is_expected_note = expected_midi.note == msg.note
            is_note_on = msg.type == 'note_on'
            print(f" Received {msg} " + ("\u2705" if is_expected_note else "\u274C"))
            if is_expected_note:
                performance_tracker[melody_idx].played = is_note_on


if __name__ == "__main__":
    app = QApplication()
    main_window = JambudWindow()
    midi_in_port: Optional[mido.ports.BaseInput] = mido.open_input(mido.get_input_names()[0]) if len(mido.get_input_names()) > 0 else None
    midi_out_port = mido.open_output(mido.get_output_names()[0])
    print(f"MIDI output device: {midi_out_port.name}")
    # main_window.load_svg(Path('verovio-output.svg').read_bytes())
    abc_melody = sys.argv[1] if len(sys.argv) > 1 else 'ABcd'
    main_window.load_abc(abc_melody)
    ticker.bpm = 120 / time_stretch_factor
    ticker_thread = Thread(target=ticker.increment_ticks)
    listener = Thread(target=midi_event_listener, kwargs={'abc_melody': abc_melody})
    listener.daemon = True
    listener.start()
    ticker_thread.daemon = True
    ticker_thread.start()
    # main_window.load_abc('AB[ceg]d') # TODO support chords
    main_window.animate(0 * time_stretch_factor)  # TODO support midi_tempo
    # TODO: enable_midi_playback
    # TODO: enable_midi_metronome
    main_window.show()
    # listener.join(); ticker_thread.join() # where to join?
    sys.exit(app.exec())
