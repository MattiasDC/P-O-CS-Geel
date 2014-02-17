import cv2
import numpy as np
from PIL import Image
from PIL import _imaging
from shapes import *
from time import time

min_contour_length = 200
canny_threshold1 = 50
canny_threshold2 = 130
approx_precision = 0.005
iterations = 1


def process_picture(image):
    gray_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)

    #Find edges in image
    edge_image = cv2.Canny(gray_image, canny_threshold1, canny_threshold2)

    #Make lines thicker to make found edges of shapes closed
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated_edge_image = cv2.dilate(edge_image, element, iterations=iterations)

    cv2.imwrite('testNotFlooded.jpg', dilated_edge_image)
    #Fill the rest of the image => result = black shapes, rest is white
    cv2.floodFill(dilated_edge_image, None, (0, 0), 255)
    cv2.imwrite('testFlooded.jpg', dilated_edge_image)
    #Find contours of black shapes
    contours, _ = cv2.findContours(dilated_edge_image, 1, 2)

    #Filter small elements out of the contours
    contours = filter(lambda x: cv2.arcLength(x, True) > min_contour_length, contours)
    #Approximate contours TODO is this necessary??
    contours = map(lambda x: cv2.approxPolyDP(x, approx_precision*cv2.arcLength(x, True), True), contours)
    shapes = []
    # TODO filter giant rectangle properly
    for contour in contours[:-1]:
        print contour.tolist()
        cv2.drawContours(gray_image, [contour], 0, (255, 0, 0), 2)

    return gray_image, dilated_edge_image


def find_center(contour):
    """
    Find the center of a contour.
    This method will find an approximation of the center of a contour.
    It will make a rectangle which fits in the contour and calculate the middle point of the rectangle.
    """
    pass


if __name__ == '__main__':
    img = Image.open('C:\Users\Mattias\Desktop\star.png')
    gray_with_contour, processed = process_picture(img)
    cv2.imwrite('testc.jpg', gray_with_contour)
    cv2.imwrite('testg.jpg', processed)