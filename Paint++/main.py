# Install pyqt6,pyqt6-tools
import os
from img_canvas import Img_Canvas
import cv2
import numpy as np
import sys
from image_menu_functions import imf
from tools_menu_functions import tools

# imports different classes from the PyQt library
from PyQt6.QtCore import QSizeF, QSize
from PyQt6 import QtGui
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QImageReader, QImage, QImageIOHandler, QImageWriter
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QMainWindow,
    QLabel,
    QMenu,
    QCheckBox,
    QStatusBar,
    QToolBar, QStyle, QFileDialog, QMessageBox, QScrollArea, QVBoxLayout, QLayout
)

def main():

    # creates an object from the QApplication class (classname() means to create object)
    app = QApplication(sys.argv)

    # creates an object from the QWidget class
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default, so calle the show method
    window.file_menu()
    window.edit_menu()
    window.image_menu()
    window.tools_menu()
    app.exec()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint++")
        self.resize(1000, 1000)


        self.scroll = QScrollArea()

        container = QWidget()
        layout = QVBoxLayout(container)

        self.canvas = Img_Canvas(container)
        self.imf = imf(self.canvas)
        self.tools = tools(self.canvas)

        layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll.setWidget(container)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.current_path = None

    # this is a test-branch for git/pr

    #### This method creates the dropdown menu for File #####
    #### It does not contain the operations of the buttons #####
    def file_menu(self):

        menu = self.menuBar()

        ##### New button to create a new image ####
        new_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon), "New", self)
        new_.triggered.connect(self.toolbar_button_clicked)

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
        properties.triggered.connect(self.toolbar_button_clicked)

        ##### Quit Button in File-menu #####
        quit_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop), "Exit Program", self)
        quit_.triggered.connect(self.toolbar_button_clicked)

        ##### Adds the Buttons to the menu #####
        file_menu = menu.addMenu("&File")
        file_menu.addAction(new_)
        file_menu.addAction(open_)
        file_menu.addAction(save)
        file_menu.addAction(save_as)
        file_menu.addAction(properties)
        file_menu.addAction(quit_)

    def edit_menu(self):
        menu = self.menuBar()

        edit_menu = menu.addMenu("&Edit")

## 2.Clipboard (menu with the following options:Copy, paste and Cut)
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

        edit_menu.addAction(paste_action)
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)

    def image_menu(self):
        # Makes Image menu
        menu = self.menuBar()
        image_menu = menu.addMenu("&Image")

        # Makes select submenu
        select_menu = QMenu("&Select", self)
        image_menu.addMenu(select_menu)
        rectangular = QAction(QIcon("icons/icons8-rectangular.svg"), "Rectangular", self)
        lasso = QAction(QIcon("icons/icons8-lasso.svg"), "Lasso", self)
        polygon = QAction(QIcon("icons/icons8-polygon.svg"), "Polygon", self)
        select_menu.addAction(rectangular)
        select_menu.addAction(lasso)
        select_menu.addAction(polygon)

        # Makes Cropping and resizing
        crop = QAction(QIcon("icons/icons8-crop.svg"), "Crop", self)
        crop.triggered.connect(self.imf.selective_crop)

        resize = QAction(QIcon("icons/icons8-resize.svg"), "Resize", self)
        resize.triggered.connect(self.imf.resize)

        image_menu.addAction(crop)
        image_menu.addAction(resize)

        # Makes Orientation submenu
        orientation_menu = QMenu("&Orientation", self)
        image_menu.addMenu(orientation_menu)

        rotate_right = QAction(QIcon("icons/icons8-rotate_right.svg"), "Rotate right", self)
        rotate_right.triggered.connect(self.imf.rotate_CW)

        rotate_left = QAction(QIcon("icons/icons8-rotate_left.svg"), "Rotate left", self)
        rotate_left.triggered.connect(self.imf.rotate_CCW)

        flip_horizontal = QAction(QIcon("icons/icons8-flip_horizontal.svg"), "Flip horizontal", self)
        flip_horizontal.triggered.connect(self.imf.flip_horizontal)

        flip_vertical = QAction(QIcon("icons/icons8-flip_vertical.svg"), "Flip vertical", self)
        flip_vertical.triggered.connect(self.imf.flip_vertical)

        orientation_menu.addAction(rotate_right)
        orientation_menu.addAction(rotate_left)
        orientation_menu.addAction(flip_horizontal)
        orientation_menu.addAction(flip_vertical)

    def tools_menu(self):
        menu = self.menuBar()
        tools_menu = menu.addMenu("&Tools")

        zoom = QAction(QIcon("icons/icons8-zoom.svg"), "Zoom", self)
        zoom.triggered.connect(self.tools.zoom)

        draw = QAction(QIcon("icons/icons8-draw.svg"), "Draw", self)
        draw.triggered.connect(self.tools.lasso_draw)

        tools_menu.addAction(draw)
        tools_menu.addAction(zoom)

    def toolbar_button_clicked(self, s):
        print("click", s)

    def current_qimage(self):
        pm = self.canvas.pixmap()
        return None if pm is None else pm.toImage()

    def write_image(self, path: str, fmt: bytes | None):
        img = self.current_qimage()
        if img is None:
            QMessageBox.information(self, "Nothing to save", "Load or create an image first.")
            return False

        writer = QImageWriter(path, fmt  if fmt else b"")
        ok = writer.write(img)
        if not ok:
            QMessageBox.critical(self, "Save Failed", writer.errorString() or "Unkown error.")
            return False

        self.current_path = path
        self.status.showMessage(f"Saved: {os.path.basename(path)}")
        return True

    def open_file(self):
       fmts = sorted(set(bytes(f).decode("ascii").lower() for f in QImageReader.supportedImageFormats()))
       file_filter = "Images (" + " ".join(f"*.{ext}" for ext in fmts) + ");;All Files (*)"

       path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", file_filter)
       if not path:
           return

       reader = QImageReader(path)
       reader.setAutoTransform(True)
       img = reader.read()
       if img.isNull():
           QMessageBox.critical(self, "Open Image Failed", f"{reader.errorString()}\n\nFile: {path}")
           return

       pix = QPixmap.fromImage(img)
       if pix.isNull():
           QMessageBox.critical(self, "Open Image Failed", f"Loaded QImage but QPixmap is null. \nFile: {path}")
           return

       name = os.path.basename(path)
       self.status.showMessage(f"Opened: {name} -  {pix.width()}x{pix.height()} px")
       self.setWindowTitle(f"Paint++ - {name}")

       self.canvas.set_image(pix)
       vp = self.scroll.viewport().size()
       desired = QSize(max(pix.width(), vp.width()), max(pix.height(), vp.height()))
       self.canvas.resize(desired)
       self.current_path = path

    def save(self):
        if not self.current_path:
            self.save_as()
            return

        ext = os.path.splitext(self.current_path)[1].lower().lstrip(".")
        fmt = ext.encode("ascii") if ext else None
        self.write_image(self.current_path, fmt)

    def save_as(self):
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

        if os.path.exists(path):
            resp = QMessageBox.question(self, "Overwrite?", f"{os.path.basename(path)} exists. Overwrite?")
            if resp != QMessageBox.StandardButton.Yes:
                return

        if self.write_image(path, fmt):
            self.setWindowTitle(f"Paint++ - {os.path.basename(path)}")

if __name__ == '__main__':
    main()