import cv2
import numpy as np

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