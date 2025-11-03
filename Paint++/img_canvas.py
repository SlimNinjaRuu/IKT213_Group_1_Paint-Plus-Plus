# imports different classes from the PyQt library
from PyQt6 import QtGui
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QPen, QImage, QGuiApplication
from PyQt6.QtCore import Qt, QPoint, QSize, QRect, pyqtSignal, pyqtSlot, QBuffer, QByteArray, QIODevice, QMimeData
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QMainWindow,
    QLabel,
    QCheckBox,
    QStatusBar,
    QToolBar, QStyle, QFileDialog, QMessageBox, QScrollArea, QInputDialog
)

from numpy.ma.core import reshape

TRANSPARENT = QColor(0, 0, 0, 0)


##### Inhertis from Qwidget ######
class Img_Canvas(QWidget):
    historyChanged = pyqtSignal(bool, bool) # undo, redo - for enabling/disabling action



    def __init__(self, parent=None):
        super().__init__(parent)


        self.image: QPixmap | None = None                                       # No image loaded yet - Hodls QPixmap (image data)
        self._checker = self.make_checker_brush(tile=16)        # Background Pattern
        self.offset = QPoint(0, 0)                              # Sets the position of the image (for panning)
        self.panning = False                                    # Is the image being dragged, Boolean value
        self.last_pos = None                                    # Last Mouse position

        self._undo_stack: list[QPixmap] = []                    # Undo function
        self._redo_stack: list[QPixmap] = []
        self._max_undos = 20                                    # Can undo back 20 times

        self.selected = False
        self.handle_size = 8
        self.dragging_handle = None
        self.resize_start_size = None
        self.resize_start_pos = None

        self.zoom_scale = 1.0


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
        self.zoom_scale = 1.0

        if self.image is not None and not self.image.isNull():

            self.setMinimumSize(self.image.size())

            if self.image.width() > self.width() or self.image.height() > self.height():
                self.resize(self.image.size())                      # Resize Widget to prefferd size

        self.update()                                           # Redraw to show new image

    def pixmap(self):
        """Return the currently displayed QPixmap."""
        return self.image if self.image is not None and not self.image.isNull() else None

    def zoom_in(self):
        self.zoom_scale *= 1.25
        self.update()

    def zoom_out(self):
        self.zoom_scale *= 0.8
        self.update()

    def reset_zoom(self):
        self.zoom_scale = 1.0
        self.update()

    def get_zoom_percent(self):
        return int(self.zoom_scale * 100)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self._checker)

        if self.image is None or self.image.isNull():
            return

        # Scale dimensions
        scaled_width = int(self.image.width() * self.zoom_scale)
        scaled_height = int(self.image.height() * self.zoom_scale)

        # Center using scaled size
        x = (self.width() - scaled_width) / 2
        y = (self.height() - scaled_height) / 2

        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())

        # Draw image scaled
        p.drawPixmap(xi, yi, scaled_width, scaled_height, self.image)

        # Border
        p.setPen(QPen(QColor("#000000") if self.selected else QColor("#888888"),
                      3 if self.selected else 1))
        p.drawRect(xi, yi, scaled_width - 1, scaled_height - 1)

    def sizeHint(self):
        if self.image is not None:
            return self.image.size()
        return QSize(800, 600)


    ##### Mouse Press (Start Dragging) #####
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.image is None or self.image.isNull():
                return

            click_pos = event.position().toPoint()

            # On-screen rect of scaled image
            scaled_w = int(self.image.width() * self.zoom_scale)
            scaled_h = int(self.image.height() * self.zoom_scale)
            x = (self.width() - scaled_w) / 2
            y = (self.height() - scaled_h) / 2
            xi = int(x + self.offset.x())
            yi = int(y + self.offset.y())
            image_rect = QRect(xi, yi, scaled_w, scaled_h)

            if image_rect.contains(click_pos):
                self.selected = True
                self.panning = True
                self.last_pos = click_pos
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.update()
            else:
                self.selected = False
                self.update()

    # Change cursor to hand


    ##### Mouse movement while dragging #####
    def mouseMoveEvent(self, event):
        if self.panning and self.last_pos is not None:

            pos = event.position().toPoint()                    # Current mouse position
            delta = pos - self.last_pos                         # The Change in mouse position
            self.offset += delta                                # Move the image by that amount
            self.last_pos = pos                                 # Update for next frame
            self.update()                                       # Trigger paintEvent to redraw, handled by Qt's Event loop


    ##### Mouse Release (stop dragging) #####
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False                                # Stop Panning mode
            self.last_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)          # Change back to normal cursor


    ##### Allows User to Change he canvas Size
    def resize_canvas(self):

        width, ok1 = QInputDialog.getInt(self, "Canvas Width", "Enter Width", 800, 100, 5000 )
        if not ok1:     # User Clicked cancel
            return

        height, ok2 = QInputDialog.getInt(self, "Canvas Height", "Enter Height", 800, 100, 5000 )
        if not ok2:     # User Clicked Cancel
            return

        # undo snapshot before change
        self.mark_state()

        # create a new transparent pixmap and blit old content
        new_pm = QPixmap(width, height)
        new_pm.fill(TRANSPARENT)

        if self.image and not self.image.isNull():
            p = QPainter(new_pm)
            # draw existing image at 0,0 (or compute centered coords if you prefer)
            p.drawPixmap(0, 0, self.image)
            p.end()

        self.image = new_pm
        self.setMinimumSize(self.image.size())
        self.resize(self.image.size())
        self.update()

    ##### Convert QImage to Numpy array for OpenCV
    def qimage_to_numpy(qimage: QImage):
        """Convert QImage (any) to numpy BGR (OpenCV)."""
        qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(qimage.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        # RGBA -> BGR
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        return bgr

    def numpy_to_qimage(arr: np.ndarray) -> QImage:
        """Convert numpy BGR (OpenCV) to QImage RGB888."""
        rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return q_img.copy()

    def _push_undo(self):
        """Save a snapshot of the current image into the undo stack."""
        if isinstance(self.image, QPixmap) and not self.image.isNull():
            if len(self._undo_stack) >= self._max_undos:
                self._undo_stack.pop(0)
            self._undo_stack.append(self.image.copy())

        # modify the image (open, draw, paste, cut)

    def mark_state(self):
        """Call this RIGHT BEFORE any change to self.image pixels."""
        self._push_undo()
        self._redo_stack.clear()
        self.historyChanged.emit(bool(self._undo_stack), bool(self._redo_stack))

    def reset_history(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.historyChanged.emit(False, False)


    def undo(self):
        if not self._undo_stack:
            return
        current = self.image.copy() if self.image and not self.image.isNull() else None
        self.image = self._undo_stack.pop()
        if current is not None:
            self._redo_stack.append(current)
        self.update()
        self.historyChanged.emit(bool(self._undo_stack), bool(self._redo_stack))

    def redo(self):
        if not self._redo_stack:
            return
        current = self.image.copy() if self.image and not self.image.isNull() else None
        self.image = self._redo_stack.pop()
        if current is not None:
            self._undo_stack.append(current)
        self.update()
        self.historyChanged.emit(bool(self._undo_stack), bool(self._redo_stack))

    # Clipboard dunction
    def copy_to_clipboard(self):
        if self.image and not self.image.isNull():
            QGuiApplication.clipboard().setImage(self.image.toImage().copy())

    def paste_from_clipboard(self):
        cb = QGuiApplication.clipboard()
        md = cb.mimeData()

        # Prefer image (most robust on Windows), fallback to pixmap
        pix = None
        if md and md.hasImage():
            img = cb.image()  # QImage
            if not img.isNull():
                pix = QPixmap.fromImage(img)
        if pix is None or pix.isNull():
            p2 = cb.pixmap()
            if not p2.isNull():
                pix = p2

        if pix is None or pix.isNull():
            return

        self.mark_state()

        if self.image is None or self.image.isNull():
            self.image = pix.copy()
        else:
            p = QPainter(self.image)
            p.drawPixmap(0, 0, pix)
            p.end()

        self.update()

    def cut_to_clipboard(self):
        if not self.image or self.image.isNull():
            return

        self.mark_state()

        # Put PNG bytes on the clipboard (no shared buffers)
        img_copy = self.image.toImage().copy()
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img_copy.save(buf, b"PNG")
        buf.close()
        md = QMimeData()
        md.setData("image/png", ba)
        QGuiApplication.clipboard().setMimeData(md)

        # Replace canvas with a fresh transparent pixmap (same size)
        size = self.image.size()
        new_pm = QPixmap(size.width(), size.height())
        new_pm.fill(TRANSPARENT)  # <— use the constant here
        self.image = new_pm

        self.update()



