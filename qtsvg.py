from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from pugixml import pugi
import mido
import sys
import time

doc = pugi.XMLDocument()
svg_data = ('<svg width="400" height="100" xmlns="http://www.w3.org/2000/svg">'
            '<style type="text/css">circle { fill: "dimgray" } circle.active { fill: "green" }</style>'
            '<circle r="45" cx="050" cy="50" class="active" />'
            '<circle r="45" cx="150" cy="50" />'
            '<circle r="45" cx="250" cy="50" />'
            '<circle r="45" cx="350" cy="50" />'
            '</svg>')


def precise_timer(parent, msec: int, functor):
    timer = QTimer(parent)
    timer.setTimerType(Qt.PreciseTimer)
    timer.timeout.connect(functor)
    timer.setSingleShot(True)
    timer.start(msec)


if __name__ == "__main__":
    global port
    port = mido.open_output(mido.get_output_names()[0])
    app = QApplication(sys.argv)
    # svg_data = Path('Zeichen_123.svg').read_text()
    svgWidget = QSvgWidget()
    svgWidget.setWindowTitle('Visual Metronome [bpm=120]')
    svgWidget.renderer().load(bytearray(svg_data, encoding='UTF-8'))
    svgWidget.setGeometry(0, 0, 400, 100)
    svgWidget.show()
    # print("show")
    prevtime = time.time()
    beatcnt = 0

    def update_beat():
        global beatcnt
        global prevtime
        global svg_data
        global port

        port.send(mido.Message('note_off', note=34 if beatcnt % 4 == 3 else 32, channel=9))
        port.send(mido.Message('note_on', note=34 if beatcnt % 4 == 0 else 32, channel=9))
        # svg_data = svg_data.replace("active", "passive")
        result = doc.load_string(svg_data)
        if result.status == pugi.STATUS_OK:
            [elem.node().remove_attribute('class') for elem in doc.select_nodes(f"/svg/circle")]  # reset active class
            doc.select_node(f"/svg/circle[{(beatcnt  % 4) + 1}]").node().append_attribute('class').set_value('active')
            xml_writer = pugi.StringWriter()
            doc.save(writer=xml_writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF8)
            svg_data = xml_writer.getvalue()
            beatcnt = beatcnt+1
        else:
            exit(123)

        svgWidget.renderer().load(bytearray(svg_data, encoding='UTF-8'))
        svgWidget.update()
        currtime = time.time()
        # print(f"beat {beatcnt} [duration={(currtime - prevtime):0.4f}ms]")
        prevtime = currtime
        # QTimer.singleShot(500, lambda: update_beat())  # recurse every .5 sec
        precise_timer(app, 500, lambda: update_beat())
    # time.sleep(1)  # cannot block the main thread when using Qt
    # QTimer.singleShot(500, lambda: update_beat())
    precise_timer(app, 500, lambda: update_beat())

    sys.exit(app.exec())
