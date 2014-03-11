from time import time
from PIL import Image
from random import randint
import cv2
from Shapes import *
import colorsys


min_contour_length = 100    # The minimum length of the contour of a shape, used to filter
max_contour_factor = 0.8
canny_threshold1 = 5       # Thresholds for the canny edge detection algorithm
canny_threshold2 = 15
approx_precision = 0.005    # The approximation of the contour when using the Ramer-Douglas-Peucker (RDP) algorithm
iterations = 5              # The amount of iterations to dilate the edges to make the contours of the shapes closed
max_shape_offset = 0.1
i = 1

#colors = {(40, 70, 70): 'green',
#          (40, 65, 110): 'blue',
#          (220, 170, 90): 'yellow',
#          (255, 255, 255): 'white',
#          (160, 30, 70): 'red'}

shapes = [Rectangle, Star, Ellipse, Heart]


def process_picture(image):
    global i
    #Filter giant rectangle of the image itself
    res_x, res_y = image.size
    max_contour_length = (2*res_x + 2*res_y)*max_contour_factor

    #Load image gray scale
    lab_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2LAB)
    cv2.imwrite('a/' + str(i)+'lab.jpg', lab_image)
    lab_blur_image = cv2.GaussianBlur(lab_image, (3, 3), 3)
    gray_image = cv2.cvtColor(np.asarray(lab_blur_image), cv2.COLOR_BGR2GRAY)
    cv2.imwrite('a/' + str(i) + 'gray.jpg', gray_image)
    #Find edges in image
    edge_image = cv2.Canny(gray_image, canny_threshold1, canny_threshold2)
    cv2.imwrite('a/' + str(i)+'canny.jpg', edge_image)

    #Make lines thicker to make found edges of shapes closed
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated_edge_image = cv2.dilate(edge_image, element, iterations=iterations)
    cv2.imwrite('a/' + str(i) + 'dilate.jpg', dilated_edge_image)
    #Fill the rest of the image => result = black shapes, rest is white)
    #Find contours of black shapes
    contours, _ = cv2.findContours(dilated_edge_image, 1, 2)
    cv2.imwrite('a/' + str(i) + 'fill1.jpg', dilated_edge_image)
    for contour in contours:
        cv2.drawContours(dilated_edge_image, [contour], 0, (255, 0, 0), 3)
        cv2.floodFill(dilated_edge_image, None, find_center(contour), 0)
        cv2.floodFill(dilated_edge_image, None, find_center(contour), 255)
    #filled_image = fill_image(dilated_edge_image)
    cv2.imwrite('a/' + str(i) + 'fill2.jpg', dilated_edge_image)
    contours, _ = cv2.findContours(dilated_edge_image, 1, 2)

    #Filter small elements out of the contours and filter to large elements
    #contours = filter(lambda x: min_contour_length < cv2.arcLength(x, True) < max_contour_length, contours)
    #Approximate contour with less points to smooth the contour
    contours = map(lambda x: cv2.approxPolyDP(x, approx_precision*cv2.arcLength(x, True), True), contours)

    found_shapes = []

    for contour in contours:
        values = dict()

        color = find_shape_color(contour, image)
        center = find_center(contour)

        #For each possible shape, calculate the matching
        for shape in shapes:
            values[cv2.matchShapes(contour, shape.contour, 1, 0)] = shape(color, center)

        #Get the best match and check if it is less than the max offset
        minimum = min(values)
        #if minimum < max_shape_offset:
        cv2.drawContours(gray_image, [contour], 0, (255, 0, 0), 3)
        cv2.putText(gray_image, color, tuple(contour[0].tolist()[0]),
                    cv2.FONT_HERSHEY_PLAIN, 3.0, (255, 0, 0))

        found_shapes.append(values.get(minimum))
    cv2.imwrite('a/' + str(i) + 'result.jpg', gray_image)
    i += 1
    return found_shapes


def fill_image(image):
    """
    This method fills the image with white pixels, except for shapes.
    The method uses the flood fill algorithm after making a black corner around the image.
    """
    image = cv2.copyMakeBorder(image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    cv2.floodFill(image, None, (0, 0), 0)
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
    #_, value = min(map(lambda (r, g, b): (abs(r-x) + abs(g-y) + abs(b-z), (r, g, b)), colors.keys()))
    h, s, v = colorsys.rgb_to_hsv(x/255.0, y/255.0, z/255.0)
    if 0 <= s*100 <= 25 and v*100 >= 80:
        return 'white'
    if 30 <= h*360 < 75:
        return 'yellow'
    elif 0 <= h*360 <= 30 or 329 <= h*360 <= 360:
        return 'red'
    elif 200 <= h*360 < 329:
        return 'blue'
    elif 75 <= h*360 < 200:
        return 'green'