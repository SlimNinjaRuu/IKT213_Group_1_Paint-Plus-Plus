
# imports different classes from the PyQt library
from PyQt6 import QtGui
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush
from PyQt6.QtCore import Qt, QPoint, QSize

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QMainWindow,
    QLabel,
    QCheckBox,
    QStatusBar,
    QToolBar, QStyle, QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.uic.Compiler.qtproxies import QtWidgets


# Creates the class for the canvas
class Img_Canvas(QWidget):

    # Initiates the canvas
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None
        self._checker = self.make_checker_brush(tile=16)

        self.offset = QPoint(0, 0)
        self.panning = False
        self.Last_pos = None

    def make_checker_brush(self, tile=16):
        light = QColor("#eeeeee")
        dark = QColor("#bbbbbb")

        pm = QPixmap(tile * 2, tile * 2)
        pm.fill(light)

        p = QPainter(pm)
        p.fillRect(0, tile, tile, tile, dark)
        p.fillRect(tile, 0, tile, tile, dark)
        p.end()

        return QBrush(pm)

    def set_image(self, pix):
        self.image = pix
        self.offset = QPoint(0, 0)
        self.resize(pix.size())
        self.update()
        print("[canvas] set_image:" , pix.size(), "null", pix.isNull())


    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self._checker)

        if self.image is None:
            return

        x = (self.width() - self.image.width()) / 2
        y = (self.height() - self.image.height()) / 2

        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())
        p.drawPixmap(xi, yi, self.image)

        p.setPen(QColor("#888888"))
        p.drawRect(xi, yi, self.image.width()-1, self.image.height()-1)


    def sizeHint(self):
        return QSize(800, 600)


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = True
            self.Last_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.panning and self.Last_pos is not None:
            pos = event.position().toPoint()
            delta = pos - self.Last_pos
            self.offset += delta
            self.Last_pos = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False
            self.Last_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

