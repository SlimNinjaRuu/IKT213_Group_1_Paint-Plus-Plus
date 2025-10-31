# image_menu_functions.py
import cv2
import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QInputDialog, QMessageBox

class imf:
    """Image manipulation tools for Paint++ (rotate, flip, resize, etc.)"""

    def __init__(self, canvas):
        # canvas = your Img_Canvas object (so we can access self.canvas.pixmap())
        self.canvas = canvas

    @staticmethod
    def cv2_to_qpixmap(bgr):
        # If cv2 picture is none return without doing convertion
        if bgr is None:
            return QPixmap()

        bgr = bgr.copy()

        # takes the cv2 bgr image and makes it rgb image
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        height, width, channels =  rgb.shape
        bytes_per_line = width * channels

        # makes rgb to QImage
        qimg = QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # returns Qpixmap from QImage
        return QPixmap.fromImage(qimg.copy())

    @staticmethod
    def qpixmap_to_cv2(pixmap):
        # If QPixmap is none return without doing conversion
        if pixmap.isNull():
            return None

        # Makes a QImage in rgb from QPixmap
        qimg = pixmap.toImage().convertToFormat(QImage.Format.Format_RGB888)

        # QImage height and width
        w = qimg.width()
        h = qimg.height()
        bytes_per_line = qimg.bytesPerLine()

        # Will make a deep copy
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())

        # Creates numpy array from, QImage
        arr = np.frombuffer(ptr, np.uint8).reshape((h, bytes_per_line))

        arr = arr[:, :w*3].reshape((h, w, 3))

        # Converts RGB array to BGR and returns it
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return bgr.copy()

    # === ROTATE ===
    def rotate_CW(self):
        # Gets the QPixmap
        pix = self.canvas.pixmap()

        # Does not rotate if QPixmap is empty, returns
        if not pix or pix.isNull():
            return

        # Makes a bgr
        cv = self.qpixmap_to_cv2(pix)

        # Rotates the bgr in cv2
        cv = cv2.rotate(cv, cv2.ROTATE_90_CLOCKWISE)

        # Makes a QPixmap of rotated bgr
        qpix = self.cv2_to_qpixmap(cv)

        # Sets  the rotated QPixmap as canvas
        self.canvas.set_image(qpix)

    def rotate_CCW(self):
        # Gets the QPixmap
        pix = self.canvas.pixmap()

        # Does not rotate if QPixmap is empty, returns
        if not pix or pix.isNull():
            return

        # Makes a bgr
        cv = self.qpixmap_to_cv2(pix)

        # Rotates the bgr in cv2
        cv = cv2.rotate(cv, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Makes a QPixmap of rotated bgr
        qpix = self.cv2_to_qpixmap(cv)

        # Sets the rotated QPixmap as canvas
        self.canvas.set_image(qpix)

    # === FLIP ===
    def flip_horizontal(self):
        # Gets the QPixmap
        pix = self.canvas.pixmap()

        # Does not flip if QPixmap is empty, returns
        if not pix or pix.isNull():
            return

        # Makes a bgr
        cv = self.qpixmap_to_cv2(pix)

        # Flips the bgr in cv2
        cv = cv2.flip(cv, 1)

        # Makes QPixmap of flipped bgr
        qpix = self.cv2_to_qpixmap(cv)

        # Sets the flipped QPixmap as canvas
        self.canvas.set_image(qpix)

    def flip_vertical(self):
        # Gets the QPixmap
        pix = self.canvas.pixmap()

        # Does not flip if QPixmap is empty, returns
        if not pix or pix.isNull():
            return

        # Makes a bgr
        cv = self.qpixmap_to_cv2(pix)

        # Flips the bgr in cv2
        cv = cv2.flip(cv, 0)

        # Makes QPixmap of flipped bgr
        qpix = self.cv2_to_qpixmap(cv)

        # Sets the flipped QPixmap as canvas
        self.canvas.set_image(qpix)

    def selective_crop(self):
        # Gets the QPixmap
        pix = self.canvas.pixmap()

        # Does not crop if QPixmap is empty, returns
        if not pix or pix.isNull():
            return

        # Makes a bgr
        cv = self.qpixmap_to_cv2(pix)

        # User selects ROI
        r = cv2.selectROI("Crop select", cv)

        # Crops the image over the selected ROI
        crop_image = cv[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        cv2.destroyWindow("Crop select")

        # Makes QPixmap of cropped bgr
        qpix = self.cv2_to_qpixmap(crop_image)

        # Sets the cropped QPixmap as canvas
        self.canvas.set_image(qpix)
    def resize(self):

        pix = self.canvas.pixmap()

        if self.canvas.image is None or self.canvas.image.isNull():
            QMessageBox.information(None, "No Image, Image must be loaded first")
            return

        # Get current image dimensions
        current_width = self.canvas.width()
        current_height = self.canvas.height()

        # Ask for new width
        width, ok1 = QInputDialog.getInt(
            None,
            "Resize Image", f"Enter Width (current: {current_width}px:",
            current_width,
            1,  # minimum
            10000  # maximum
        )

        if not ok1:  # User Canceld
            return

        height, ok2 = QInputDialog.getInt(
            None, "Resize Image", f"Enter Height (current: {current_height}px:",
            current_height,
            1,
            10000
        )
        if not ok2:  # User Cancelde
            return

        cv_image = self.qpixmap_to_cv2(pix)
        resized_image = cv2.resize(cv_image, (width, height))
        new_pixmap = self.cv2_to_qpixmap(resized_image)
        self.canvas.set_image(new_pixmap)