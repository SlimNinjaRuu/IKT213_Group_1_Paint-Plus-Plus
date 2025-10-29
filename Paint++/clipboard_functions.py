import cv2
import numpy as np
from selection_tools_functions import *

def copy_image(image):
    # Makes a deep copy
    return image.copy()  # or: np.copy(image)

def main():
    img = cv2.imread('100.jpg', 1)
    if img is None:
        raise FileNotFoundError("Could not load '100.jpg'")

    # Saves the selected area in the copied_image variable
    selected_area = rectangular_selection(img)
    copied_image = copy_image(selected_area)
    cv2.imshow("Copied selection", copied_image)
    cv2.waitKey(0)


    selected_area2 = polygon_selection(img, mode="alpha_cropped")
    copied_image2 = copy_image(selected_area2)
    cv2.imwrite("cutout2.png", copied_image2)
    cv2.waitKey(0)

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
