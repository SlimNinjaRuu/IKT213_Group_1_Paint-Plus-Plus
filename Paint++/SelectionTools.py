import cv2
import numpy as np



class SelectionTools:

    @staticmethod
    # Returns a uint8 mask (0 = outside, 255 = inside) for the rectangle selection
    def rect_mask(hw, p1, p2):

        # Reads image size
        h, w = int(hw[0]), int(hw[1])           # image height/width
        x1, y1 = int(p1[0]), int(p1[1])         # first corner
        x2, y2 = int(p2[0]), int(p2[1])         # opposite corner

        # Reorder corner cordinates (makes first corner top-left, and second bottom-right)
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        # Keeps selection inside the image by limiting the points between 0 and image size (heit, width)
        x1 = int(np.clip(x1, 0, w))
        x2 = int(np.clip(x2, 0, w))
        y1 = int(np.clip(y1, 0, h))
        y2 = int(np.clip(y2, 0, h))


        # If the rectangle has no area, return an empty mask
        if x2 <= x1 or y2 <= y1:
            return np.zeros((h, w), dtype=np.uint8)

        # Creates an empty mask with all pixels = 0
        mask = np.zeros((h, w), dtype=np.uint8)           #   0 = outside the selection
        mask[y1:y2, x1:x2] = 255                          # 255 = inside selection
        return mask

    @staticmethod
    def polygon_mask(hw, pts):

        # Reads image size
        h, w = int(hw[0]), int(hw[1])
        pts = np.asarray(list(pts), dtype=np.int32)     # use the points to create numpy array of ints
        mask = np.zeros((h, w), dtype=np.uint8)   # create empty mask (same size as image)


        # need table of points, N rows, 2 collums, at least 3 points (number of dimensions)
        if pts.ndim != 2 or pts.shape[0] < 3:
            return mask

        # Keep points inside the image by limiting all the points to be 0 to width-1 or height-1
        pts[:, 0] = np.clip(pts[:,0], 0, w - 1)
        pts[:, 1] = np.clip(pts[:,1], 0, h - 1)


        # Mark inside the polygon as selected
        cv2.fillPoly(mask, [pts], 255)

        return mask

    @staticmethod
    # Treated as a polygon with many points from a drag
    def lasso_mask(hw, pts):
        return SelectionTools.polygon_mask(hw, pts)


    # Find bounding box of non-zero pixels in mask
    @staticmethod
    def bbox_from_mask(mask: np.ndarray):

        nz = cv2.findNonZero(mask)
        if nz is None or len(nz) == 0:
            return None

        x, y, w, h = cv2.boundingRect(nz)
        return (x, y, w, h)


    # Get bounding box from mask
    @staticmethod
    def crop_to_selection(bgr: np.ndarray, mask: np.ndarray, strict: bool = False):

        bb = SelectionTools.bbox_from_mask(mask)
        if bb is None:
            return None

        x, y, w, h, = bb

        H, W = bgr.shape[:2]

        # Clamp bbox to image bounds
        x0 = max(0, min(x, W))
        y0 = max(0, min(y, H))
        x1 = max(0, min(x + w, W))
        y1 = max(0, min(y + h, H))

        # Invalid region cancels crop
        if x1 <= x0 or y1 <= y0:
            return None

        # Crop color image to bbox
        crop = bgr[y0:y1, x0:x1].copy()

        if strict:
            # Use mask inside bbox to zero out outside pixels
            submask = mask[y0:y1, x0:x1]
            if submask.dtype != np.uint8:
                submask = submask.astype(np.uint8)
            crop[submask == 0] = 0
        return crop


    # Apply op_func to whole image
    @staticmethod
    def apply_in_mask(bgr: np.ndarray, op_func,  mask: np.ndarray):

        modified = op_func(bgr.copy())

        # Copy original and blend back only inside mask
        out = bgr.copy()
        out[mask > 0] = modified[mask > 0]
        return out

