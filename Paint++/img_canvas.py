# imports different classes from the PyQt library
from PyQt6 import QtGui
import random
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QPen, QPolygon, QImage
from PyQt6.QtCore import Qt, QPoint, QSize, QRect, pyqtSignal
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QColorDialog,
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
    colorPicked = pyqtSignal(QColor)
    def __init__(self, imf_instance, parent=None):
        super().__init__(parent)

        self.imf = imf_instance

        self.image = None                                       # No image loaded yet - Hodls QPixmap (image data)
        self._checker = self.make_checker_brush(tile=16)        # Background Pattern
        self.offset = QPoint(0, 0)                       # Sets the position of the image (for panning)
        self.panning = True                                     # Is the image being dragged, Boolean value - True for default
        self.Last_pos = None                                    # Last Mouse position

        self.selected = False
        self.handle_size = 8
        self.dragging_handle = None
        self.resize_start_size = None
        self.resize_start_pos = None

        self.zoom_scale = 1.0

        self.pen_color = QColor(0, 0, 0)

        self.pen_width = 5
        self.shape_width = 20
        self.shape_height = 20
        self.spray_size = 10

        # Textbox size
        self.text_size = 50
        self.text_enabled = False
        self.text = ""
        self.text_size = 20

        # Paintbrush default drawing state
        self.drawing = False

        # For selecting brush
        self.brush_enabled = False

        # For selecting spray
        self.spray_enabled = False

        # For selecting rectangle
        self.rect_enabled = False

        # For selecting ellipse
        self.ellipse_enabled = False

        # For selecting triangle
        self.triangle_enabled = False

        # Store fill checkbox state
        self.shape_fill_enabled = False

        # For selecting color picker
        self.picker_enabled = False

        self.eraser_enabled = False

    def set_fill_enabled(self, state: int):
        self.shape_fill_enabled = bool(state)
        # print("Canvas fill enabled:", self.shape_fill_enabled)

        # if tool instantly affects canvas repaint
        self.update()

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
        # Convert QPixmap to QImage so we can draw on it
        if pix is not None and not pix.isNull():
            self.image = pix.toImage()
            # Ensure it has an alpha channel for transparency
            if self.image.format() != QImage.Format.Format_ARGB32:
                self.image = self.image.convertToFormat(QImage.Format.Format_ARGB32)
        else:
            self.image = None

        self.offset = QPoint(0, 0)
        self.zoom_scale = 1.0

        if self.image is not None and not self.image.isNull():
            self.setMinimumSize(self.image.size())
            if self.image.width() > self.width() or self.image.height() > self.image.height():
                self.resize(self.image.size())

        self.update()

    def pixmap(self):
        """Return the currently displayed image as QPixmap."""
        if self.image is not None and not self.image.isNull():
            return QPixmap.fromImage(self.image)
        return None

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
        x = (self.width() - self.image.width()) / 2
        y = (self.height() - self.image.height()) / 2

        # Where the image drawn after the users dragged it (self.offset)
        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())
        p.drawImage(xi, yi, self.image.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # Draw border around the image
        if self.selected:
            p.setPen(QPen(QColor("#000000"), 3))
        else:
            p.setPen(QColor("#888888"))

        p.drawRect(xi, yi, scaled_width-1, scaled_height-1)

    def sizeHint(self):
        if self.image is not None:
            return self.image.size()
        return QSize(800, 600)

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

    ##### Mouse Press (Start Dragging) #####

    def mousePress_compute(self, event):
        # If LMB is not pressed return
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # If image is none, return
        if self.image is None:
            return

        # Mouse position in widget coordinates
        click_pos = event.position().toPoint()

        # Centered position of the image on the canvas (before pan)
        x = (self.width() - self.image.width()) / 2
        y = (self.height() - self.image.height()) / 2

        # Apply pan offset and snap to integer pixels
        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())

        # Store for later use (e.g., in mouseMoveEvent)
        self.image_origin = QPoint(xi, yi)

        # Actual rectangle occupied by the image
        image_rect = QRect(xi, yi, self.image.width(), self.image.height())

        return click_pos, self.image_origin, image_rect, xi, yi

    def mousePressEvent(self, event):
        # Computing position of mouse press
        click_pos, image_origin, image_rect, xi, yi = self.mousePress_compute(event)

        # Check if the click was inside the image rectangle
        if image_rect.contains(click_pos): # Inside

            # If brush mode is enabled then draw, not pan
            if (getattr(self, "brush_enabled", False) or getattr(self, "spray_enabled", False) or getattr(self, "rect_enabled", False) or
                    getattr(self, "ellipse_enabled", False) or getattr(self, "triangle_enabled", False) or getattr(self, "text_enabled", False) or getattr(self, "eraser_enabled", False)):

                # Set drawing state as true
                self.drawing = True

                # Store mouse cursor position
                self.last_point = click_pos

                # Convert widget coordinates to image coordinates
                image_x = click_pos.x() - xi
                image_y = click_pos.y() - yi

                # Draw a point directly on the image
                painter = QtGui.QPainter(self.image)

                if getattr(self, "eraser_enabled", False):
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                    pen = QPen(Qt.GlobalColor.transparent, self.pen_width)

                else:
                    pen = QPen(self.pen_color, self.pen_width)

                painter.setPen(pen)

                # Sets font for text
                if getattr(self, "text_enabled", False):
                    font = QtGui.QFont()
                    font.setFamily('Times')
                    font.setBold(True)
                    font.setPointSize(self.text_size)
                    painter.setFont(font)

                sw = self.shape_width
                sh = self.shape_height

                if self.shape_fill_enabled:
                    brush = QtGui.QBrush()
                    brush.setColor(QtGui.QColor(self.pen_color))
                    brush.setStyle(Qt.BrushStyle.SolidPattern)
                    painter.setBrush(brush)

                if getattr(self, "triangle_enabled", False):
                    points = QPolygon([QPoint(int(image_x - sw/2), int(image_y + sh/2)), QPoint(int(image_x + sw/2), int(image_y + sh/2)), QPoint(int(image_x), int(image_y - sh/2))])
                    painter.drawPolygon(points)

                elif getattr(self, "text_enabled", False):
                    painter.drawText(image_x, image_y, self.text)

                elif getattr(self, "rect_enabled", False):
                    painter.drawRect(int(image_x - sw/2), int(image_y - sh/2), sw, sh)

                elif getattr(self, "ellipse_enabled", False):
                    painter.drawEllipse(int(image_x - sw/2), int(image_y - sh/2), sw, sh)

                elif getattr(self, "brush_enabled", False) or getattr(self, "eraser_enabled", False):
                    painter.drawPoint(image_x, image_y)

                elif getattr(self, "spray_enabled", False):
                    # Draw many tiny dots near the initial click (like a quick spray burst)
                    for n in range(100):  # same density as during movement
                        xo = random.gauss(0, self.spray_size)
                        yo = random.gauss(0, self.spray_size)

                        # Draw using image coordinates
                        painter.drawPoint(
                            int(image_x + xo),
                            int(image_y + yo)
                        )

                painter.end()

                # Update display so the dot appears immediately
                self.update()
                return

            elif getattr(self, "panning", False):
                # If paint was disabled, pan not draw
                self.selected = True                            # Mark image as selected
                self.last_pos = click_pos                       # Remember where they clicked (for dragging)
                self.setCursor(Qt.CursorShape.ClosedHandCursor) # Change cursor to closed hand (grabbing)
                self.update()  # Redraw the canvas

        else: # Outside
            self.selected = False  # Deselect the image
            self.update()  # Redraw the canvas

    def mouseMoveEvent(self, event):
        # Drawing state if drawing is enabled and LMB is pressed
        if getattr(self, "brush_enabled", False) and self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            # Creates painter object for drawing on image
            painter = QPainter(self.image)

            # Creates pen with defined color and width
            pen = QPen(self.pen_color, self.pen_width)

            # Makes painter use the selected pen
            painter.setPen(pen)

            # Gets the current mouse position adjusted for image offset
            current_point = event.position().toPoint() - self.image_origin

            # Gets the previous mouse position adjusted for image offset
            last_point_on_image = self.last_point - self.image_origin

            # Draws line from last to current position on the image
            painter.drawLine(last_point_on_image, current_point)

            # Releases painter
            painter.end()

            # Updates the last point for next mouse event (store screen position)
            self.last_point = event.position().toPoint()

            # Triggers repaint of the widget
            self.update()
            return

        if getattr(self, "spray_enabled", False) and self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            # Creates painter object for drawing on image
            painter = QPainter(self.image)

            # Creates pen with defined color and width
            pen = QPen(self.pen_color, self.pen_width)

            # Makes painter use the selected pen
            painter.setPen(pen)

            # Gets the current mouse position adjusted for image offset
            current_point = event.position().toPoint() - self.image_origin

            for n in range(100):
                xo = random.gauss(0, self.spray_size)
                yo = random.gauss(0, self.spray_size)
                painter.drawPoint(
                    int(current_point.x() + xo),
                    int(current_point.y() + yo)
                )
            # Releases painter
            painter.end()

            # Updates the last point for next mouse event (store screen position)
            self.last_point = event.position().toPoint()

            # Triggers repaint of the widget
            self.update()
            return

        if getattr(self, "eraser_enabled", False) and self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)

            eraser_pen = QPen(Qt.GlobalColor.transparent)
            eraser_pen.setWidth(self.pen_width)
            eraser_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            eraser_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(eraser_pen)

            current_point = event.position().toPoint() - self.image_origin
            last_point_on_image = self.last_point - self.image_origin

            painter.drawLine(last_point_on_image, current_point)
            painter.end()

            self.last_point = event.position().toPoint()
            self.update()
            return

        # Panning state as default when LMB is pressed
        if self.panning and (event.buttons() & Qt.MouseButton.LeftButton):
            # Difference in position after pressing and dragging
            delta = event.position().toPoint() - self.last_pos

            # Adds the difference to the offset
            self.offset += delta

            # Updates the last position for next move event
            self.last_pos = event.position().toPoint()

            # Triggers panning of the widget
            self.update()

    def mouseReleaseEvent(self, event):
        # Cheks if LMB is released
        if event.button() == Qt.MouseButton.LeftButton:

            if (getattr(self, "rect_enabled", False) or getattr(self, "triangle_enabled", False) or getattr(self, "brush_enabled", False)
                            or getattr(self, "ellipse_enabled", False) or getattr(self, "spray_enabled", False) or getattr(self, "eraser_enabled", False)):
                self.drawing = False

            # If brush tool was not active, stop panning
            if self.panning:

                # Change cursor back to arrow from fist
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_eraser_mode(self):
        self.eraser_enabled = not self.eraser_enabled

        if self.eraser_enabled:
            # disable all other tools
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.text_enabled = False
            self.picker_enabled = False
            self.panning = False

            size, ok = QInputDialog.getInt(self, "Eraser size", "Size (1-100)", 20, 1, 100)
            if not ok: return

            self.pen_width = size
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_brush_mode(self):
        # Toggles the brush enabled state
        self.brush_enabled = not self.brush_enabled

        # If paintbrush is enabled set cursor as cross
        if self.brush_enabled:

            self.spray_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.panning = False
            self.text_enabled = False
            self.picker_enabled = False
            self.eraser_enabled = False

            brush_size, ok1 = QInputDialog.getInt(self, "Paintbrush size", "Enter size (1-100)", 5, 1, 100)
            if not ok1: return

            # Paintbrush thickness
            self.pen_width = brush_size

            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose brush color")
            if not color.isValid():
                return

            self.pen_color = color

            self.setCursor(Qt.CursorShape.CrossCursor)

        # If paintbrush is disabled set cursor as standard arrow
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_spray_mode(self):
        # Toggles the spray enabled state
        self.spray_enabled = not self.spray_enabled

        # If spray is enabled set cursor as cross
        if self.spray_enabled:

            self.brush_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.panning = False
            self.text_enabled = False
            self.picker_enabled = False
            self.eraser_enabled = False

            # Spray pixel thickness
            self.pen_width = 1

            spray_size, ok1 = QInputDialog.getInt(self, "Spray diameter", "Enter size (1-100)", 5, 1, 100)
            if not ok1: return

            self.spray_size = spray_size

            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose spray color")
            if not color.isValid():
                return

            self.pen_color = color

            self.setCursor(Qt.CursorShape.CrossCursor)

        # If spray is disabled set cursor as standard arrow
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_rect_mode(self):
        self.rect_enabled = not self.rect_enabled

        if self.rect_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.panning = False
            self.text_enabled = False
            self.picker_enabled = False
            self.eraser_enabled = False

            outline_width, ok1 = QInputDialog.getInt(self, "Outline width", "Enter line thickness (1-100)", 5, 1, 100)
            if not ok1: return

            rect_width, ok2 = QInputDialog.getInt(self, "Rectangle width", "Enter width (1-1000)", 50, 1, 1000)
            if not ok2: return

            rect_height, ok3 = QInputDialog.getInt(self, "Rectangle height", "Enter heigth (1-1000)", 50, 1, 1000)
            if not ok3: return

            self.pen_width = outline_width
            self.shape_width = rect_width
            self.shape_height = rect_height

            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                        self, "Choose rectangle color")

            if not color.isValid():
                return

            self.pen_color = color

            self.setCursor(Qt.CursorShape.CrossCursor)

        # If paintbrush is disabled set cursor as standard arrow
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_ellipse_mode(self):
        self.ellipse_enabled = not self.ellipse_enabled

        if self.ellipse_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.triangle_enabled = False
            self.text_enabled = False
            self.panning = False
            self.picker_enabled = False
            self.eraser_enabled = False

            outline_width, ok1 = QInputDialog.getInt(self, "Outline width", "Enter line thickness (1-100)", 5, 1, 100)
            if not ok1: return

            ellipse_width, ok2 = QInputDialog.getInt(self, "Ellipse width", "Enter width (1-1000)", 50, 1, 1000)
            if not ok2: return

            ellipse_height, ok3 = QInputDialog.getInt(self, "Ellipse height", "Enter heigth (1-1000)", 50, 1, 1000)
            if not ok3: return

            self.pen_width = outline_width
            self.shape_width = ellipse_width
            self.shape_height = ellipse_height

            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose ellipse color")

            if not color.isValid():
                return

            self.pen_color = color

            self.setCursor(Qt.CursorShape.CrossCursor)

        # If paintbrush is disabled set cursor as standard arrow
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_triangle_mode(self):
        self.triangle_enabled = not self.triangle_enabled

        if self.triangle_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.panning = False
            self.text_enabled = False
            self.picker_enabled = False
            self.eraser_enabled = False

            outline_width, ok1 = QInputDialog.getInt(self, "Outline width", "Enter line thickness (1-100)", 5, 1, 100)
            if not ok1: return

            triangle_width, ok2 = QInputDialog.getInt(self, "Triangle width", "Enter width (1-1000)", 50, 1, 1000)
            if not ok2: return

            triangle_height, ok3 = QInputDialog.getInt(self, "Triangle height", "Enter heigth (1-1000)", 50, 1, 1000)
            if not ok3: return

            self.pen_width = outline_width
            self.shape_width = triangle_width
            self.shape_height = triangle_height

            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose triangle color")

            if not color.isValid():
                return

            self.pen_color = color
            self.setCursor(Qt.CursorShape.CrossCursor)

        # If paintbrush is disabled set cursor as standard arrow
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_text_mode(self):
        self.text_enabled = not self.text_enabled

        if self.text_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.panning = False
            self.picker_enabled = False
            self.eraser_enabled = False

            pointsize, ok1 = QInputDialog.getInt(self, "Text size", "Enter size (1-100)", 5, 1, 100)
            if not ok1: return

            text, ok2 = QInputDialog.getText(self, "Text", "Enter text:")
            if not ok2 or text=="": return

            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose triangle color")

            if not color.isValid():
                return

            self.text = text
            self.pen_color = color
            self.text_size = pointsize
            self.setCursor(Qt.CursorShape.CrossCursor)

            # If paintbrush is disabled set cursor as standard arrow
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_panning_mode(self):
        self.panning = not self.panning

        self.brush_enabled = False
        self.spray_enabled = False
        self.rect_enabled = False
        self.ellipse_enabled = False
        self.triangle_enabled = False
        self.text_enabled = False
        self.picker_enabled = False
        self.eraser_enabled = False

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def color_picker(self):
        self.brush_enabled = False
        self.spray_enabled = False
        self.rect_enabled = False
        self.ellipse_enabled = False
        self.triangle_enabled = False
        self.text_enabled = False
        self.panning = False
        self.eraser_enabled = False

        # Check if image is opened
        if self.image is None or self.image.isNull():
            QMessageBox.information(None, "No Image", "Image must be loaded first")
            return

        # Get QPixmap
        pix = QPixmap.fromImage(self.image)

        # Convert QPixmap to BGR
        cv = self.imf.qpixmap_to_cv2(pix)
        cv_image = cv2.cvtColor(cv, cv2.COLOR_RGBA2BGR)

        clicked_pos = {"x": None, "y": None}

        # Define callback before assigning
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked_pos["x"], clicked_pos["y"] = x, y
                cv2.destroyAllWindows()

        # Show image and set callback
        cv2.imshow("Color Picker", cv_image)
        cv2.setMouseCallback("Color Picker", mouse_callback)

        # Wait for user click
        while True:
            cv2.waitKey(20)
            if clicked_pos["x"] is not None:
                break

        # Extract BGR color at the clicked pixel
        r, g, b = cv_image[clicked_pos["y"], clicked_pos["x"]]
        self.pen_color = QColor(int(b), int(g), int(r))

        self.colorPicked.emit(self.pen_color)

        self.panning = True