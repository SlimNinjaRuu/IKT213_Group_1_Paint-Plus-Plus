# imports different classes from the PyQt library
from PyQt6 import QtGui
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QPen, QImage
from PyQt6.QtCore import Qt, QPoint, QSize, QRect
import cv2
from PyQt6 import QtCore
from PyQt6.QtCore import QRectF
import numpy as np
from image_menu_functions import imf
from SelectionTools import SelectionTools
from SelectionManager import SelectionManager

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


##### Inhertis from Qwidget ######
class Img_Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None                                       # No image loaded yet - Hodls QPixmap (image data)
        self._checker = self.make_checker_brush(tile=16)        # Background Pattern
        self.offset = QPoint(0, 0)                       # Sets the position of the image (for panning)
        self.panning = False                                    # Is the image being dragged, Boolean value
        self.Last_pos = None                                    # Last Mouse position

        self.selected = False
        self.handle_size = 8
        self.dragging_handle = None
        self.resize_start_size = None
        self.resize_start_pos = None

        self.zoom_scale = 1.0

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.sel_mode = "pan"
        self.rect_anchor = None                                 # Qpoint in image coordinates
        self.rect_current = None                                # Qpoint to image coordinate
        self.sel_active = False
        self.sel_frozen = False                                 # Selection is finalized with Enter
        self.sel_points = []

        self.sel_mgr = SelectionManager()                       # Selection state holder
        self.active_mask = None
        self.ops_since_freeze = False


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
        p.fillRect(self.rect(), self._checker)                  # Draw Checkerd Background

        if self.image is None:                                  # Exits the method if there is no image
            return

        scaled_width = int(self.image.width() * self.zoom_scale)
        scaled_height = int(self.image.height() * self.zoom_scale)

        # Calculates where to draw the image so it is centered
        x = (self.width() - scaled_width) / 2
        y = (self.height() - scaled_height) / 2

        # Where the image drawn after the users dragged it (self.offset)
        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())
        p.drawPixmap(xi, yi, scaled_width, scaled_height, self.image)                        # Draws the image with DrawPixmap

        # Draw border around the image
        if self.selected:
            p.setPen(QPen(QColor("#000000"), 3))
        else:
            p.setPen(QColor("#888888"))

        p.drawRect(xi, yi, scaled_width-1, scaled_height-1)

        if self.sel_active:
            selection_path = QtGui.QPainterPath()

            # Rectangle selection
            if self.sel_active and self.sel_mode == "rect" and self.rect_anchor and self.rect_current:
                a = self.rect_anchor
                b = self.rect_current

                x1, y1 = min(a.x(), b.x()), min(a.y(), b.y())
                x2, y2 = max(a.x(), b.x()), max(a.y(), b.y())

                tl = self.image_to_widget(QPoint(x1, y1))
                br = self.image_to_widget(QPoint(x2, y2))
                selection_path.addRect(QRectF(QRect(tl, br)))

            # Lasso/polygon selection
            elif self.sel_mode in ("lasso", "poly") and len(self.sel_points) >= 2:

                pts_w = [self.image_to_widget(p) for p in self.sel_points]

                path = QtGui.QPainterPath()
                path.moveTo(QtCore.QPointF(pts_w[0]))

                for q in pts_w[1:]:
                    path.lineTo(QtCore.QPointF(q))

                if self.sel_mode == "poly" and self.sel_frozen and len(pts_w) >= 3:
                    path.closeSubpath()

                selection_path.addPath(path)


            if not selection_path.isEmpty():
                overlay = QtGui.QPainterPath()
                overlay.addRect(QRectF(self.rect()))
                dimmed_area = overlay.subtracted(selection_path)

                p.fillPath(dimmed_area, QColor( 0, 0, 0, 80))
                p.setPen(QPen(QColor(255, 0, 0), 2))
                p.drawPath(selection_path)




    def sizeHint(self):
        if self.image is not None:
            return self.image.size()
        return QSize(800, 600)


    ##### Mouse Press (Start Dragging) #####
    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton and self.sel_active and self.sel_mode == "rect":
            if not self.sel_frozen:
                pos_w = event.position().toPoint()
                pos_i = self.widget_to_image(pos_w)

                if pos_i is not None:
                    self.rect_anchor = pos_i
                    self.rect_current = pos_i
                    self.sel_mgr.rect_start(pos_i.x(), pos_i.y())
                    self.update()
                return
        if event.button() == Qt.MouseButton.LeftButton and self.sel_active and self.sel_mode == "lasso":
            if not self.sel_frozen:
                pos_i = self.widget_to_image(event.position().toPoint())
                if pos_i is not None:
                    if not self.sel_points:
                        self.sel_points = [pos_i]
                    else:
                        self.sel_points.append(pos_i)
                    self.sel_mgr.lasso_press(pos_i.x(), pos_i.y())
                    self.update()
                return

        if event.button() == Qt.MouseButton.LeftButton and self.sel_active and self.sel_mode == "poly":
            if not self.sel_frozen:
                pos_i = self.widget_to_image(event.position().toPoint())
                if pos_i is not None:
                    self.sel_points.append(pos_i)
                    self.sel_mgr.polygon_add_vertex(pos_i.x(), pos_i.y())
                    self.update()
                return


        if event.button() == Qt.MouseButton.LeftButton:
            if self.image is None:
                return

            click_pos = event.position().toPoint()
            image_rect = self.image_rect_on_widget()

            # Calculate image rectangle (at current zoom + offset)
            sw = int(self.image.width() * self.zoom_scale)
            sh = int(self.image.height() * self.zoom_scale)
            x = (self.width() - sw) / 2
            y = (self.height() - sh) / 2

            xi = int(x + self.offset.x())
            yi = int(y + self.offset.y())
            image_rect = QRect(xi, yi, sw, sh)

            # Check if clicking inside image
            if image_rect.contains(click_pos):
                self.selected = True
                self.panning = True
                self.Last_pos = click_pos
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.update()
            else:
                self.selected = False
                self.update()


            self.panning = True                                 # Start Panning mode
            self.Last_pos = event.position().toPoint()          # Remember where we clicked
            self.setCursor(Qt.CursorShape.ClosedHandCursor)     # Change cursor to hand


    ##### Mouse movement while dragging #####
    def mouseMoveEvent(self, event):

        if self.sel_active and self.sel_mode == "lasso" and not self.sel_frozen and self.sel_points:
            pos_i = self.widget_to_image(event.position().toPoint())
            if pos_i is not None:
                if self.sel_points[-1] != pos_i:
                    self.sel_points.append(pos_i)
                    self.sel_mgr.lasso_move(pos_i.x(), pos_i.y(), bool(event.buttons() & Qt.LeftButton))
                    self.update()
            return


        if self.sel_active and self.sel_mode == "rect" and not self.sel_frozen and  self.rect_anchor is not None:
            pos_w = event.position().toPoint()
            pos_i = self.widget_to_image(pos_w)
            if pos_i is not None:
                self.rect_current = pos_i
                self.sel_mgr.rect_update(pos_i.x(), pos_i.y())
                self.update()
            return


        if self.panning and self.Last_pos is not None:

            pos = event.position().toPoint()                    # Current mouse position
            delta = pos - self.Last_pos                         # The Change in mouse position
            self.offset += delta                                # Move the image by that amount
            self.Last_pos = pos                                 # Update for next frame
            self.update()                                       # Trigger paintEvent to redraw, handled by Qt's Event loop


    ##### Mouse Release (stop dragging) #####
    def mouseReleaseEvent(self, event):

        if self.sel_active and self.sel_mode == "lasso" and self.sel_points and not self.sel_frozen:

            self.sel_mgr.lasso_release()
            self.update()
            return


        if self.sel_active and self.sel_mode == "rect" and self.rect_anchor is not None:

            if not self.sel_frozen:
                pos_w = event.position().toPoint()
                pos_i = self.widget_to_image(pos_w)
                if pos_i is not None:
                    self.rect_current = pos_i
                    self.update()
                return



        if self.sel_active and self.sel_mode == "rect":
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False                                # Stop Panning mode
            self.Last_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)          # Change back to normal cursor


    ##### Allows User to Change he canvas Size
    def resize_canvas(self):

        width, ok1 = QInputDialog.getInt(self, "Canvas Width", "Enter Width", 800, 100, 5000 )
        if not ok1:     # User Clicked cancel
            return

        height, ok2 = QInputDialog.getInt(self, "Canvas Height", "Enter Height", 800, 100, 5000 )
        if not ok2:     # User Clicked Cancel
            return

        self.resize(width, height)
        self.update()

    ##### Convert QImage to Numpy array for OpenCV
    def qimage_to_numpy(self, qimage):
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        bits = ptr.tobytes()
        ptr.setsize(qimage.sizeInBytes())
        arr = np.array(ptr, reshape(height, width, 4))  #RGBA

        # Convert RGBA to BGR (OpenCV format)
        bgr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        return bgr

    def numpy_to_qimage(arr):

        # Convert BGR to RGB
        rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)

        height, width, channels = rgb.shape
        bytes_per_line = 3 * width

        q_img = QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return q_img.copy()


    def start_selection(self, mode: str):

        if not self.image or self.image.isNull():
            return

        if mode not in ("rect", "lasso", "poly"):
            return

        self.sel_mode = mode
        self.sel_active = True
        self.sel_frozen = False
        self.rect_anchor = None
        self.rect_current = None
        self.sel_points = []
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()

        self.sel_mgr.start(mode, min_dist=2)
        self.update()

    def cancel_selection(self):
        self.sel_mode = "pan"
        self.sel_active = False
        self.sel_frozen = False
        self.rect_anchor = None
        self.rect_current = None
        self.sel_points = []
        self.sel_mgr.cancel()
        self.active_mask = None
        self.ops_since_freeze = False

        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()


    def image_rect_on_widget(self) -> QRect:

        if not self.image or self.image.isNull():
            return QRect()

        sw = int(self.image.width() * self.zoom_scale)
        sh = int(self.image.height() * self.zoom_scale)

        x = int((self.width() - sw) / 2 + self.offset.x())
        y = int((self.height() - sh) / 2 + self.offset.y())

        return QRect(x, y, sw, sh)

    def widget_to_image(self, p: QPoint):

        if not self.image or self.image.isNull():
            return None

        r = self.image_rect_on_widget()
        if not r.contains(p):
            return None

        ix = (p.x() - r.x()) / self.zoom_scale
        iy = (p.y() - r.y()) / self.zoom_scale

        ix = max(0, min(int(ix), min(self.image.width() - 1, int(ix))))
        iy = max(0, min(int(iy), min(self.image.height() - 1, int(iy))))

        return QPoint(ix, iy)


    def image_to_widget(self, p: QPoint) -> QPoint:
        r = self.image_rect_on_widget()
        wx = int(r.x() + p.x() * self.zoom_scale)
        wy = int(r.y() + p.y() * self.zoom_scale)
        return QPoint(wx, wy)

    def keyPressEvent(self, event):

        if self.sel_active and self.sel_mode in ("rect","lasso", "poly"):
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):

                if not self.sel_mgr.state.frozen:
                    if self.sel_mgr.freeze():
                        self.sel_frozen = True

                        bgr = imf.qpixmap_to_cv2(self.image)

                        if bgr is None:
                            self.cancel_selection()
                            return

                        h, w = bgr.shape[:2]

                        self.active_mask = self.sel_mgr.mask((h, w))
                        self.ops_since_freeze = False
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                        self.update()
                    return

                self.cancel_selection()
                return

            if event.key() == Qt.Key.Key_Escape:
                self.cancel_selection()
                return
        super().keyPressEvent(event)


    def selection_bounds_image(self):
        if not (self.sel_active and self.rect_anchor and self.rect_current):
            return None

        x1, y1 = self.rect_anchor.x(), self.rect_anchor.y()
        x2, y2 = self.rect_current.x(), self.rect_current.y()

        x1, x2 = sorted((int(x1), int(x2)))
        y1, y2 = sorted((int(y1), int(y2)))

        if x2 <= x1 or y2 <= y1:
            return None
        return (x1, y1, x2, y2)

    def get_cv2_image(self):
        if not self.image or self.image.isNull():
            return None
        return imf.qpixmap_to_cv2(self.image)


    def set_cv2_image(self, bgr):
        self.set_image(imf.cv2_to_qpixmap(bgr))










