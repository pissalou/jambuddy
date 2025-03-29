from PySide6 import QtWebEngineWidgets
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from pugixml import pugi
import mido
import verovio
import sys
import time

tk = verovio.toolkit()
tk.setScale(75)
doc = pugi.XMLDocument()
tk.loadData("""X:1
T:Simple tune
M:4/4
L:1/4
K:C
|:ABcd:|]""")
svg_data = tk.renderToSVG(1)  # abc2svg
doc.load_string(svg_data)
css = doc.select_node("/svg/style").node().text().get()
css += ' .active{ fill:red; stroke: red;}'
print(css)
doc.select_node("/svg/style").node().text().set(css)
xml_writer = pugi.StringWriter()
doc.save(writer=xml_writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF8)
svg_data = xml_writer.getvalue()


def precise_timer(parent, msec: int, functor):
    timer = QTimer(parent)
    timer.setTimerType(Qt.PreciseTimer)
    timer.timeout.connect(functor)
    timer.setSingleShot(True)
    timer.start(msec)


# filename = 'verovio-temp.svg'
if __name__ == "__main__":
    global port
    port = mido.open_output(mido.get_output_names()[0])
    app = QApplication(sys.argv)
    # svg_data = Path('Zeichen_123.svg').read_text()
    svg_view = QtWebEngineWidgets.QWebEngineView()
    svg_view.setWindowTitle('Visual MIDI Player [bpm=120]')
    # print(f"Loading SVG data {svg_data[:65]}...")
    # svgWidget.renderer().load(bytearray(svg_data, encoding='UTF-8'))
    svg_view.setContent(bytearray(svg_data, encoding='UTF-8'), mimeType='image/svg+xml')
    # svgWidget.renderer().load(filename)
    scaling_factor = 2
    svg_view.setGeometry(0, 0, 210*scaling_factor, 297*scaling_factor)
    svg_view.show()
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
        # svgWidget.renderer().load(filename)
        # result = doc.load_string(svg_data)
        print('.', end='')
        result = doc.load_string(svg_data)
        # result = type('obj2dict', (object,), {"status": pugi.STATUS_OK})
        # if result.status == pugi.STATUS_OK:
        # print(len(doc.select_nodes(f"/svg//g[@class='note'][{beatcnt + 1}]")), end='')
        [elem.node().remove_attribute('class') for elem in doc.select_nodes("/svg//g[@class='note']//*[not(child::*)]")]  # reset active class
        for leaf_elem in doc.select_nodes(f"/svg//g[@class='note' or @class='chord'][{(beatcnt % 4) + 1}]//*[not(child::*)]"):
            # print(leaf_elem.node().name())
            leaf_elem.node().append_attribute('class').set_value('active')
            # leaf_elem.node().append_attribute('fill').set_value('red')
            # leaf_elem.node().attribute('stroke').set_value('red')
        xml_writer = pugi.StringWriter()
        doc.save(writer=xml_writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF8)
        svg_data = xml_writer.getvalue()
        # print(svg_data)
        beatcnt = beatcnt + 1
        # else:
        #     exit(123)

        svg_view.setContent(bytearray(svg_data, encoding='UTF-8'), mimeType='image/svg+xml')
        # svgWidget.renderer().load(bytearray(svg_data, encoding='UTF-8'))
        # svg_view.reload()
        svg_view.update()
        currtime = time.time()
        # print(f"beat {beatcnt} [duration={(currtime - prevtime):0.4f}ms]")
        prevtime = currtime
        # QTimer.singleShot(500, lambda: update_beat())  # recurse every .5 sec
        precise_timer(app, 500, lambda: update_beat())
    # time.sleep(1)  # cannot block the main thread when using Qt
    # QTimer.singleShot(500, lambda: update_beat())
    precise_timer(app, 500, lambda: update_beat())

    sys.exit(app.exec())
