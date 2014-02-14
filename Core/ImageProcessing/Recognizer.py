import cv2
import PIL
import numpy

def process_picture(image):
    image = PIL_to_cv(image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, _ = cv2.findContours(thresh, 1, 2)

    shapes = []

    for contour in contours:
        if cv2.arcLength(contour, True) > 100:
            simp = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
            if len(simp) == :

            elif len(simp) == 3:
                print 'triangle'


def PIL_to_cv(image):
    open_cv_image = numpy.array(image)
    # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()