import cv2
import numpy as np
import math


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

    # Create window and show image copy for drawing
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(window_name, disp)

    # shared state for mouse callback
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

        # Enter: accept current points
        if key in (13, 10):   # Enter/Return
            # If not closed yet but valid, close it in the returned pts implicitly
            break

        # Escape: cancel selection
        if key == 27:
            points.clear()
            break

    cv2.destroyWindow(window_name)
    return np.array(points, dtype=np.int32)

# Helper: apply polygon extraction with given mode
def polygon_selection(image_bgr, pts, mode="alpha_cropped"):
    return extract_polygon(image_bgr, np.asarray(pts, dtype=np.int32), mode=mode)



def extract_polygon(image, pts, mode="alpha_cropped"):

    # Fallback: not enough points to original
    if pts is None or len(pts) < 3:
        return image.copy()

    # Make binary mask from polygon
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

#Apply a grayscale effect only inside the binary mask.
def apply_gray_inside_mask(image, mask):

    # Convert full image to grayscale
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_gray_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

    # Copy original and replace the masked pixels with grayscale version
    out = image.copy()
    out[mask > 0] = img_gray_bgr[mask > 0]
    return out


#Make a polygon mask from pts and apply the demo effect.
def finalize_with_mask(image, pts):

    if pts.shape[0] < 3:
        return image.copy()

    # Build mask from polygon points
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)

    # Apply grayscale only inside mask
    return apply_gray_inside_mask(image, mask)

def _lasso_mouse(event, x, y, flags, state):
    disp     = state["disp"]
    points   = state["points"]
    drawing  = state["drawing"]
    last_pt  = state["last_pt"]
    min_dist = state["min_dist"]

    if event == cv2.EVENT_LBUTTONDOWN:
        # Start drawing freehand path
        state["drawing"] = True
        state["last_pt"] = (x, y)
        points.append((x, y))
        # Firs point when drawing - thickness and color
        cv2.circle(disp, (x, y), 2, (255, 0, 0), -1, lineType=cv2.LINE_AA)
        cv2.imshow(state["win"], disp)

    elif event == cv2.EVENT_MOUSEMOVE and drawing and (flags & cv2.EVENT_FLAG_LBUTTON):

        # Mouse moving while LMB is held and drawing is active
        if last_pt is None:
            state["last_pt"] = (x, y)
            return

        # Only add a point if we moved at least min_dist pixels
        if math.hypot(x - last_pt[0], y - last_pt[1]) >= min_dist:
            points.append((x, y))
            # Drawing line - thickness and color
            cv2.line(disp, last_pt, (x, y), (255, 0, 0), 2, lineType=cv2.LINE_AA)
            state["last_pt"] = (x, y)
            cv2.imshow(state["win"], disp)

    elif event == cv2.EVENT_LBUTTONUP:
        # Stop drawing on mouse release
        state["drawing"] = False
        state["last_pt"] = None

def lasso_points(image, min_dist=2, window_name="Lasso select"):
    """
    Hold & drag LMB to draw a free-form polygon (lasso).
    Press Enter to accept; Esc to cancel.
    """
    points = []
    disp = image.copy()

    # Shared state for mouse callback
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

    # Wait for Enter or Esc
    while True:
        key = cv2.waitKey(20) & 0xFF
        if key in (13, 10):   # Enter/Return
            break
        if key == 27:         # Esc
            points.clear()
            break

    cv2.destroyWindow(window_name)
    return np.array(points, dtype=np.int32)

# Takes the points after lasso has been drawn on the Qt canvas
def lasso_selection(image_bgr, pts):

    pts = np.array(pts, dtype=np.int32)
    if pts is None or len(pts) < 3:
        return image_bgr.copy()

    mask = np.zeros(image_bgr.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts.astype(np.int32)], 255)


    img_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    img_gray_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
    out = image_bgr.copy()
    out[mask > 0] = img_gray_bgr[mask > 0]
    return out

##################################### LASSO #####################################

def rectangular_selection(image_bgr, p1, p2):

    x1, y1, = p1
    x2, y2, = p2
    x1, x2, = sorted((int(x1), int(x2)))
    y1, y2, = sorted((int(y1), int(y2)))

    if x2 <= x1 or y2 <= y1:
        return image_bgr.copy()
    return image_bgr[y1:y2, x1:x2].copy()



# Demo - not used in the final progrm
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
