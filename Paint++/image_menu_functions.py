# image_menu_functions.py
import cv2
import numpy as np
from PyQt6.QtGui import QPixmap, QImage

class imf:
    """Image manipulation tools for Paint++ (rotate, flip, resize, etc.)"""

    def __init__(self, canvas):
        # canvas = your Img_Canvas object (so we can access self.canvas.pixmap())
        self.canvas = canvas

    @staticmethod
    def cv2_to_qpixmap(bgr):
        if bgr is None:
            return QPixmap()
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        return QPixmap.fromImage(qimg)

    @staticmethod
    def qpixmap_to_cv2(pixmap):
        if pixmap.isNull():
            return None
        qimg = pixmap.toImage().convertToFormat(QImage.Format.Format_RGB888)
        w = qimg.width()
        h = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(h * w * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 3))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return bgr

    # === ROTATE ===
    def rotate_CW(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.qpixmap_to_cv2(pix)
        cv = cv2.rotate(cv, cv2.ROTATE_90_CLOCKWISE)
        self.canvas.set_image(self.cv2_to_qpixmap(cv))

    def rotate_CCW(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.qpixmap_to_cv2(pix)
        cv = cv2.rotate(cv, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.canvas.set_image(self.cv2_to_qpixmap(cv))

    # === FLIP ===
    def flip_horizontal(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.qpixmap_to_cv2(pix)
        cv = cv2.flip(cv, 1)
        self.canvas.set_image(self.cv2_to_qpixmap(cv))

    def flip_vertical(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.qpixmap_to_cv2(pix)
        cv = cv2.flip(cv, 0)
        self.canvas.set_image(self.cv2_to_qpixmap(cv))

    def selective_crop(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.qpixmap_to_cv2(pix)
        r = cv2.selectROI("Crop select", cv)
        crop_image = cv[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        cv2.destroyWindow("Crop select")
        self.canvas.set_image(self.cv2_to_qpixmap(crop_image))

    def resize(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.qpixmap_to_cv2(pix)
        # Lag widget for å velge resize størrelse!
        image_resize = cv2.resize(cv, (500, 500))
        self.canvas.set_image(self.cv2_to_qpixmap(image_resize))
