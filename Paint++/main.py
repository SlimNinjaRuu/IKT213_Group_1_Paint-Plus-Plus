import os
import sys
import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QImageReader, QImageWriter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QStatusBar, QStyle,
    QFileDialog, QMessageBox, QScrollArea, QMenu
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint++")
        self.setMinimumSize(400, 300)
        self.resize(900, 600)

        self.image_label = QLabel("No image loaded", alignment=Qt.AlignmentFlag.AlignCenter)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.image_label)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.current_path = None

    # --- Menyer ---
    def file_menu(self):
        menu = self.menuBar()

        new_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon), "New", self)
        new_.triggered.connect(self.toolbar_button_clicked)

        open_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open", self)
        open_.triggered.connect(self.open_file)

        save = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save", self)
        save.triggered.connect(self.save)
        save.setShortcut(QKeySequence.StandardKey.Save)

        save_as = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save as", self)
        save_as.triggered.connect(self.save_as)
        save_as.setShortcut(QKeySequence.StandardKey.SaveAs)

        properties = QAction(QIcon("icons/icons8-settings.svg"), "Settings", self)
        properties.triggered.connect(self.toolbar_button_clicked)

        quit_ = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop), "Exit Program", self)
        quit_.triggered.connect(self.close)

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

        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        cut_action = QAction("Cut", self)

        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(cut_action)

    def image_menu(self):
        menu = self.menuBar()
        image_menu = menu.addMenu("&Image")

        select_menu = QMenu("&Select", self)
        image_menu.addMenu(select_menu)

        rectangular = QAction(QIcon("icons/icons8-rectangular.svg"), "Rectangular", self)
        lasso = QAction(QIcon("icons/icons8-lasso.svg"), "Lasso", self)
        polygon = QAction(QIcon("icons/icons8-polygon.svg"), "Polygon", self)

        select_menu.addAction(rectangular)
        select_menu.addAction(lasso)
        select_menu.addAction(polygon)

        crop = QAction(QIcon("icons/icons8-crop.svg"), "Crop", self)
        resize = QAction(QIcon("icons/icons8-resize.svg"), "Resize", self)
        image_menu.addAction(crop)
        image_menu.addAction(resize)

        orientation_menu = QMenu("&Orientation", self)
        image_menu.addMenu(orientation_menu)

        rotate_right = QAction(QIcon("icons/icons8-rotate_right.svg"), "Rotate right", self)
        rotate_left = QAction(QIcon("icons/icons8-rotate_left.svg"), "Rotate left", self)
        flip_horizontal = QAction(QIcon("icons/icons8-flip_horizontal.svg"), "Flip horizontal", self)
        flip_vertical = QAction(QIcon("icons/icons8-flip_vertical.svg"), "Flip vertical", self)

        orientation_menu.addAction(rotate_right)
        orientation_menu.addAction(rotate_left)
        orientation_menu.addAction(flip_horizontal)
        orientation_menu.addAction(flip_vertical)

    # --- Funksjoner ---
    def toolbar_button_clicked(self):
        print("click")

    def current_qimage(self):
        pm = self.image_label.pixmap()
        if pm is None:
            return None
        return pm.toImage()

    def write_image(self, path: str, fmt: bytes | None):
        img = self.current_qimage()
        if img is None:
            QMessageBox.information(self, "Nothing to save", "Load or create an image first.")
            return False

        writer = QImageWriter(path, fmt if fmt else b"")
        ok = writer.write(img)
        if not ok:
            QMessageBox.critical(self, "Save Failed", writer.errorString() or "Unknown error.")
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
        self.image_label.setPixmap(pix)
        self.image_label.adjustSize()

        name = os.path.basename(path)
        self.status.showMessage(f"Opened: {name} - {pix.width()}x{pix.height()} px")
        self.setWindowTitle(f"Paint++ - {name}")

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

        suggested = self.current_path or ""
        path, _ = QFileDialog.getSaveFileName(self, "Save Image As", suggested, file_filter)
        if not path:
            return

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


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.file_menu()
    window.edit_menu()
    window.image_menu()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
