import sys, cv2
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QAction, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QStyle, QMessageBox

def cv2_to_qpixmap(bgr):
    if bgr is None:
        return QPixmap()
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(qimg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application")
        self.setMinimumSize(QSize(400, 300))

        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image_label)

        self._bgr = None  # store OpenCV image
        self.image_menu()
        self.tools_menu()

    def button_clicked(self):
        bgr = cv2.imread("../100.jpg")
        if bgr is None:
            QMessageBox.critical(self, "Error", "Could not load 100.jpg")
            return
        self._bgr = bgr
        self.image_label.setPixmap(cv2_to_qpixmap(self._bgr))

    def rotate(self):
        if self._bgr is None:
            return
        self._bgr = cv2.rotate(self._bgr, cv2.ROTATE_90_CLOCKWISE)
        self.image_label.setPixmap(cv2_to_qpixmap(self._bgr))

    def image_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&Image")
        act_open = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Open", self)
        act_open.triggered.connect(self.button_clicked)
        file_menu.addAction(act_open)

    def tools_menu(self):
        menu = self.menuBar()
        tools_menu = menu.addMenu("&Tools")
        act_rotate = QAction("Rotate 90°", self)
        act_rotate.triggered.connect(self.rotate)  # <-- correct connection
        tools_menu.addAction(act_rotate)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
