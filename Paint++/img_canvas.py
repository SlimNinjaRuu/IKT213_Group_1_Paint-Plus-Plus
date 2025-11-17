# imports different classes from the PyQt library
from PyQt6 import QtGui
import random
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QPen, QPolygon, QImage
from PyQt6.QtCore import Qt, QPoint, QSize, QRect, pyqtSignal
from PyQt6 import QtCore
from PyQt6.QtCore import QRectF
from image_menu_functions import imf
from SelectionManager import SelectionManager
from PyQt6.QtWidgets import (QWidget, QColorDialog, QInputDialog)



##### Inhertis from Qwidget ######
class Img_Canvas(QWidget):
    colorPicked = pyqtSignal(QColor)

    def __init__(self, imf_instance, parent=None):
        super().__init__(parent)

        self.imf = imf_instance

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

        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 5
        self.shape_width = 20
        self.shape_height = 20
        self.spray_size = 10

        # Textbox size
        self.text_size = 50
        self.text_enabled = False
        self.text = ""

        # Paintbrush default drawing state
        self.drawing = False

        # For selecting brush
        self.brush_enabled = False
        self.eraser_enabled = False

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
        self._cv_picker_active = False
        self._cv_picker_click = None
        self._cv_picker_timer = None
        self._cv_picker_win = "Color Picker"

        # Selection Tools
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.sel_mode = "pan"
        self.rect_anchor = None                                 # Qpoint in image coordinates
        self.rect_current = None                                # Qpoint to image coordinate
        self.sel_active = False
        self.sel_frozen = False                                 # Selection is finalized with Enter
        self.sel_points = []
        self.pending_op = None

        self.sel_mgr = SelectionManager()                       # Selection state holder
        self.active_mask = None
        self.ops_since_freeze = False


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
        # Load new image from QPixmap
        if pix is not None and not pix.isNull():

            # Store as QImage so we can draw on it
            self.image = pix.toImage()
            # Ensure it has an alpha channel for transparency
            if self.image.format() != QImage.Format.Format_ARGB32:
                self.image = self.image.convertToFormat(QImage.Format.Format_ARGB32)
        else:
            self.image = None

        # Reset pan and zoom
        self.offset = QPoint(0, 0)
        self.zoom_scale = 1.0

        # Update minimmum sizr to match image
        if self.image is not None and not self.image.isNull():
            self.setMinimumSize(self.image.size())
            if self.image.width() > self.width() or self.image.height() > self.image.height():
                self.resize(self.image.size())

        # Redraw widget
        self.update()

    # Return current image as QPixmap
    def pixmap(self):
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


    # Paint widget: background, image, border and selection overlay
    def paintEvent(self, event):
        p = QPainter(self)

        # Fill background with checker pattern
        p.fillRect(self.rect(), self._checker)


        if self.image is None:                                  # Exits the method if there is no image
            return

        # Find the scaled image size from zoom
        scaled_width = int(self.image.width() * self.zoom_scale)
        scaled_height = int(self.image.height() * self.zoom_scale)

        # Center image in widget
        x = (self.width() - scaled_width) / 2
        y = (self.height() - scaled_height) / 2


        # Apply panning offset
        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())

        # Draw scaled image
        p.drawImage(xi, yi, self.image.scaled(
            scaled_width,
            scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))        # Draws the image with DrawPixmap

        # Draw border around the image
        if self.selected:
            p.setPen(QPen(QColor("#000000"), 3))
        else:
            p.setPen(QColor("#888888"))

        p.drawRect(xi, yi, scaled_width-1, scaled_height-1)

        # Draw selection overlay if active
        if self.sel_active:
            selection_path = QtGui.QPainterPath()

            # Rectangle selection
            if self.sel_active and self.sel_mode == "rect" and self.rect_anchor and self.rect_current:
                a = self.rect_anchor
                b = self.rect_current

                x1, y1 = min(a.x(), b.x()), min(a.y(), b.y())
                x2, y2 = max(a.x(), b.x()), max(a.y(), b.y())

                # convert image coordinates to widget coordinates
                tl = self.image_to_widget(QPoint(x1, y1))
                br = self.image_to_widget(QPoint(x2, y2))
                selection_path.addRect(QRectF(QRect(tl, br)))

            # Lasso/polygon selection outline
            elif self.sel_mode in ("lasso", "poly") and len(self.sel_points) >= 2:

                # Convert all selection points to widget coordinates
                pts_w = [self.image_to_widget(p) for p in self.sel_points]

                path = QtGui.QPainterPath()
                path.moveTo(QtCore.QPointF(pts_w[0]))

                for q in pts_w[1:]:
                    path.lineTo(QtCore.QPointF(q))

                # Close shape when frozen
                if self.sel_frozen and len(pts_w) >= 3:
                    path.closeSubpath()

                selection_path.addPath(path)

            # Dim everything outside selection and draw red outline
            if not selection_path.isEmpty():
                overlay = QtGui.QPainterPath()
                overlay.addRect(QRectF(self.rect()))
                dimmed_area = overlay.subtracted(selection_path)

                # Darken outside selection
                p.fillPath(dimmed_area, QColor( 0, 0, 0, 80))

                # Highlight selection border
                p.setPen(QPen(QColor(255, 0, 0), 2))
                p.drawPath(selection_path)



    # Suggest default widget size based on image
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
        scaled_width = int(self.image.width() * self.zoom_scale)
        scaled_height = int(self.image.height() * self.zoom_scale)

        x = (self.width() - scaled_width) / 2
        y = (self.height() - scaled_height) / 2


        # Apply pan offset and snap to integer pixels
        xi = int(x + self.offset.x())
        yi = int(y + self.offset.y())

        # Store for later use (e.g., in mouseMoveEvent)
        self.image_origin = QPoint(xi, yi)

        # Actual rectangle occupied by the image
        image_rect = QRect(xi, yi, scaled_width, scaled_height)
        return click_pos, self.image_origin, image_rect, xi, yi



    # Handle mouse press for selection, drawing anf panning
    def mousePressEvent(self, event):

        # Handle active selection before tools
        if event.button() == Qt.MouseButton.LeftButton and self.sel_active and not self.sel_frozen:


            # Rectangle selection: set anchor and start rect
            if self.sel_mode == "rect":
                pos_w = event.position().toPoint()
                pos_i = self.widget_to_image(pos_w)

                if pos_i is not None:
                    self.rect_anchor = pos_i
                    self.rect_current = pos_i
                    self.sel_mgr.rect_start(pos_i.x(), pos_i.y())
                    self.update()
                return

            # Lasso selection: start freehand path
            elif self.sel_mode == "lasso" and not self.sel_frozen:
                if event.button() == Qt.MouseButton.LeftButton:
                    pos_i = self.widget_to_image(event.position().toPoint())
                    if pos_i is not None:
                        self.sel_points.append(pos_i)
                        self.sel_mgr.lasso_press(pos_i.x(), pos_i.y())
                        self.update()
                return

            # Polygon selection: add vertex on each click
            elif self.sel_mode == "poly" and not self.sel_frozen:
                pos_i = self.widget_to_image(event.position().toPoint())
                if pos_i is not None:
                    self.sel_points.append(pos_i)
                    self.sel_mgr.polygon_add_vertex(pos_i.x(), pos_i.y())
                    self.update()
                return

        # Handle drawing tools (brush, shapes, text, spray eraser)
        result = self.mousePress_compute(event)
        if result is None:
            return

        # unpack mouse press info
        click_pos, image_origin, image_rect, xi, yi = result

        # Check if the click was inside the image rectangle
        if image_rect.contains(click_pos):

            # If brush mode is enabled then draw, not pan
            if (self.brush_enabled or self.spray_enabled or self.rect_enabled or self.ellipse_enabled or self.triangle_enabled or self.text_enabled or getattr(self, "eraser_enabled", False)):

                # Set drawing state as true
                self.drawing = True

                # Store mouse cursor position
                self.last_point = click_pos

                # Convert widget coordinates to image coordinates
                pos_i = self.widget_to_image(click_pos)
                if pos_i is None:
                    return
                image_x = pos_i.x()
                image_y = pos_i.y()

                # Draw a point directly on the image
                painter = QtGui.QPainter(self.image)
                pen = QPen(self.pen_color, self.pen_width)
                painter.setPen(pen)

                # Eraser uses transparent composition
                if getattr(self, "eraser_enabled", False):
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                    pen = QPen(Qt.GlobalColor.transparent, self.pen_width)

                else:
                    pen = QPen(self.pen_color, self.pen_width)
                    painter.setPen(pen)

                # Sets font for text
                font = QtGui.QFont()
                font.setFamily('Times')
                font.setBold(True)
                font.setPointSize(self.text_size)
                painter.setFont(font)

                sw = self.shape_width
                sh = self.shape_height

                # optional fill for shapes
                if self.shape_fill_enabled:
                    brush = QtGui.QBrush()
                    brush.setColor(QtGui.QColor(self.pen_color))
                    brush.setStyle(Qt.BrushStyle.SolidPattern)
                    painter.setBrush(brush)

                # Triangle at click position
                if getattr(self, "triangle_enabled", False):
                    points = QPolygon([QPoint(int(image_x - sw/2), int(image_y + sh/2)), QPoint(int(image_x + sw/2), int(image_y + sh/2)), QPoint(int(image_x), int(image_y - sh/2))])
                    painter.drawPolygon(points)

                # Centered text at click position
                elif getattr(self, "text_enabled", False):
                    fm = painter.fontMetrics()
                    textwidth = fm.horizontalAdvance(self.text)
                    textheight = fm.height()

                    painter.drawText(
                        image_x - textwidth // 2,
                        image_y + textheight // 2,
                        self.text)


                # Centertd at click position
                elif getattr(self, "rect_enabled", False):
                    painter.drawRect(int(image_x - sw/2), int(image_y - sh/2), sw, sh)

                elif getattr(self, "ellipse_enabled", False):
                    painter.drawEllipse(int(image_x - sw/2), int(image_y - sh/2), sw, sh)

                # Single brush point
                elif getattr(self, "brush_enabled", False):
                    painter.drawPoint(image_x, image_y)

                # Spray burst at click position
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
                self.update()
                return

            # No drawing tool active, start panning
            self.panning = True
            self.selected = True                            # Mark image as selected
            self.Last_pos = click_pos                       # Remember where they clicked (for dragging)
            self.setCursor(Qt.CursorShape.ClosedHandCursor) # Change cursor to closed hand (grabbing)
            self.update()  # Redraw the canvas
        else: # Outside
            self.selected = False  # Deselect the image
            self.update()  # Redraw the canvas


    # Handle mouse movement for selection, drawing and panning
    def mouseMoveEvent(self, event):

        # Lasso selection: record path while dragging
        if self.sel_active and self.sel_mode == "lasso" and not self.sel_frozen:
            if event.buttons() & Qt.MouseButton.LeftButton and self.sel_mgr.state.drawing:
                pos_i = self.widget_to_image(event.position().toPoint())
                if pos_i is not None:

                    # Add new point if it is different from the last
                    if not self.sel_points or self.sel_points[-1] != pos_i:
                        self.sel_points.append(pos_i)
                        self.sel_mgr.lasso_move(pos_i.x(), pos_i.y(), True)
                        self.update()
            return


        # Rectangle Selection: update current corner while dragging
        elif self.sel_active and self.sel_mode == "rect" and not self.sel_frozen and self.rect_anchor is not None:
            pos_w = event.position().toPoint()
            pos_i = self.widget_to_image(pos_w)
            if pos_i is not None:
                self.rect_current = pos_i
                self.sel_mgr.rect_update(pos_i.x(), pos_i.y())
                self.update()
            return

        # Brush tool: draw on image while sragging with LMB
        if getattr(self, "brush_enabled", False) and self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            # Creates painter object for drawing on image
            painter = QPainter(self.image)

            # Use pen with current color and width
            pen = QPen(self.pen_color, self.pen_width)
            painter.setPen(pen)

            # Find image position on widget with zoom and offset
            scaled_width = int(self.image.width() * self.zoom_scale)
            scaled_height = int(self.image.height() * self.zoom_scale)
            x = (self.width() - scaled_width) / 2
            y = (self.height() - scaled_height) / 2

            xi = int(x + self.offset.x())
            yi = int(y + self.offset.y())


            # Convert mouse position from widget space to image pixel coordinates
            current_widget = event.position().toPoint()

            current_img = QPoint(
                int((current_widget.x() - xi ) / self.zoom_scale),
                int((current_widget.y() - yi ) / self.zoom_scale))

            last_img = QPoint(
                int((self.last_point.x() - xi ) / self.zoom_scale),
                int((self.last_point.y() - yi ) / self.zoom_scale))

            # Draws line from last to current position on the image
            painter.drawLine(last_img, current_img)

            # Releases painter
            painter.end()

            # Updates the last point for next mouse event (store screen position)
            self.last_point = event.position().toPoint()

            # Triggers repaint of the widget
            self.update()
            return


        # Eraser tooø: clear pixels along hte stroke
        if getattr(self, "eraser_enabled", False) and self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)

            # Configure Eraser pen: transparent, correct size, rounded stroke
            eraser_pen = QPen(Qt.GlobalColor.transparent)
            eraser_pen.setWidth(self.pen_width)
            eraser_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            eraser_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(eraser_pen)

            # Convert mouse position from widget space to image pixel coordinates (using image_origin)
            current_point = event.position().toPoint() - self.image_origin
            last_point_on_image = self.last_point - self.image_origin

            painter.drawLine(last_point_on_image, current_point)
            painter.end()

            # Store last mouse position in widget space
            self.last_point = event.position().toPoint()
            self.update()
            return


        # Spray tool: Draw random points around the cursor
        if getattr(self, "spray_enabled", False) and self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            # Creates painter object for drawing on image
            painter = QPainter(self.image)

            # Creates pen with defined color and width
            pen = QPen(self.pen_color, self.pen_width)

            # Makes painter use the selected pen
            painter.setPen(pen)

            # Gets the current mouse position adjusted for image offset
            current_point = event.position().toPoint()


            # Find image position on widget using zoom and offset
            scaled_width = int(self.image.width() * self.zoom_scale)
            scaled_height = int(self.image.height() * self.zoom_scale)
            x = (self.width() - scaled_width) / 2
            y = (self.height() - scaled_height) / 2
            xi = int(x + self.offset.x())
            yi = int(y + self.offset.y())

            # Draw spray as random points around the cursor
            current_img_x = int((current_point.x() - xi) / self.zoom_scale)
            current_img_y = int((current_point.y() - yi) / self.zoom_scale)


            # Draw spray as random points around the cursor
            for n in range(100):
                xo = random.gauss(0, self.spray_size)
                yo = random.gauss(0, self.spray_size)
                painter.drawPoint(
                    int(current_img_x + xo),
                    int(current_img_y + yo)
                )
            # Releases painter
            painter.end()

            # Store last mouse position in widget space
            self.last_point = event.position().toPoint()

            # Request repaint of the widget space
            self.update()
            return

        # Panning: move image when dragging with left mouse button
        if self.panning and (event.buttons() & Qt.MouseButton.LeftButton):

            pos = event.position().toPoint()
            delta = pos - self.Last_pos

            # Adds the difference to the offset
            self.offset += delta

            # Updates the last position for next move event
            self.Last_pos = pos

            # Triggers panning of the widget
            self.update()



    ##### Mouse Release (stop dragging) #####
    def mouseReleaseEvent(self, event):

        if self.sel_active and not self.sel_frozen:
            if self.sel_mode == "lasso" and self.sel_points:
                self.sel_mgr.lasso_release()
                self.update()
                return
            elif self.sel_mode == "rect" and self.rect_anchor is not None:
                    pos_w = event.position().toPoint()
                    pos_i = self.widget_to_image(pos_w)
                    if pos_i is not None:
                        self.rect_current = pos_i
                        self.update()
                    return

        if event.button() == Qt.MouseButton.LeftButton:

            if (getattr(self, "rect_enabled", False) or getattr(self, "triangle_enabled", False) or getattr(self, "brush_enabled", False)
                            or getattr(self, "ellipse_enabled", False) or getattr(self, "spray_enabled", False) or getattr(self,"eraser_enabled", False)):
                self.drawing = False

            # If brush tool was not active, stop panning
            if self.panning:
                self.panning = False
                self.Last_pos = None
                # Change cursor back to arrow from fist
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


    # Toggle eraser tool
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

            # Ask for eraser size
            size, ok = QInputDialog.getInt(self, "Eraser size", "Size (1-100)", 20, 1, 100)
            if not ok: return

            # Use size as pen width for erasing
            self.pen_width = size
            self.setCursor(Qt.CursorShape.CrossCursor)

        # Exit eraser mode and enable panning
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


    # Toggle rectangle drawing tool
    def toggle_rect_mode(self):

        # Enable/disable rectangle mode
        self.rect_enabled = not self.rect_enabled


        # Turn off other tools
        if self.rect_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.panning = False
            self.text_enabled = False
            self.picker_enabled = False
            self.eraser_enabled = False

            # Ask for outline width
            outline_width, ok1 = QInputDialog.getInt(self, "Outline width", "Enter line thickness (1-100)", 5, 1, 100)
            if not ok1: return


            # Ask or rectangle size
            rect_width, ok2 = QInputDialog.getInt(self, "Rectangle width", "Enter width (1-1000)", 50, 1, 1000)
            if not ok2: return

            rect_height, ok3 = QInputDialog.getInt(self, "Rectangle height", "Enter heigth (1-1000)", 50, 1, 1000)
            if not ok3: return


            # Store size and outline settings
            self.pen_width = outline_width
            self.shape_width = rect_width
            self.shape_height = rect_height

            # Ask for outline color
            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                        self, "Choose rectangle color")

            if not color.isValid():
                return

            self.pen_color = color

            self.setCursor(Qt.CursorShape.CrossCursor)

        # Exit rectanlge mode and enable panning
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)


    # Toggle ellipse drawing tool
    def toggle_ellipse_mode(self):

        # Enable/disable ellipse mode
        self.ellipse_enabled = not self.ellipse_enabled

        # Turn off other tools
        if self.ellipse_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.triangle_enabled = False
            self.text_enabled = False
            self.panning = False
            self.picker_enabled = False
            self.eraser_enabled = False

            # ask for outline width
            outline_width, ok1 = QInputDialog.getInt(self, "Outline width", "Enter line thickness (1-100)", 5, 1, 100)
            if not ok1: return


            # Ask for ellipse size
            ellipse_width, ok2 = QInputDialog.getInt(self, "Ellipse width", "Enter width (1-1000)", 50, 1, 1000)
            if not ok2: return

            ellipse_height, ok3 = QInputDialog.getInt(self, "Ellipse height", "Enter heigth (1-1000)", 50, 1, 1000)
            if not ok3: return

            # Store size and outline settings
            self.pen_width = outline_width
            self.shape_width = ellipse_width
            self.shape_height = ellipse_height

            # Ask for outline color
            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose ellipse color")

            if not color.isValid():
                return

            self.pen_color = color

            self.setCursor(Qt.CursorShape.CrossCursor)

        # Exit ellips mode and enable panning
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)



    # Toggle triangle drawing tool
    def toggle_triangle_mode(self):

        # Enable/disable triangle mode
        self.triangle_enabled = not self.triangle_enabled

        # Turn off other tools
        if self.triangle_enabled:
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.panning = False
            self.text_enabled = False
            self.picker_enabled = False
            self.eraser_enabled = False

            # Ask for outline width
            outline_width, ok1 = QInputDialog.getInt(self, "Outline width", "Enter line thickness (1-100)", 5, 1, 100)
            if not ok1: return

            # Ask for Triangle size
            triangle_width, ok2 = QInputDialog.getInt(self, "Triangle width", "Enter width (1-1000)", 50, 1, 1000)
            if not ok2: return

            triangle_height, ok3 = QInputDialog.getInt(self, "Triangle height", "Enter heigth (1-1000)", 50, 1, 1000)
            if not ok3: return


            # Store size and outline settings
            self.pen_width = outline_width
            self.shape_width = triangle_width
            self.shape_height = triangle_height


            # Ask for outline color
            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose triangle color")

            if not color.isValid():
                return

            self.pen_color = color
            self.setCursor(Qt.CursorShape.CrossCursor)

        # Exit Triangle mode and enable panning
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)


    # Toogle text tool on/off
    def toggle_text_mode(self):
        self.text_enabled = not self.text_enabled

        if self.text_enabled:
            # Turn off other tools
            self.brush_enabled = False
            self.spray_enabled = False
            self.rect_enabled = False
            self.ellipse_enabled = False
            self.triangle_enabled = False
            self.panning = False
            self.picker_enabled = False
            self.eraser_enabled = False

            # Ask for text size
            pointsize, ok1 = QInputDialog.getInt(self, "Text size", "Enter size (1-100)", 5, 1, 100)
            if not ok1: return

            # Ask for text content
            text, ok2 = QInputDialog.getText(self, "Text", "Enter text:")
            if not ok2 or text=="": return

            # Ask for text color
            color = QColorDialog.getColor(self.pen_color if hasattr(self, "pen_color") else QColor(0, 0, 0),
                                          self, "Choose triangle color")

            if not color.isValid():
                return

            # Store text settings and switch to crosshair
            self.text = text
            self.pen_color = color
            self.text_size = pointsize
            self.setCursor(Qt.CursorShape.CrossCursor)

        # Exit txt mode and enable panning
        else:
            self.panning = True
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # Turn panning on/off and disable other tools
    def toggle_panning_mode(self):

        # Flip panning state
        self.panning = not self.panning

        # Disable all drawing tools
        self.brush_enabled = False
        self.spray_enabled = False
        self.rect_enabled = False
        self.ellipse_enabled = False
        self.triangle_enabled = False
        self.text_enabled = False
        self.picker_enabled = False
        self.eraser_enabled = False

        # Normal cursor when panning
        self.setCursor(Qt.CursorShape.ArrowCursor)



    # Begin a new selection (rect, lasso or poly)
    def start_selection(self, mode: str):

        # Need an image first
        if not self.image or self.image.isNull():
            return

        # Only allow known modes
        if mode not in ("rect", "lasso", "poly"):
            return

        # Reset selection state
        self.sel_mode = mode
        self.sel_active = True
        self.sel_frozen = False
        self.rect_anchor = None
        self.rect_current = None
        self.sel_points = []

        # Crosshair cursor and focus for key events
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()

        # Tell SelectionManager to start tracking
        self.sel_mgr.start(mode, min_dist=2)
        self.update()

    # Reset and exit selection mode
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

        # Restore normal cursor and repaint
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()


    # Get the image's displayed rectangle in the widget (scaled + offset)
    def image_rect_on_widget(self) -> QRect:

        # No image loaded
        if not self.image or self.image.isNull():
            return QRect()

        # Scaled image size
        sw = int(self.image.width() * self.zoom_scale)
        sh = int(self.image.height() * self.zoom_scale)

        # Centered position + panning offset
        x = int((self.width() - sw) / 2 + self.offset.x())
        y = int((self.height() - sh) / 2 + self.offset.y())

        return QRect(x, y, sw, sh)


    # Convert widget coordinates to image coordinates
    def widget_to_image(self, p: QPoint):

        # No image loaded
        if not self.image or self.image.isNull():
            return None


        r = self.image_rect_on_widget()
        if not r.contains(p):               # Click is outside the image area
            return None

        # Map from widget space to image space
        ix = (p.x() - r.x()) / self.zoom_scale
        iy = (p.y() - r.y()) / self.zoom_scale

        # Clamp to valid image bounds
        ix = max(0, min(int(ix), min(self.image.width() - 1, int(ix))))
        iy = max(0, min(int(iy), min(self.image.height() - 1, int(iy))))

        return QPoint(ix, iy)

    # Convert image coordinates to widget coordinates
    def image_to_widget(self, p: QPoint) -> QPoint:
        r = self.image_rect_on_widget()                 # image position/size on the widget
        wx = int(r.x() + p.x() * self.zoom_scale)
        wy = int(r.y() + p.y() * self.zoom_scale)
        return QPoint(wx, wy)


    # Handle keyboard input
    def keyPressEvent(self, event):

        # Handle keys when a selection is active
        if self.sel_active and self.sel_mode in ("rect", "lasso", "poly"):
            # ENTER pressed
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # Case A: Selection is frozen and operation is waiting
                if self.sel_frozen and self.pending_op:
                    op, params = self.pending_op  # params is a dict of options


                    pix = self.pixmap()
                    if pix is None:
                        self.pending_op = None
                        return

                    # Convert current pixmap BGR image
                    bgr = imf.qpixmap_to_cv2(pix)

                    # If conversion failed, cancel selection
                    if bgr is None:
                        self.pending_op = None
                        return


                    if op == "crop":
                        # crop via SelectionManager
                        out = self.sel_mgr.crop(bgr, **params) if hasattr(self.sel_mgr, "crop") else None
                        if out is not None:
                            self.set_cv2_image(out)
                        # clear op and exit selection
                        self.pending_op = None
                        self.cancel_selection()
                    return

                # Case B: not frozen yet -> freeze (build active_mask) and allow panning
                if not self.sel_mgr.state.frozen:

                    # Freeze selection and build mask
                    if self.sel_mgr.freeze():
                        self.sel_frozen = True

                        pix = self.pixmap()
                        if pix is None:
                            self.cancel_selection()
                            return

                        # Convert current pixmap BGR image
                        bgr = imf.qpixmap_to_cv2(pix)

                        # If conversion failed, cancel selection
                        if bgr is None:
                            self.cancel_selection()
                            return

                        # Build mask matching image size
                        h, w = bgr.shape[:2]
                        self.active_mask = self.sel_mgr.mask((h, w))

                        # No edits done since we froze the selection
                        self.ops_since_freeze = False

                        # Switch to panning with a normal cursor
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                        self.panning = True
                        self.update()
                return

            # Escape pressed: cancel selection and pending operation
            if event.key() == Qt.Key.Key_Escape:
                self.pending_op = None
                self.cancel_selection()
                return

        # Let the base class handle other keys
        super().keyPressEvent(event)

    # Get selection bounds in image coords
    def selection_bounds_image(self):

        # Require active selection and points
        if not (self.sel_active and self.rect_anchor and self.rect_current):
            return None

        # Get raw coordinates
        x1, y1 = self.rect_anchor.x(), self.rect_anchor.y()
        x2, y2 = self.rect_current.x(), self.rect_current.y()


        # Sort so x1 < x2, y1 < y2
        x1, x2 = sorted((int(x1), int(x2)))
        y1, y2 = sorted((int(y1), int(y2)))


        # Ignore empty / inverted selection
        if x2 <= x1 or y2 <= y1:
            return None
        return (x1, y1, x2, y2)


    # Get current image as BGR (cv2)
    def get_cv2_image(self):
        pix = self.pixmap()
        if pix is None or pix.isNull():
            return None
        return imf.qpixmap_to_cv2(pix)


    # Update the canvas with a new OpenCV BGR image
    def set_cv2_image(self, bgr):

        # Convert OpenCV BGR image to QPixmap and set as the current image
        self.set_image(imf.cv2_to_qpixmap(bgr))

        # Emit current color
        self.colorPicked.emit(self.pen_color)

        # Enable panning
        self.panning = True