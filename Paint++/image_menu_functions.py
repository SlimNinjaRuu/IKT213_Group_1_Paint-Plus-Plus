# image_menu_functions.py
import cv2
import numpy as np
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
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

        # takes the cv2 bgr image and makes it rgb image
        rgba = cv2.cvtColor(bgr, cv2.COLOR_BGRA2RGBA)

        height, width, channels = rgba.shape
        bytes_per_line = width * channels

        # makes rgb to QImage
        qimg = QImage(rgba.data, width, height, bytes_per_line, QImage.Format.Format_ARGB32)

        # returns Qpixmap from QImage
        return QPixmap.fromImage(qimg.copy())

    @staticmethod
    def qpixmap_to_cv2(pixmap):
        # If QPixmap is none return without doing conversion
        if pixmap.isNull():
            return None

        # Makes a QImage in rgba from QPixmap
        qimg = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)

        # QImage height and width
        w = qimg.width()
        h = qimg.height()
        ## bytes_per_line = qimg.bytesPerLine()

        # Will make a deep copy
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())

        # Creates numpy array from, QImage              ## 4
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 4))

        ## arr = arr[:, :w*3].reshape((h, w, 3))

        # Converts RGB array to BGR and returns it
        bgra = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        return bgra.copy()
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
        # Get current pixmap from canvas
        pix = self.canvas.pixmap()

        # Abort if no image
        if not pix or pix.isNull():
            return

        # Convert QPixmap to OpenCV BGR image
        cv = self.qpixmap_to_cv2(pix)

        # Let user select the region of interest
        r = cv2.selectROI("Crop select", cv)

        # Crops the image over the selected ROI
        crop_image = cv[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        cv2.destroyWindow("Crop select")

        # Makes QPixmap of cropped bgr
        qpix = self.cv2_to_qpixmap(crop_image)

        # Sets the cropped QPixmap as canvas
        self.canvas.set_image(qpix)


    def resize(self):

        # Get current pixmap
        pix = self.canvas.pixmap()

        # Abort if no canvas image
        if self.canvas.image is None or self.canvas.image.isNull():
            QMessageBox.information(None, "No Image", "Image must be loaded first")
            return

        # Get current image dimensions from the canvas
        current_width = self.canvas.width()
        current_height = self.canvas.height()

        # Ask user for new width
        width, ok1 = QInputDialog.getInt(
            None,
            "Resize Image", f"Enter Width (current: {current_width}px:",
            current_width,
            1,  # minimum
            10000  # maximum
        )

        if not ok1:  # User Canceld
            return

        # Ask user for new height
        height, ok2 = QInputDialog.getInt(
            None, "Resize Image", f"Enter Height (current: {current_height}px:",
            current_height,
            1,
            10000
        )
        if not ok2:  # User Cancelde
            return

        # Convert QPixmap to an OpenCV image
        cv_image = self.qpixmap_to_cv2(pix)

        # Resize with OpenCV
        resized_image = cv2.resize(cv_image, (width, height))

        # Convert back to QPixmap and update canvas
        new_pixmap = self.cv2_to_qpixmap(resized_image)
        self.canvas.set_image(new_pixmap)



    def apply_operation_with_selection(self, operation_func):
        # Get current pixmap
        pix = self.canvas.pixmap()

        if not pix or pix.isNull():
            return

        c = self.canvas

        # Convert Qpixmap to OpenCV image
        cv_img = self.qpixmap_to_cv2(pix)

        # If frozen selection exists, apply only inside mask
        if hasattr(c, "sel_mgr") and c.sel_mgr.state.frozen and c.sel_mgr.is_ready():

                h, w = cv_img.shape[:2]
                mask = c.sel_mgr.mask((h, w))

                # Apply operatuon to a copy
                modified = operation_func(cv_img.copy())

                # Blend modified pixels only where mask > 0
                result = cv_img.copy()
                result[mask > 0] = modified[mask > 0]

                return self.cv2_to_qpixmap(result)

        # No selection: apply to whole image
        modified = operation_func(cv_img)
        return self.cv2_to_qpixmap(modified)

    def request_crop(self, strict: bool = False):

        c = self.canvas

        # Requiers active, frozen selection with mask
        if not (getattr(c, "sel_active", False)
                and getattr(c, "sel_frozen", False)
                and getattr(c, "active_mask", None) is not None):
            QMessageBox.information(None, "Crop", "Select an area an press enter to freeze it first. \n Then choose Image -> Crop and press Enter to apply.")
            return

        # Get current image as BGR
        bgr = c.get_cv2_image()
        if bgr is None:
            return

        # Let SelectionManager perform crop
        out = c.sel_mgr.crop(bgr, strict=bool(strict))
        if out is not None:
            self.canvas.set_cv2_image(out)

        # Exit selection mode after crop
        c.cancel_selection()

