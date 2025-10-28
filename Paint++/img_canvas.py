
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


##### Inhertis from Qwidget ######

class Img_Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None                                       # No image loaded yet - Hodls QPixmap (image data)
        self._checker = self.make_checker_brush(tile=16)        # Background Pattern
        self.offset = QPoint(0, 0)                              # Sets the position of the image (for panning)
        self.panning = False                                    # Is the image being dragged, Boolean value
        self.Last_pos = None                                    # Last Mouse position



    def make_checker_brush(self, tile=16):
        light = QColor("#eeeeee")
        dark = QColor("#bbbbbb")

        pm = QPixmap(tile * 2, tile * 2)                        # Creates a 32x32 pixel image
        pm.fill(light)

        p = QPainter(pm)
        p.fillRect(0, tile, tile, tile, dark)                   # Bottom left square
        p.fillRect(tile, 0, tile, tile, dark)                   # Top right Square
        p.end()

        return QBrush(pm)


    ##### Loading Images #####
    def set_image(self, pix):

        self.image = pix                                        # Store the new image
        self.offset = QPoint(0, 0)                              # Reset to center
        self.resize(self.image.size())                          # Resize Widget to prefferd size
        self.update()                                           # Redraw to show new image


    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self._checker)                  # Draw Checkerd Background

        if self.image is None:                                  # Exits the method if there is no image
            return

        # Calculates where to draw the image so it is centered
        x = (self.width() - self.image.width()) / 2
        y = (self.height() - self.image.height()) / 2

        # Where the image drawn after the users dragged it (self.offset)
        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())
        p.drawPixmap(xi, yi, self.image)                        # Draws the image with DrawPixmap

        # Draw border around the image
        p.setPen(QColor("#888888"))
        p.drawRect(xi, yi, self.image.width()-1, self.image.height()-1)


    def sizeHint(self):
        if self.image is not None:
            return self.image.size()
        return QSize(800, 600)


    ##### Mouse Press (Start Dragging) #####
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = True                                 # Start Panning mode
            self.Last_pos = event.position().toPoint()          # Remember where we clicked
            self.setCursor(Qt.CursorShape.ClosedHandCursor)     # Change cursor to hand


    ##### Mouse movement while dragging #####
    def mouseMoveEvent(self, event):
        if self.panning and self.Last_pos is not None:

            pos = event.position().toPoint()                    # Current mouse position
            delta = pos - self.Last_pos                         # The Change in mouse position
            self.offset += delta                                # Move the image by that amount
            self.Last_pos = pos                                 # Update for next frame
            self.update()                                       # Trigger paintEvent to redraw, handled by Qt's Event loop


    ##### Mouse Release (stop dragging) #####
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False                                # Stop Panning mode
            self.Last_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)          # Change back to normal cursor

