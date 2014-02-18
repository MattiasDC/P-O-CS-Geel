import cv2
import numpy as np
from PIL import Image
from PIL import _imaging
from shapes import *

min_contour_length = 400    # The minimum length of the contour of a shape, used to filter
max_contour_factor = 0.8
canny_threshold1 = 20       # Thresholds for the canny edge detection algorithm
canny_threshold2 = 60
approx_precision = 0.005    # The approximation of the contour when using the Ramer-Douglas-Peucker (RDP) algorithm
iterations = 2              # The amount of iterations to dilate the edges to make the contours of the shapes closed
max_offset_shape = 0.1      # The maximum offset for the shape recognition

colors = {(50, 100, 0): 'Green',
          (0, 50, 100): 'Blue',
          (240, 210, 10): 'Yellow',
          (255, 255, 255): 'White',
          (0, 0, 0): 'Black',
          (200, 0, 0): 'Red'}

shapes = [Rectangle, Star, Ellipse, Heart]


def process_picture(image):
    #Filter giant rectangle of the image itself
    res_x, res_y = image.size
    max_contour_length = (2*res_x + 2*res_y)*max_contour_factor

    #Load image gray scale
    gray_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    gray_image = cv2.GaussianBlur(gray_image, (3, 3), 3)
    #Find edges in image
    edge_image = cv2.Canny(gray_image, canny_threshold1, canny_threshold2)

    #Make lines thicker to make found edges of shapes closed
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated_edge_image = cv2.dilate(edge_image, element, iterations=iterations)

    #Fill the rest of the image => result = black shapes, rest is white
    dilated_edge_image = fill_image(dilated_edge_image)
    cv2.imwrite('testFlooded.jpg', dilated_edge_image) #TODO write
    #Find contours of black shapes
    contours, _ = cv2.findContours(dilated_edge_image, 1, 2)

    #Filter small elements out of the contours and filter to large elements
    contours = filter(lambda x: min_contour_length < cv2.arcLength(x, True) < max_contour_length, contours)
    #Approximate contour with less points to smooth the contour
    contours = map(lambda x: cv2.approxPolyDP(x, approx_precision*cv2.arcLength(x, True), True), contours)

    for contour in contours:
        values = dict()

        color = find_shape_color(contour, image)

        #For each possible shape, calculate the matching
        for shape in shapes:
            values[cv2.matchShapes(contour, shape.contour, 1, 0)] = shape(color)

        #Get the best match and check if it is less than the max offset
        minimum = min(values)
        if minimum < max_offset_shape:
            cv2.drawContours(gray_image, [contour], 0, (255, 0, 0), 3)
            cv2.putText(gray_image, values.get(minimum).__class__.__name__ + ' ' + color, tuple(contour[0].tolist()[0]),
                        cv2.FONT_HERSHEY_PLAIN, 3.0, (255, 0, 0))

    return gray_image, dilated_edge_image


def fill_image(image):
    """
    This method fills the image with white pixels, except for shapes.
    The method uses the flood fill algorithm after making a black corner around the image.
    """
    image = cv2.copyMakeBorder(image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    cv2.imwrite('testNotFlooded.jpg', image)    # TODO write
    cv2.floodFill(image, None, (0, 0), 255)
    return image


def find_center(contour):
    """
    Find the center of a contour.
    This method calculates the center of mass
    """
    moments = cv2.moments(contour)
    return int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])


def find_shape_color(contour, image):
    """
    Find the color of the contour which represents a shape.
    This function uses the center of mass, and get the pixel color from it from the image
    """
    center = find_center(contour)
    x, y, z = image.getpixel(center)
    _, value = min(map(lambda (r, g, b): (abs(r-x) + abs(g-y) + abs(b-z), (r, g, b)), colors.keys()))

    print x, y, z, colors[value]
    return colors[value]


if __name__ == '__main__':
    img = Image.open('C:\Users\Mattias\PycharmProjects\P-O-Geel-2\TestSuite\Images\\4.jpg')
    gray_with_contour, processed = process_picture(img)
    cv2.imwrite('testc.jpg', gray_with_contour)     # TODO write
    cv2.imwrite('testg.jpg', processed)             # TODO write