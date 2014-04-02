from time import time
from PIL import Image
import cv2
from math import pi
from Shapes import *
import colorsys
import os
import glob
from pybrain.structure import FeedForwardNetwork
from pybrain.tools.customxml import NetworkReader



min_contour_length = 100    # The minimum length of the contour of a shape, used to filter
max_contour_factor = 0.6
canny_threshold1 = 5       # Thresholds for the canny edge detection algorithm
canny_threshold2 = 18
approx_precision = 0.01    # The approximation of the contour when using the Ramer-Douglas-Peucker (RDP) algorithm
iterations = 2             # The amount of iterations to dilate the edges to make the contours of the shapes closed
max_shape_offset = 0.2
shape_map = {0: Rectangle,
             1: Ellipse,
             2: Heart,
             3: Star}

feature_size = (30, 30)
start_time = time()
net = NetworkReader.readFrom("/home/pi/P-O-Geel2/Pi/ImageProcessing/Networks/network40.xml")
print str(time()-start_time)


def process_picture(image):
    global shape_map, net, feature_size, canny_threshold1, canny_threshold2, max_contour_factor, min_contour_length,\
        approx_precision, iterations, max_shape_offset

    try:
        #Filter giant rectangle of the image itself
        res_x, res_y = image.size
        max_contour_length = (2*res_x + 2*res_y)*max_contour_factor

        #Load image gray scale
        gray_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2LAB)
        gray_image = cv2.cvtColor(gray_image, cv2.COLOR_RGB2GRAY)
        gray_image = cv2.GaussianBlur(gray_image, (5, 5), 2)
        #Find edges in image
        edge_image = cv2.Canny(gray_image, canny_threshold1, canny_threshold2)

        #Make lines thicker to make found edges of shapes closed
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        dilated_edge_image = cv2.dilate(edge_image, element, iterations=iterations)
        #Fill the rest of the image => result = black shapes, rest is white

        #Find contours of black shapes
        contours, _ = cv2.findContours(dilated_edge_image, 1, 2)

        #Filter small elements out of the contours and filter to large elements
        contours = filter(lambda x: min_contour_length < cv2.arcLength(x, True) < max_contour_length, contours)
        #Approximate contour with less points to smooth the contour
        contours = filter(lambda x: len(x) > 2, contours)

        sorted_contours = list(map(lambda c: (find_center(c), cv2.arcLength(c, True), c), contours))
        sorted_contours = sorted(sorted_contours)

        contours2 = []

        for ((x, y), l, contour) in sorted_contours[:]:
            if not ((x, y), l, contour) in sorted_contours:
                continue
            close_by = filter(lambda ((x1, y1), l1, c1): abs(x1 -x) <= 50 and abs(y1 -y) <= 50, sorted_contours)
            _, large_contour = sorted(map(lambda (_, length, con): (length, con), close_by), reverse=True)[0]
            contours2.append(large_contour)
            for element in close_by:
                sorted_contours.remove(element)

        contours = contours2

    except TypeError:
        return []

    found_shapes = []

    contours = filter(lambda c: len(c) > 2, contours)

    for contour in contours:
        color = find_shape_color(contour, image)
        center = find_center(contour)
        features = None

        if is_valid_shape(contour, image):
            features = get_features(contour, gray_image)
            if features is not None and not is_on_edge(contour, gray_image.shape):
                st = time()
                net_return = net.activate(features)
                print "neural time: " + str(time()-st)
                r = net_return.argmax(axis=0)
                found_shapes.append(shape_map[r](color, center))
                cv2.putText(gray_image, shape_map[r](color, center).__class__.__name__ + " " + str(color), tuple(contour[0].tolist()[0]), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
            else:
                found_shapes.append(UnrecognizedShape(color, center))
            cv2.drawContours(gray_image, [contour], 0, (255, 0, 0), -1)

    return found_shapes


def fill_image(image):
    """
    This method fills the image with white pixels, except for shapes.
    The method uses the flood fill algorithm after making a black corner around the image.
    """
    image = cv2.copyMakeBorder(image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    cv2.floodFill(image, None, (0, 0), 255)
    return image


def is_on_edge(contour, (dh, dw)):
    coordinates = [(h, w) for [[h, w]] in contour]
    return any(filter(lambda (x, y): x <= 1 or x == dw or y == dh or y <= 1, coordinates))


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


def get_features(contour, image):
    (x, y), r = cv2.minEnclosingCircle(contour)
    left_up_x = x-r
    left_up_y = y-r
    right_down_x = x+r
    right_down_y = y+r

    height, width = image.shape
    blank_image = np.zeros((height, width))
    cv2.drawContours(blank_image, [contour], 0, (255, 0, 0), -1)

    if left_up_x < 0 or left_up_y < 0 or right_down_x < 0 or right_down_x < 0:
        return None

    sliced = blank_image[left_up_y:right_down_y, left_up_x:right_down_x]
    scaled_slice = cv2.resize(sliced, feature_size)
    return scaled_slice.flat


def is_valid_shape(contour, image):
    return (not is_gray(contour, image)) and is_full_shape(contour)


def is_gray(contour, image):
    offset = 20
    white = 220

    center = find_center(contour)
    x, y, z = image.getpixel(center)

    if x > white or y > white or z > white:
        return False
    if abs(x - y) < offset and abs(x - z) < offset and abs(y - z) < offset:
        return True
    return False


def is_full_shape(contour):
    area = cv2.contourArea(contour)
    return area/cv2.arcLength(contour, True) > 3


# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    path = "/home/nooby4ever/Desktop/benjamin/600x450/"
    os.chdir(path)
    for file in glob.glob("*.jpg"):
        print file
        map(lambda x: x.__class__, process_picture(Image.open(path + file)))
