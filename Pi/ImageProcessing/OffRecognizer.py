from time import time
from PIL import Image
import cv2
from math import pi
from Shapes import *
import colorsys
import os
import glob


min_contour_length = 75    # The minimum length of the contour of a shape, used to filter
max_contour_factor = 0.6
canny_threshold1 = 3       # Thresholds for the canny edge detection algorithm
canny_threshold2 = 10
# 15 45
approx_precision = 0.01    # The approximation of the contour when using the Ramer-Douglas-Peucker (RDP) algorithm
iterations = 2             # The amount of iterations to dilate the edges to make the contours of the shapes closed
# 2
max_shape_offset = 0.2
shapes = [Rectangle, Star, Ellipse, Heart]
i = 0


def process_picture(image):
    global i

    try:
        #Filter giant rectangle of the image itself
        res_x, res_y = image.size
        max_contour_length = (2*res_x + 2*res_y)*max_contour_factor

        #Load image gray scale
        #gray_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
        #gray_image = cv2.GaussianBlur(gray_image, (3, 3), 3)
        gray_image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2LAB)
        gray_image = cv2.cvtColor(gray_image, cv2.COLOR_RGB2GRAY)
        gray_image = cv2.GaussianBlur(gray_image, (5, 5), 2)
        #Find edges in image
        edge_image = cv2.Canny(gray_image, canny_threshold1, canny_threshold2)

        cv2.imshow('e-image', edge_image)
        #Make lines thicker to make found edges of shapes closed
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        dilated_edge_image = cv2.dilate(edge_image, element, iterations=iterations)
        cv2.imshow('d-image', dilated_edge_image)
        #Fill the rest of the image => result = black shapes, rest is white

        #filled_image = fill_image(dilated_edge_image)
        filled_image = dilated_edge_image
        #Find contours of black shapes
        contours, _ = cv2.findContours(filled_image, 1, 2)

        #Filter small elements out of the contours and filter to large elements
        contours = filter(lambda x: min_contour_length < cv2.arcLength(x, True) < max_contour_length, contours)
        #Approximate contour with less points to smooth the contour
        #contours = map(lambda x: cv2.approxPolyDP(x, approx_precision*cv2.arcLength(x, True), True), contours)
        contours = filter(lambda x: len(x) > 2, contours)

        sorted_contours = list(map(lambda c: (find_center(c), cv2.arcLength(c, True), c), contours))
        sorted_contours = sorted(sorted_contours)

        contours2 = []

        for ((x, y), l, contour) in sorted_contours[:]:
            if not ((x, y), l, contour) in sorted_contours:
                continue
            close_by = filter(lambda ((x1, y1), l1, c1): (x1*0.95 <= x <= x1*1.05) and (y1*0.95 <= y <= y1*1.05),
                              sorted_contours)
            _, large_contour = sorted(map(lambda (_, length, con): (length, con), close_by), reverse=True)[0]
            contours2.append(large_contour)
            for element in close_by:
                sorted_contours.remove(element)

        contours = contours2

    except TypeError:
        return []

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
        if minimum < max_shape_offset:
            #cv2.drawContours(gray_image, [contour], 0, (255, 0, 0), 1)
            #cv2.putText(gray_image, values[minimum].__class__.__name__ + color, tuple(contour[0].tolist()[0]),
            #            cv2.FONT_HERSHEY_PLAIN, 3.0, (255, 0, 0))
            found_shapes.append(values.get(minimum))
            #TODO collect features and feed to network
    #cv2.imshow('image', gray_image)
    #cv2.waitKey(0)
    i += 1
    return found_shapes


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


def get_features(contour):
    result = []
    for l in invariant_moments(contour).tolist():
        result.extend(l)
    result.append(circularity_degree(contour))
    result.append(rectangle_degree(contour))
    result.append(sphericity_degree(contour))
    result.append(concavity_degree(contour))
    result.append(flat_degree(contour))
    return result


def invariant_moments(contour):
    return cv2.HuMoments(cv2.moments(contour))


def circularity_degree(contour):
    return (cv2.arcLength(contour, True)**2)/cv2.contourArea(contour)


def rectangle_degree(contour):
    _, _, width, height = cv2.boundingRect(contour)
    area = (width*height)
    return cv2.contourArea(contour)/area


def sphericity_degree(contour):
    c, r = cv2.minEnclosingCircle(contour)
    print str(cv2.contourArea(contour)), str(pi*(r**2))
    return cv2.contourArea(contour)/(pi*(r**2))


def concavity_degree(contour):
    return 1 - (cv2.contourArea(contour)/cv2.contourArea(cv2.convexHull(contour)))


def flat_degree(contour):
    _, _, width, height = cv2.boundingRect(contour)
    return float(width)/height


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


# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    path = "/home/nooby4ever/Desktop/benjamin/600x450/"
    os.chdir(path)
    for file in glob.glob("*.jpg"):
        print file
        map(lambda x: x.__class__, process_picture(Image.open(path + file)))

