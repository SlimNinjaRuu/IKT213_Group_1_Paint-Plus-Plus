import cv2
import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from image_menu_functions import imf
import math

class tools:
    def __init__(self, canvas, imf_module=None):
        self.canvas = canvas
        self.imf = imf_module or imf

    # Zoom
    def zoom(self):
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return
        cv = self.imf.qpixmap_to_cv2(pix)
        # Factor is to be changed for zooming in/out
        factor = 0.5
        zoomed_img = cv2.resize(cv, None, fx=factor, fy=factor, interpolation=cv2.INTER_LINEAR)
        self.canvas.set_image(self.imf.cv2_to_qpixmap(zoomed_img))

    @staticmethod
    def _lasso_mouse(event, x, y, flags, state):
        disp = state["disp"]
        points = state["points"]
        drawing = state["drawing"]
        last_pt = state["last_pt"]
        min_dist = state["min_dist"]

        if event == cv2.EVENT_LBUTTONDOWN:
            state["drawing"] = True
            state["last_pt"] = (x, y)
            points.append((x, y))
            # dot at start - thickness and color
            cv2.circle(disp, (x, y), 2, (255, 0, 255), -1, lineType=cv2.LINE_AA)
            cv2.imshow(state["win"], disp)

        elif event == cv2.EVENT_MOUSEMOVE and drawing and (flags & cv2.EVENT_FLAG_LBUTTON):
            if last_pt is None:
                state["last_pt"] = (x, y)
                return
            if math.hypot(x - last_pt[0], y - last_pt[1]) >= min_dist:
                points.append((x, y))
                # Drawing line - thickness and color
                cv2.line(disp, last_pt, (x, y), (255, 0, 255), 2, lineType=cv2.LINE_AA)
                state["last_pt"] = (x, y)
                cv2.imshow(state["win"], disp)

        elif event == cv2.EVENT_LBUTTONUP:
            state["drawing"] = False
            state["last_pt"] = None

    def lasso_points(self, image, min_dist=2, window_name="Lasso select"):
        """
        Draw freehand on a copy of `image`.
        Return (points_as_np_array, drawn_image).
        Press Enter to accept; Esc to cancel (returns empty points and original image).
        """
        points = []
        disp = image.copy()
        if len(disp.shape) == 2:
            disp = cv2.cvtColor(disp, cv2.COLOR_GRAY2BGR)

        state = {
            "disp": disp,
            "points": points,
            "drawing": False,
            "last_pt": None,
            "min_dist": max(1, int(min_dist)),
            "win": window_name,
        }

        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(window_name, disp)
        # staticmethod (or class name) avoids the implicit self
        cv2.setMouseCallback(window_name, tools._lasso_mouse, state)

        accepted = False
        while True:
            key = cv2.waitKey(20) & 0xFF
            if key in (13, 10):  # Enter
                accepted = True
                break
            if key == 27:  # Esc
                break

        cv2.destroyWindow(window_name)

        if not accepted:
            # cancel: return original image and empty points
            return np.zeros((0, 2), dtype=np.int32), image

        return np.array(points, dtype=np.int32), disp

    def lasso_draw(self, min_dist=2):
        """
        Convert canvas QPixmap -> cv2 image, let user draw with lasso, then
        convert the edited image back to QPixmap, update the canvas, and return it.
        """
        pix = self.canvas.pixmap()
        if not pix or pix.isNull():
            return None

        cv_img = self.imf.qpixmap_to_cv2(pix)

        pts, edited = self.lasso_points(cv_img, min_dist=min_dist, window_name="Lasso select")

        # If user cancelled, do nothing
        if pts.shape[0] == 0 or edited is None:
            return None

        qpix = self.imf.cv2_to_qpixmap(edited)
        # Update the canvas (assuming your canvas has set_image)
        self.canvas.set_image(qpix)
