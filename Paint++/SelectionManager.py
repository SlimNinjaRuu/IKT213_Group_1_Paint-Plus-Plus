#import numpy as np
from dataclasses import dataclass, field
import numpy as np
from SelectionTools import SelectionTools


@dataclass
class SelectionState:
    mode: str = "none"                             # "rect", "poly", "lasso", "none"
    frozen: bool = False                           # Set as True after Enter is pressed
    rect_anchor = None                             # Start of rectangle (x,y)
    rect_current = None                            # Current mouse position (x,y)

    points:list = field(default_factory=list)      # Poly/Lasso points
    min_dist:int = 2                               # add point if it is more than 2px from the last
    last_pt = None                                 # last point
    drawing:bool = False                           # Lasso is currently dragging


class SelectionManager:

    def __init__(self):
        self.state = SelectionState()              # all selection states

    def start(self, mode, min_dist=2):

        valid_modes = {"rect", "poly", "lasso"}             # Allowed tools
        mode = mode if mode in valid_modes else "none"      # Fallback if invalid tool

        min_dist = max(1, int(min_dist))                    # make sure min_dist is an int >= 1


        # Reset selection, (keep tool + lasso spacing, clears the rest
        self.state = SelectionState(mode=mode, min_dist=min_dist)


    def cancel(self):
        self.start("none")      # clears selection


    # Returns True if the current selection has enough data to be frozen/used
    def is_ready(self):

        state = self.state

        # Rectangle need both corners, anchor (startpoint and current)
        if state.mode == "rect":
            return state.rect_anchor is not None and state.rect_current is not None


        # Needs at least 3 verticies to form an area
        if state.mode == "poly":
            return len(state.points) >= 3

        # Needs at least 2 pints to form a path
        if state.mode == "lasso":
            return len(state.points) >= 3

        return False

    '''
    When user press enter the first time, locks the selection,
    allowing for other operations in the selected area
    '''
    def freeze(self):

        if self.is_ready() and not self.state.frozen:
            self.state.frozen = True
            return True

        return False

    # ---------- Rectangle ---------- #

    # Stats rectangle selection, returns True if rectangle was started, othervisw returns False
    def rect_start(self, x, y):
        state = self.state

        if state.mode == "rect" and not state.frozen:
            state.rect_anchor = (int(x), int(y))            # First corner (on mouse click)
            state.rect_current = state.rect_anchor          # Second corner (follows mouse)
            return True
        return False


    # Updates rectangle on mouse movement
    def rect_update(self, x, y):
        state = self.state

        if state.mode == "rect" and not state.frozen and state.rect_anchor is not None:
            state.rect_current = (int(x), int(y))           # second corner follows mouse


    # For displaying the rectangular overlay
    def rect_points(self):
        return self.state.rect_anchor, self.state.rect_current


    # ---------- Polygon ---------- #

    def polygon_add_vertex(self, x, y):
        state = self.state


        if state.mode == "poly" and not state.frozen:
            state.points.append((int(x), int(y)))               # add vertices on each click


    def polygon_points(self):
        return np.asarray(self.state.points, dtype=np.int32)    # for overlay path



    # ---------- Lasso ---------- #

    def lasso_press(self, x, y):
        state = self.state

        if state.mode == "lasso" and not state.frozen:

            state.drawing = True                                # begin dragging
            state.last_pt = (x, y)

            state.points.append((int(x), int(y)))               # first point


    # Records lasso points as the mouse moves while the left-mouse-button is  held down
    def lasso_move(self, x, y, lmb_down):
        state = self.state

        if state.mode != "lasso" or state.frozen or not state.drawing or not lmb_down:
            return

        # if there is no last point, set it and stop here
        if state.last_pt is None:
            state.last_pt = (x,y)
            return


        # calculate movement since the last recorded point
        last_x, last_y = state.last_pt
        delta_x = x - last_x
        delta_y = y - last_y

        # only add new point if we move at least min_dist pixels from the last one (uses distance formula for diagonal movement)
        if delta_x * delta_x + delta_y * delta_y >= state.min_dist * state.min_dist:
            state.points.append((int(x), int(y)))
            state.last_pt = (x, y)

    def lasso_release(self):
        state = self.state

        if state.mode == "lasso":
            state.drawing = False
            state.last_pt = None

    # Returns the points as an int32 array for OpenCV (reads from self.state.points
    def lasso_points(self):
        return np.asarray(self.state.points, dtype=np.int32)



    # ---------- Mask ---------- #

    # returns a uint8 mask
    def mask(self, hw):
        state = self.state

        if state.mode == "rect" and state.rect_anchor and state.rect_current:
            return SelectionTools.rect_mask(hw, state.rect_anchor, state.rect_current)

        if state.mode == "poly" and len(state.points) >= 3:
            return SelectionTools.polygon_mask(hw, state.points)

        if state.mode == "lasso" and len(state.points) >= 3:
            return SelectionTools.lasso_mask(hw, state.points)

        return np.zeros(hw, dtype=np.uint8)


    def has_frozen_selcetion(self) -> bool:
        return self.state.frozen and self.is_ready()

    def bbox(self, hw):

        mask = self.mask(hw)
        if mask is None or mask.size == 0:
            return None
        return SelectionTools.bbox_from_mask(mask)

    def crop(self, bgr: np.ndarray, strict: bool = False):

        if not self.has_frozen_selcetion():
            return None

        h, w = bgr.shape[:2]
        mask = self.mask((h, w))

        if mask is None or mask.size == 0:
            return None

        return SelectionTools.crop_to_selection(bgr, mask, strict)


    def apply_in_selection(self, bgr: np.ndarray, op_func):

        if not self.has_frozen_selcetion():
            return None

        h, w = bgr.shape[:2]
        mask = self.mask((h, w))

        if mask is None:
            return None

        return SelectionTools.apply_in_mask(bgr, op_func, mask)


