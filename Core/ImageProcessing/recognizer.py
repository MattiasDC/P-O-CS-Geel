import cv2
import numpy as np
from PIL import Image
from shapes import *


def process_picture(image):
    image = _PIL_to_cv(image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, _ = cv2.findContours(thresh, 1, 2)

    shapes = []

    for contour in contours:
        # to prevent detection of small shapes
        if cv2.arcLength(contour, True) > 100:
            #error possible = 1%
            simp = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
            if len(simp) == Rectangle.corners:
                print "Rec"
                find_center(contour)
                shapes.append(Rectangle(None))
            elif len(simp) == Star.corners:
                print "Star"
                shapes.append(Rectangle(None))




def _PIL_to_cv(pilImage):
    """
    Converts a PIL object to a BGR image for opencv
    """
    return np.asarray(pilImage)[:, :, ::-1]

def find_center(contour):
    """
    Find the center of a contour.
    This method will find an approximation of the center of a contour.
    It will make a rectangle which fits in the contour and calculate the middle point of the rectangle.
    """

    for point in contour:
        print point


if __name__ == '__main__':
    img = Image.open('C:\Users\Mattias\PycharmProjects\P-O-Geel-2\TestSuite\Images\\1.jpg')
    process_picture(img)