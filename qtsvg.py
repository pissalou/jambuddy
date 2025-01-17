from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import sys
import time

curr_color = 'red'
next_color = 'green'
svg_data = '<svg height="100" width="100" xmlns="http://www.w3.org/2000/svg"><circle r="45" cx="50" cy="50" fill="red"/></svg>'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # svg_data = Path('Zeichen_123.svg').read_text()
    svgWidget = QSvgWidget()
    svgWidget.renderer().load(bytearray(svg_data, encoding='UTF-8'))
    svgWidget.setGeometry(50, 50, 100, 100)
    svgWidget.show()
    # print("show")
    prevtime = time.time()

    def toggle_color():
        global curr_color
        global next_color
        global prevtime
        global svg_data
        svg_data = svg_data.replace(curr_color, next_color)
        svgWidget.renderer().load(bytearray(svg_data, encoding='UTF-8'))
        svgWidget.update()
        currtime = time.time()
        # print(f"update {curr_color}->{next_color} @ {currtime - prevtime}")
        prevtime = currtime
        temp_color = next_color; next_color = curr_color; curr_color = temp_color  # the old switcheroo
        QTimer.singleShot(500, lambda: toggle_color())  # recurse every .5 sec
    #  time.sleep(1)  # cannot block the main thread when using Qt
    QTimer.singleShot(500, lambda: toggle_color())

    sys.exit(app.exec())
