import os

# imports different classes from the PyQt library
from PyQt6.QtCore import QSizeF, QSize
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtCore import *
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QImageReader, QImage, QImageIOHandler, QImageWriter
from PyQt6.QtGui import QPainter, QPixmap, QColor, QBrush, QPen, QImageReader
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QDockWidget,
    QMainWindow,
    QFrame,
    QMenu,
    QColorDialog,
    QCheckBox,
    QStatusBar,
    QToolBar, QStyle, QFileDialog, QMessageBox, QScrollArea, QVBoxLayout, QLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QTabWidget, QDialog)
from img_canvas import Img_Canvas
from image_menu_functions import imf

import sys

def main():

    # creates an object from the QApplication class (classname() means to create object)
    app = QApplication(sys.argv)

    # creates an object from the QWidget class
    window = MainWindow()
    window.show()
    window.file_menu()
    window.edit_menu()
    window.image_menu()
    window.tools_menu()
    window.shapes_menu()
    app.exec()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint++")
        self.resize(1920, 1080)
        self.panning = True
        self.canvas = Img_Canvas(imf)                                  # Creates an instance of the canvas class
        self.canvas.colorPicked.connect(self.on_color_picked)
        self.scroll = QScrollArea()                                 # Creates a scroll area

        self.imf = imf(self.canvas)
        self.undo_history = []                                      # List to store previous image states for undo function

        self.scroll.setWidget(self.canvas)                          # Puts the canvas inside the scroll area
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.scroll)                          # Makes tbe scroll are the main content

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.current_path = None                                    # Tracks current file path

        # Create a dock panel
        dock = QDockWidget("", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        tool_panel = QWidget()
        layout = QVBoxLayout(tool_panel)

        # Add checkbox
        self.cb_shape_fill = QCheckBox("Shape fill")
        layout.addWidget(self.cb_shape_fill)

        dock.setWidget(tool_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        self.cb_shape_fill.stateChanged.connect(self.canvas.set_fill_enabled)

        # Color preview box
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(60, 60)
        self.color_preview.setStyleSheet("background-color: black; border: 1px solid #333; border-radius: 4px;")

        layout.addSpacing(60)

        # PyQt6 (horizontal centering)
        layout.addWidget(self.color_preview, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)

    def update_color_preview(self, color: QColor):
        self.color_preview.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #333; border-radius: 4px;"
        )

    def on_color_picked(self, color: QColor):
        # Update pen color in canvas
        self.canvas.pen_color = color

        # Update preview box
        self.update_color_preview(color)

        # Optional: show message in status bar
        self.status.showMessage(f"Picked color: {color.name()}", 2000)

    #### Undo Functions
    def save_state(self):

        pixmap = self.canvas.pixmap()
        if pixmap and not pixmap.isNull():
            self.undo_history.append(pixmap.copy())                 # Make a copy and add to history


    # Undo the last action
    def undo(self):
        if len(self.undo_history) < 2:
            self.status.showMessage("Nothing to undo")
            return

        self.undo_history.pop()                                     # Remove current state

        previous = self.undo_history[-1]
        self.canvas.set_image(previous.copy())
        self.status.showMessage(f"Undo successfull. {len(self.undo_history) - 1} undos remaining")



    #### This method creates the dropdown menu for File #####
    #### It does not contain the operations of the buttons #####
    def file_menu(self):

        menu = self.menuBar()

        ##### New button to create a new image ####
        new_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon), "New", self)
        new_.triggered.connect(self.open_new_instance)

        ##### Open file in File-menu #####
        open_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open", self)
        open_.triggered.connect(self.open_file)

        ##### Save Button in File-menu #####
        save = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save", self)
        save.triggered.connect(self.save)
        save.setShortcut(QKeySequence.StandardKey.Save)

        ##### Save as Button in File-menu #####
        save_as = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save as", self)
        save_as.triggered.connect(self.save_as)
        save_as.setShortcut(QKeySequence.StandardKey.SaveAs)

        ##### Properties Button in File-menu
        properties = QAction(QIcon("icons/icons8-settings.svg"), "Settings", self)
        properties.triggered.connect(self.open_properties_dialog)

        ##### Quit Button in File-menu #####
        quit_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop), "Exit Program", self)
        quit_.triggered.connect(self.exit_program)

        ##### Adds the Buttons to the menu #####
        file_menu = menu.addMenu("&File")
        file_menu.addAction(new_)
        file_menu.addAction(open_)
        file_menu.addAction(save)
        file_menu.addAction(save_as)
        file_menu.addAction(properties)
        file_menu.addAction(quit_)

    def open_properties_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")

        layout = QVBoxLayout(dlg)

        btn_canvas = QPushButton("Canvas Size..", dlg)
        btn_canvas.clicked.connect(lambda: self.canvas.resize_canvas())
        layout.addWidget(btn_canvas)

        btn_close = QPushButton("Close", dlg)
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)

        dlg.setLayout(layout)
        dlg.resize(QSize(600, 600))
        dlg.exec()

    def open_new_instance(self):
        import subprocess, sys, os
        script = os.path.abspath(sys.argv[0])
        QProcess.startDetached(sys.executable, [script])


    def exit_program(self):
        QApplication.quit()

    def edit_menu(self):
        menu = self.menuBar()

        edit_menu = menu.addMenu("&Edit")

        # Adds an undo button
        undo_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack),
            "Undo",
            self,
        )
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)                  # Adds Ctrl+Z
        undo_action.triggered.connect(self.undo)

        edit_menu.addAction(undo_action)
        edit_menu.addSeparator()

        # 2.Clipboard (menu with the following options:Copy, paste and Cut)
        edit_menu.addSection("Clipboard")


        # Edit function
        copy_action = QAction(
            QIcon.fromTheme(
                "Edit-Copy",
                self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ),
            "Copy",
            self,
        )
        copy_action.setShortcut(QKeySequence.StandardKey.Copy) # copy function
        copy_action.triggered.connect(self.toolbar_button_clicked)

        paste_action = QAction(
            QIcon.fromTheme(
                "Edit-Paste",
                self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart),
            ),
            "Paste",
            self,
        )
        paste_action.setShortcut(QKeySequence.StandardKey.Paste) #paste function
        paste_action.triggered.connect(self.toolbar_button_clicked)

        cut_action = QAction(
            QIcon.fromTheme(
                "Edit-Cut",
                self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogEnd),
            ),
            "Cut",
            self,
        )
        cut_action.setShortcut(QKeySequence.StandardKey.Cut) #cut function
        cut_action.triggered.connect(self.toolbar_button_clicked)

        # Allows user to change the canvas size, uses the resize_canvas method from img_canvas
        canvas_size = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Canvas Size", self)
        canvas_size.triggered.connect(self.canvas.resize_canvas)

        edit_menu.addAction(paste_action)
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(canvas_size)


    def image_menu(self):
        # Makes Image menu
        menu = self.menuBar()
        image_menu = menu.addMenu("&Image")

        # Makes select submenu
        select_menu = QMenu("&Select", self)
        image_menu.addMenu(select_menu)
        rectangular = QAction(QIcon("icons/icons8-rectangular.svg"), "Rectangular", self)
        rectangular.triggered.connect(lambda : [self.save_state(), self.canvas.start_selection("rect"), self.canvas.setFocus()])

        lasso = QAction(QIcon("icons/icons8-lasso.svg"), "Lasso", self)
        lasso.triggered.connect(lambda : self.canvas.start_selection("lasso"))

        polygon = QAction(QIcon("icons/icons8-polygon.svg"), "Polygon", self)
        polygon.triggered.connect(lambda : self.canvas.start_selection("poly"))


        select_menu.addAction(rectangular)
        select_menu.addAction(lasso)
        select_menu.addAction(polygon)

        # Makes Cropping and resizing
        crop = QAction(QIcon("icons/icons8-crop.svg"), "Crop", self)
        crop.triggered.connect(lambda: [self.save_state(), self.imf.request_crop(strict=False)])
        image_menu.addAction(crop)

        strict_crop = QAction(QIcon("icons/icons8-crop.svg"), "Strict Crop", self)
        strict_crop.triggered.connect(lambda: [self.save_state(), self.imf.request_crop(strict=True)])
        image_menu.addAction(strict_crop)

        resize = QAction(QIcon("icons/icons8-resize.svg"), "Resize", self)
        resize.triggered.connect(lambda :[self.save_state(), self.imf.resize()])

        image_menu.addAction(crop)
        image_menu.addAction(resize)

        # Makes Orientation submenu
        orientation_menu = QMenu("&Orientation", self)
        image_menu.addMenu(orientation_menu)

        rotate_right = QAction(QIcon("icons/icons8-rotate_right.svg"), "Rotate right", self)
        rotate_right.triggered.connect(lambda: [self.save_state(), self.imf.rotate_CW()])

        rotate_left = QAction(QIcon("icons/icons8-rotate_left.svg"), "Rotate left", self)
        rotate_left.triggered.connect(lambda :[self.save_state(), self.imf.rotate_CCW()])

        flip_horizontal = QAction(QIcon("icons/icons8-flip_horizontal.svg"), "Flip horizontal", self)
        flip_horizontal.triggered.connect(lambda :[self.save_state(),self.imf.flip_horizontal()])

        flip_vertical = QAction(QIcon("icons/icons8-flip_vertical.svg"), "Flip vertical", self)
        flip_vertical.triggered.connect(lambda :[self.save_state(),self.imf.flip_vertical()])

        orientation_menu.addAction(rotate_right)
        orientation_menu.addAction(rotate_left)
        orientation_menu.addAction(flip_horizontal)
        orientation_menu.addAction(flip_vertical)

    def shapes_menu(self):
        menu = self.menuBar()
        shape_menu = menu.addMenu("&Shapes")

        rect = QAction(QIcon("icons/icons8-paint.svg"), "Rectangle", self)
        rect.triggered.connect(self.canvas.toggle_rect_mode)

        ellipse = QAction(QIcon("icons/icons8-paint.svg"), "Ellipse", self)
        ellipse.triggered.connect(self.canvas.toggle_ellipse_mode)

        triangle = QAction(QIcon("icons/icons8-paint.svg"), "Triangle", self)
        triangle.triggered.connect(self.canvas.toggle_triangle_mode)

        shape_menu.addAction(rect)
        shape_menu.addAction(ellipse)
        shape_menu.addAction(triangle)


    def tools_menu(self):
        menu = self.menuBar()
        tools_menu = menu.addMenu("&Tools")

        panning = QAction("Move", self)
        panning.triggered.connect(self.canvas.toggle_panning_mode)

        zoom_in = QAction(QIcon("icons/icons8-zoom.svg"), "Zoom In", self)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.triggered.connect(self.canvas.zoom_in)

        zoom_out = QAction(QIcon("icons/icons8-zoom.svg"), "Zoom out", self)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(self.canvas.zoom_out)

        reset_zoom = QAction("Reset Zoom")
        reset_zoom.setShortcut("Ctrl+0")
        reset_zoom.triggered.connect(self.canvas.reset_zoom)

        tools_menu.addAction(panning)
        tools_menu.addAction(zoom_in)
        tools_menu.addAction(zoom_out)
        tools_menu.addAction(reset_zoom)

        # Adding paint Submenu
        paint_menu = QMenu("&Paint", self)
        tools_menu.addMenu(paint_menu)

        paint = QAction(QIcon("icons/icons8-paint.svg"), "Brush", self)
        # paint.setCheckable(True)
        paint.triggered.connect(self.canvas.toggle_brush_mode)

        spray = QAction(QIcon("icons/icons8-spray.svg"), "Spray", self)
        # spray.setCheckable(True)
        spray.triggered.connect(self.canvas.toggle_spray_mode)

        text = QAction(QIcon("icons/icons8-text.svg"), "Text", self)
        text.triggered.connect(self.canvas.toggle_text_mode)

        color_pick = QAction("Color Picker", self)
        color_pick.triggered.connect(self.canvas.color_picker)

        paint_menu.addAction(paint)
        paint_menu.addAction(spray)
        paint_menu.addAction(text)
        paint_menu.addAction(color_pick)

    def update_zoom_status(self):
        if self.canvas.image:
            zoom_percent = self.canvas.get_zoom_percent()
            self.status.showMessage(f"Zoom: {zoom_percent}%")

    def toolbar_button_clicked(self, s):
        print("click", s)

    def current_qimage(self):
        if self.canvas.image is None:
            return None
        return self.canvas.image.toImage()

    ##### Actually saves the file #####
    def write_image(self, path: str, fmt: bytes | None):


        img = self.current_qimage()             # Get Current image
        if img is None:
            QMessageBox.information(self, "Nothing to save", "Load or create an image first.")
            return False

        writer = QImageWriter(path, fmt  if fmt else b"")
        ok = writer.write(img)                  # Write to disk
        if not ok:
            QMessageBox.critical(self, "Save Failed", writer.errorString() or "Unkown error.")
            return False

        self.current_path = path
        self.status.showMessage(f"Saved: {os.path.basename(path)}")
        return True

    def open_file(self):

        # Get supported formats
       fmts = sorted(set(bytes(f).decode("ascii").lower() for f in QImageReader.supportedImageFormats()))
       file_filter = "Images (" + " ".join(f"*.{ext}" for ext in fmts) + ");;All Files (*)"


        # Show file dialog
       path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", file_filter)

        # User cancelled
       if not path:
           return

       reader = QImageReader(path)      # Try to read the image
       reader.setAutoTransform(True)    # Auto-rotate based on EXIF data
       img = reader.read()
       if img.isNull():                 # Failed to load
           QMessageBox.critical(self, "Open Image Failed", f"{reader.errorString()}\n\nFile: {path}")
           return


        # Convert to Qpixmap for Display
        # Use img for pixel processing like filters
       pix = QPixmap.fromImage(img)
       if pix.isNull():
           QMessageBox.critical(self, "Open Image Failed", f"Loaded QImage but QPixmap is null. \nFile: {path}")
           return

        # Update UI
       name = os.path.basename(path)
       self.status.showMessage(f"Opened: {name} -  {pix.width()}x{pix.height()} px")
       self.setWindowTitle(f"Paint++ - {name}")


        # Send Image to Canvas
       self.canvas.set_image(pix)                       # Calls the set_image method from img_canvas
       self.scroll.horizontalScrollBar().setValue(0)
       self.scroll.verticalScrollBar().setValue(0)

       self.current_path = path

       # Saves initial state for undo
       self.undo_history.clear()                        # Clear old history
       self.save_state()                                # Saves state of newly opened image


    def save(self):
        if not self.current_path:                       # Never saved before?
            self.save_as()                              # Ask Where to Save
            return

        # Get File extensions
        ext = os.path.splitext(self.current_path)[1].lower().lstrip(".")
        fmt = ext.encode("ascii") if ext else None
        self.write_image(self.current_path, fmt)        # Do the Actual Save



    def save_as(self):

        # Get supported write formats
        fmts = sorted(set(bytes(f).decode("ascii").lower() for f in QImageWriter.supportedImageFormats()))
        pattern = " ".join(f"*.{ext}" for ext in fmts)
        file_filter = f"Images ({pattern});;All Files (*)"

        # Sugest same dir name when possible
        suggested = self.current_path or ""
        path, selected_filter = QFileDialog.getSaveFileName(self, "Save Image As", suggested, file_filter)
        if not path:
            return

        # Ensure an extensinon, .png as default
        root, ext = os.path.splitext(path)
        if not ext:
            ext = ".png"
            path = root + ext


        fmt = ext.lstrip(".").lower().encode("ascii")

        # Check if overwrtiting
        if os.path.exists(path):
            resp = QMessageBox.question(self, "Overwrite?", f"{os.path.basename(path)} exists. Overwrite?")
            if resp != QMessageBox.StandardButton.Yes:
                return

        if self.write_image(path, fmt):
            self.setWindowTitle(f"Paint++ - {os.path.basename(path)}")

if __name__ == '__main__':
    main()