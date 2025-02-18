from PySide6.QtCore import QTimer, Qt
from typing import Callable


def precise_timer(parent, msec: int, functor: Callable):
    timer = QTimer(parent)
    timer.setTimerType(Qt.PreciseTimer)
    timer.timeout.connect(functor)
    timer.setSingleShot(True)
    timer.start(msec)
