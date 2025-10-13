import cv2
import numpy as np

def click_event(event, x, y, flags, param):
    disp = param["disp"]
    points = param["points"]

    # Showing vertices for polygon as dots on the image when m1 is given
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(disp, (x, y), 4, (255, 0, 0), -1, lineType=cv2.LINE_AA)
        cv2.imshow("Pick polygon", disp)

def polygon_points(image):
    # Getting the vertices coordinates until enter is given
    points = []
    disp = image.copy()
    cv2.namedWindow("Pick polygon", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("Pick polygon", disp)
    cv2.setMouseCallback("Pick polygon", click_event, {"disp": disp, "points": points})

    # Key loop: Enter -> done, Esc -> cancel
    while True:
        key = cv2.waitKey(20) & 0xFF
        if key in (13, 10):   # Enter/Return
            break
        if key == 27:         # Esc
            points.clear()
            break

    cv2.destroyWindow("Pick polygon")
    return np.array(points, dtype=np.int32)

def polygon_selection(image):
    pts = polygon_points(image)
    if pts.shape[0] < 3:
        # 3 or more points are needed to make a polygon
        return image.copy()

    # Making a mask
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)

    # Manipulation of the whole image
    image_manipulation = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    shape_bgr = cv2.cvtColor(image_manipulation, cv2.COLOR_GRAY2BGR)

    # Manipulation is copied only to the area inside of polygon
    out = image.copy()
    out[mask > 0] = shape_bgr[mask > 0]

    return out

def rectangular_selection(image):
    # x and y coordinate for top left selected corner
    # width and height for marked rectangle
    x, y, w, h = cv2.selectROI("Rectangular select", image)
    cv2.destroyWindow("Rectangular select")

    out = image.copy()
    roi = image[y:y+h, x:x+w]

    # Making selected area gray
    roi_manipulation = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Making the gray selected area back to 3 channels for compatibility
    #  This has to be changed in order to do other operations to the selected area
    roi_compatible = cv2.cvtColor(roi_manipulation, cv2.COLOR_GRAY2BGR)

    out[y:y+h, x:x+w] = roi_compatible

    return out

def selective_crop(image):
    r = cv2.selectROI("Crop select", image)
    crop_image = image[int(r[1]):int(r[1] + r[3]),
    int(r[0]):int(r[0] + r[2])]
    cv2.destroyWindow("Crop select")
    return crop_image

def resize(image, width, height):
    image_resize = cv2.resize(image,(width, height))
    return image_resize

def rotation(image, rotation_direction):
    if rotation_direction == 'right':
        rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        return rotated
    elif rotation_direction == 'left':
        rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return rotated
    return None

def flip(image, orientation):
    if orientation == 'vertical':
        flipped = cv2.flip(image, 0)
        return flipped
    elif orientation == 'horizontal':
        flipped = cv2.flip(image, 1)
        return flipped
    return None

def main():
    img = cv2.imread('100.jpg', 1)
    img_const = cv2.imread('100.jpg', 1)
    img_const2 = cv2.imread('100.jpg', 1)

    # Cropping parameters
    # Add some visual adjustment method - width/height = adjustable variable in GUI
    crop_width_0 = 100
    crop_width_1 = 500
    crop_height_0 = 400
    crop_height_1 = 800

    # Resizing parameters
    # Add some visual adjustment method - width/height = adjustable variable in GUI
    resized_width = 1000
    resized_height = 1000

    # Rotation parameters
    # Add some visual adjustment method - direction_rotate = adjustable variable in GUI
    # Might just be 0 for left and 1 for right in the rotation function instead of 'left' and 'right'
    direction_rotate = ['right', 'left']

    # Flipping parameters
    # Add some visual adjustment method - orientation_flip = adjustable variable in GUI
    # Might just be 0 for vertical and 1 for horizontal in the flip function instead of 'vertical' and 'horizontal'
    orientation_flip = ['vertical', 'horizontal']

    # Polygon selection demo
    # Collecting points in np array
    # pts = polygon_points(img_const2)
    img_const2 = polygon_selection(img_const2)
    cv2.imshow("Polygon selection", img_const2)
    cv2.waitKey(0)

    # Rectangular selection demo
    img_const = rectangular_selection(img_const)
    cv2.imshow("Selected image", img_const)
    cv2.waitKey(0)

    # The cropped image will be the new main image
    img = selective_crop(img)
    cv2.imshow("Cropped Image", img)
    cv2.waitKey(0)

    # The resized image will now be the new main image
    img = resize(img, resized_width, resized_height)
    cv2.imshow("resized", img)
    cv2.waitKey(0)

    # The rotated image will now be the new main image
    img = rotation(img, direction_rotate[0])
    cv2.imshow("rotated", img)
    cv2.waitKey(0)

    # The rotated image will now be the new main image
    img = rotation(img, direction_rotate[1])
    cv2.imshow("rotated 2", img)
    cv2.waitKey(0)

    # The flipped image will now be the new main image
    img = flip(img, orientation_flip[1])
    cv2.imshow("Flipped", img)
    cv2.waitKey(0)

    # The flipped image will now be the new main image
    img = flip(img, orientation_flip[0])
    cv2.imshow("Flipped 2", img)
    cv2.waitKey(0)

    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()