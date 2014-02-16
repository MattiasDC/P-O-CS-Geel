import cv2
import numpy
from shapes import *


def process_picture(image):
    image = _PIL_to_cv(image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, _ = cv2.findContours(thresh, 1, 2)

    shapes = []

    for contour in contours:
        if cv2.arcLength(contour, True) > 100:  # to prevent detection of small shapes
            simp = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
            if len(simp) == Rectangle.corners:
                print "Rec"
            elif len(simp) == Star.corners:
                print "Star"


def _PIL_to_cv(image):
    """
    Converts a PIL object to a BGR image for opencv
    """
    open_cv_image = numpy.array(image)
    return open_cv_image[:, :, ::-1].copy()
