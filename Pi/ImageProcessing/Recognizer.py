from time import time
from PIL import Image
import cv2
from Shapes import *


min_contour_length = 100    # The minimum length of the contour of a shape, used to filter
max_contour_factor = 0.8
canny_threshold1 = 15       # Thresholds for the canny edge detection algorithm
canny_threshold2 = 45
approx_precision = 0.005    # The approximation of the contour when using the Ramer-Douglas-Peucker (RDP) algorithm
iterations = 2              # The amount of iterations to dilate the edges to make the contours of the shapes closed
max_shape_offset = 0.1

colors = {(40, 70, 70): 'Green',
          (40, 65, 110): 'Blue',
          (220, 170, 90): 'Yellow',
          (255, 255, 255): 'White',
          (160, 30, 70): 'Red'}

shapes = [Rectangle, Star, Ellipse, Heart]

def process_picture(image):
    counter = 0


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
    filled_image = fill_image(dilated_edge_image)
    #Find contours of black shapes
    contours, _ = cv2.findContours(filled_image, 1, 2)

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
        if minimum < max_shape_offset:
            cv2.drawContours(gray_image, [contour], 0, (255, 0, 0), 3)
            cv2.putText(gray_image, values.get(minimum).__class__.__name__ + ' ' + color, tuple(contour[0].tolist()[0]),
                        cv2.FONT_HERSHEY_PLAIN, 3.0, (255, 0, 0))
            counter=+ 1

    return gray_image, dilated_edge_image, counter


def fill_image(image):
    """
    This method fills the image with white pixels, except for shapes.
    The method uses the flood fill algorithm after making a black corner around the image.
    """
    image = cv2.copyMakeBorder(image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
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
    return colors[value]

def get_current_position():
    """
    Returns the current position of the zeppelin in the frame (should only be used at startup)
    """
    #TODO
    return (0,0)


if __name__ == '__main__':
    minres = (300, 300)
    for i in range(120):
        if i % 10 == 0:
            minres = (minres[0]+100, minres[1]+100)
        img = Image.open('/home/nooby4ever/Desktop/foto/' + str(minres[0]) + ' ' + str(i % 10))
        start = time()
        gray_with_contour, processed, counter = process_picture(img)
        endtime = time() - start
        print endtime, minres[0], counter
        cv2.imwrite('/home/nooby4ever/Desktop/found/' + str(minres[0]) + ' ' + str(i % 10) + 'z.jpg', gray_with_contour)
        cv2.imwrite('/home/nooby4ever/Desktop/found/' + str(minres[0]) + ' ' + str(i % 10) + 'other.jpg', processed)
        print i