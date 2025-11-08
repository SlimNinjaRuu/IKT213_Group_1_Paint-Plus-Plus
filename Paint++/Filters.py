
import cv2
import numpy as np
from PyQt6.QtWidgets import QInputDialog, QMessageBox


# ----- Image filtering tool: Gaussian blur, Sobel, binary threshold, histogram equalization
class Filters:

    def __init__(self, canvas, image_functions):

        self.canvas = canvas
        self.imf = image_functions

    def warning(self, pix):
        if not pix or pix.isNull():
            QMessageBox.warning(self, "Warning", "No image")
            return True
        return False

    # ----- Gaussian blur ----- #
    def gaussian_blur(self):

        pix = self.canvas.pixmap()

        if self.warning(pix):
            return


        # Get Kernel size from user
        kernel_size,  ok = QInputDialog.getInt(
            None,
            "Gaussian Blur",
            "Enter kernel size (odd number)",
            5,                                  # default
            3,                                  # minimum
            31,                                 # maximum
            2                                   # step
        )

        if not ok:
            return

        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size = kernel_size + 1


        # Apply filter with selection support
        def blur_operation(bgr):
            return cv2.GaussianBlur(bgr, (kernel_size, kernel_size), 0)

        result_pixmap = self.imf.apply_operation_with_selection(blur_operation)

        if result_pixmap:
            self.canvas.set_image(result_pixmap)


    # ----- Sobel Filter ----- #
    def sobel_filter(self):

        pix = self.canvas.pixmap()

        if self.warning(pix):
           return

        # Ask user which direction
        directions = ["-Both (X+Y)", "X-direction", "Y-direction"]
        direction, ok = QInputDialog.getItem(
            None,
            "Sobel Filter",
            "Select edge detection method",
            directions,
            0,
            False
        )

        if not ok:
            return


        def sobel_operation(bgr):


            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)            #Convert to grayscale for edge detection

            if direction == "X-direction":
                sobel = cv2.Sobel(gray, cv2.CV_64F, 1,0,  ksize=3)     # Detect vertical edges

            elif direction == "Y-direction":
                sobel = cv2.Sobel(gray, cv2.CV_64F, 0,1, ksize=3)   #Detect horizontal edges

            else:
                # Detect edges in both direction
                sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                sobel = cv2.magnitude(sobel_x, sobel_y)

            # Convert back to uint8
            sobel = np.absolute(sobel)
            sobel = np.uint8(np.clip(sobel, 0, 255))

            # Convert back to BGR for display
            sobel_bgr = cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
            return sobel_bgr

        result_pixmap = self.imf.apply_operation_with_selection(sobel_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)


    # ----- Binary Treshhold ----- #
    def binary_threshhold(self):
        pix = self.canvas.pixmap()

        if self.warning(pix):
            return

        # Get threshold value from user
        threshold_val, ok = QInputDialog.getInt(
            None,
            "Binary Threshold",
            "Enter value between 0 and 255",
            127,     # Default
            0,       # Minimum
            255      # Maximum
        )

        if not ok:
            return

        def treshold_operation(bgr):

            # Convert to grayscale
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            #apply binary threshold
            _, binary = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)

            # convert back to BGR
            binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            return binary_bgr

        result_pixmap = self.imf.apply_operation_with_selection(treshold_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)


    # -----  Adaptive Threshold ----- #
    def adaptive_thresholding(self):

        pix = self.canvas.pixmap()

        if self.warning(pix):
            return

        block_size, ok = QInputDialog.getInt(
            None,
            "Adaptive Threshold",
            "Enter block size (odd number)",
            11,     # default
            3,      # minimum
            51,     # maximum
            2       # step
        )

        if not ok:
            return

        # Ensure block size is odd
        if block_size % 2 == 0:
            block_size += 1

        def adaptive_threshold_operation(bgr):

            # Convert to grayscale
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            adaptive = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                block_size,
                2
            )

            # convert back to BGR
            adaptive_bgr = cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR)
            return adaptive_bgr

        result_pixmap = self.imf.apply_operation_with_selection(adaptive_threshold_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)

    def histogram_operation(self):

        pix = self.canvas.pixmap()

        if self.warning(pix):
            return

        def histogram_operation(bgr):

            # Convert BGR to YCrCb color space
            ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)

            # Split the channels
            y, cr, cb = cv2.split(ycrcb)

            # Apply histogram equlization to Y channal (luminance)
            y_eq = cv2.equalizeHist(y)

            # Merge channels back
            ycrcb_eq = cv2.merge([y_eq, cr, cb])

            bgr_eq = cv2.cvtColor(ycrcb_eq, cv2.COLOR_YCrCb2BGR)
            return bgr_eq

        result_pixmap = self.imf.apply_operation_with_selection(histogram_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)

    def median_blur(self):
        pix = self.canvas.pixmap()
        if self.warning(pix):
            return

        kernel_size, ok = QInputDialog.getInt(
            None,
            "Median Blur",
            "Enter kernel size (odd number)",
            5,      # Default
            3,      # minimum
            15,     # maximum
            2
        )

        if not ok:
            return

        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size = kernel_size + 1

        def median_operation(bgr):
            return cv2.medianBlur(bgr, kernel_size)

        result_pixmap = self.imf.apply_operation_with_selection(median_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)

    def bilateral_filter(self):
        pix = self.canvas.pixmap()

        if self.warning(pix):
            return

        diameter, ok = QInputDialog.getInt(
            None,
            "Bilateral Filter",
            "Enter diameter (odd number, larger = slower)",
            9,      # default
            5,      # minimum
            15      # maximum
        )

        if not ok:
            return

        def bilateral_operation(bgr):
            return cv2.bilateralFilter(bgr, diameter, 75, 75)

        result_pixmap = self.imf.apply_operation_with_selection(bilateral_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)



    def canny_edges(self):
        pix = self.canvas.pixmap()
        if self.warning(pix):
            return


        threshold1, ok1 = QInputDialog.getInt(
            None,
            "Canny Edge Detection",
            "Enter upper threshold (0-255)",
            150,        # deault
            0,          # minimum
            255         # maximum
        )

        if not ok1:
            return

        threshold2, ok2 = QInputDialog.getInt(
            None,
            "Canny Edge Detection",
            "Enter lower threshold (0-255)",
            150,
            0,
            255
        )

        if not ok2:
            return

        def canny_operation(bgr):
            #convert to grayscale
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(gray, threshold1, threshold2)
            edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            return edges_bgr

        result_pixmap = self.imf.apply_operation_with_selection(canny_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)

    def grayscale(self):
        pix = self.canvas.pixmap()
        if self.warning(pix):
            return

        def grayscale_operation(bgr):
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            return gray_bgr

        result_pixmap = self.imf.apply_operation_with_selection(grayscale_operation)
        if result_pixmap:
            self.canvas.set_image(result_pixmap)









