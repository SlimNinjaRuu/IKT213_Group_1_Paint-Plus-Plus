import cv2
import numpy as np
import math

##################################### POLYGON #####################################

def _polygon_mouse(event, x, y, flags, state):
    disp   = state["disp"]
    points = state["points"]
    win    = state["win"]

    # Add a vertex on LMB click
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(disp, (x, y), 4, (0, 0, 255), -1, lineType=cv2.LINE_AA)
        # Draw an edge from the previous vertex
        if len(points) > 1:
            cv2.line(disp, points[-2], points[-1], (0, 0, 255), 2, lineType=cv2.LINE_AA)
        cv2.imshow(win, disp)

def polygon_points(image, window_name="Polygon select"):
    """
    Click to add vertices.
    Press 'c' to close polygon visually, Enter to accept, Esc to cancel.
    """
    points = []
    disp = image.copy()

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(window_name, disp)
    state = {"disp": disp, "points": points, "win": window_name}
    cv2.setMouseCallback(window_name, _polygon_mouse, state)

    closed_drawn = False

    while True:
        key = cv2.waitKey(20) & 0xFF

        # 'c' closes the polygon visually (draws the last edge to the first)
        if key in (ord('c'), ord('C')) and len(points) >= 3 and not closed_drawn:
            cv2.line(disp, points[-1], points[0], (0, 0, 255), 2, lineType=cv2.LINE_AA)
            cv2.imshow(window_name, disp)
            closed_drawn = True

        if key in (13, 10):   # Enter/Return
            # If not closed yet but valid, close it in the returned pts implicitly
            break

        if key == 27:         # Esc
            points.clear()
            break

    cv2.destroyWindow(window_name)
    return np.array(points, dtype=np.int32)

def polygon_selection(image, mode="alpha_cropped"):

    pts = polygon_points(image, window_name="Polygon select")
    return extract_polygon(image, pts, mode=mode)

def extract_polygon(image, pts, mode="alpha_cropped"):

    if pts is None or len(pts) < 3:
        return image.copy()

    # Make mask
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)

    if mode == "masked_bgr":
        # Keep full size, outside black
        out = cv2.bitwise_and(image, image, mask=mask)
        return out

    # Default: alpha_cropped
    # Add alpha from mask
    out_bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    out_bgra[:, :, 3] = mask

    # Crop to tight bounding box of the polygon
    x, y, w, h = cv2.boundingRect(pts)
    out_cropped = out_bgra[y:y+h, x:x+w]
    return out_cropped

##################################### POLYGON #####################################

##################################### LASSO #####################################

def apply_gray_inside_mask(image, mask):
    """Apply a grayscale effect only inside the binary mask."""
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_gray_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
    out = image.copy()
    out[mask > 0] = img_gray_bgr[mask > 0]
    return out

def finalize_with_mask(image, pts):
    """Make a polygon mask from pts and apply the demo effect."""
    if pts.shape[0] < 3:
        return image.copy()

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)

    return apply_gray_inside_mask(image, mask)

def _lasso_mouse(event, x, y, flags, state):
    disp     = state["disp"]
    points   = state["points"]
    drawing  = state["drawing"]
    last_pt  = state["last_pt"]
    min_dist = state["min_dist"]

    if event == cv2.EVENT_LBUTTONDOWN:
        state["drawing"] = True
        state["last_pt"] = (x, y)
        points.append((x, y))
        # Firs point when drawing - thickness and color
        cv2.circle(disp, (x, y), 2, (255, 0, 0), -1, lineType=cv2.LINE_AA)
        cv2.imshow(state["win"], disp)

    elif event == cv2.EVENT_MOUSEMOVE and drawing and (flags & cv2.EVENT_FLAG_LBUTTON):
        if last_pt is None:
            state["last_pt"] = (x, y)
            return
        if math.hypot(x - last_pt[0], y - last_pt[1]) >= min_dist:
            points.append((x, y))
            # Drawing line - thickness and color
            cv2.line(disp, last_pt, (x, y), (255, 0, 0), 2, lineType=cv2.LINE_AA)
            state["last_pt"] = (x, y)
            cv2.imshow(state["win"], disp)

    elif event == cv2.EVENT_LBUTTONUP:
        state["drawing"] = False
        state["last_pt"] = None

def lasso_points(image, min_dist=2, window_name="Lasso select"):
    """
    Hold & drag LMB to draw a free-form polygon (lasso).
    Press Enter to accept; Esc to cancel.
    """
    points = []
    disp = image.copy()

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
    cv2.setMouseCallback(window_name, _lasso_mouse, state)

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key in (13, 10):   # Enter/Return
            break
        if key == 27:         # Esc
            points.clear()
            break

    cv2.destroyWindow(window_name)
    return np.array(points, dtype=np.int32)

def lasso_selection(image, min_dist=2):
    pts = lasso_points(image, min_dist=min_dist, window_name="Lasso select")
    return finalize_with_mask(image, pts)

##################################### LASSO #####################################

def rectangular_selection(image):
    x, y, w, h = cv2.selectROI("Rectangular select", image)
    cv2.destroyWindow("Rectangular select")
    if w == 0 or h == 0:
        return image.copy()

    # out = image.copy()
    roi = image[y:y+h, x:x+w]
    # roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # roi_bgr  = cv2.cvtColor(roi_gray, cv2.COLOR_GRAY2BGR)
    # out[y:y+h, x:x+w] = roi_bgr
    # return out
    return roi

# Demo
def main():
    img = cv2.imread('100.jpg', 1)

    # Polygon selection should return the selected area
    cutout = polygon_selection(img, mode="alpha_cropped")
    cv2.imwrite("cutout.png", cutout)  # keep transparency
    cv2.waitKey(0)

    # Lasso selection demo (hold & drag)
    lasso_out = lasso_selection(img, min_dist=2)
    cv2.imshow("Lasso selection (result)", lasso_out)
    cv2.waitKey(0)

    # Rectangular selection should return the selected area
    rect_out = rectangular_selection(img)
    cv2.imshow("Rectangular selection (result)", rect_out)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
