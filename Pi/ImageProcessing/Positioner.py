
from math import *
from copy import copy
from time import time
import os
import glob
from PIL import Image
import Grid
from Shapes import *
import Recognizer
from values import *
import threading


factor_edge_max_edge = 1.5      # The factor which determines how long an edge between points can be
                                # with respect to the minimum edge
_core = None                    # The core
_imageprocessor = Recognizer    # The image processing
grd = None
_last_position = (0, 0)


def set_core(core, off):
    global _core, _imageprocessor, grd

    _core = core
    if off:
        grd = Grid.Grid.from_file("C:\Users\Mattias\Desktop\grid.csv")
    else:
        grd = _core.get_grid()
    _imageprocessor = Recognizer


def find_location(pil, off):
    global _core, _imageprocessor, grd
    shapes = _imageprocessor.process_picture(pil)
    if len(shapes) == 0:
        return None, None, None

    connected_shapes = interconnect_shapes(shapes)
    (x, y), found_pos = find_in_grid(connected_shapes, grd)
    if len(found_pos) == 0:
        return None, None, None

    angle = calc_rotation(found_pos)
    print "positioner: ", str((x, y))
    return (x, y), (-sin(angle)+x, cos(angle)+y), angle


def interconnect_shapes(shapes):
    """
    Connect the given points which are next to each other in a grid.
    This function connects points which can be represented in a matrix with equal distance.
    It get the minimal distance between two points and judges from that that this is the distance between points
    in the matrix. It filters out all other edges which are longer than factor_edge_max_edge*min_distance
    """
    if len(shapes) >= 2:
        edges_and_distance = [(shape1.distance_to_other(shape2), (shape1, shape2))
                              for shape1 in shapes for shape2 in shapes if shape1.center < shape2.center]

        min_distance, _ = min(edges_and_distance)

        connected_shapes = map(lambda (d, a): a,
                               filter(lambda (d, a): d <= factor_edge_max_edge*min_distance, edges_and_distance))

        return connected_shapes

    return []


def find_in_grid(shapes, grid):
    global _last_position
    #Haal de echte nodes uit alle edges en maak een tuple met een bijhorende colorpoint
    color_points_and_shapes = map(lambda x: (ColorPoint(x.color), x), list(set(list(sum(shapes, ())))))

    def right_element(element, x, y):
        if not element.__eq__(x):
            return x
        return y

    #Add alle neighbour nodes van elk element aan de colorpoints
    for c_point, shape in color_points_and_shapes:
        connected_shapes = map(lambda (x, y): right_element(shape, x, y),
                               filter(lambda (x, y): x == shape or y == shape, shapes))
        for point, other_shape in color_points_and_shapes:
            if other_shape in connected_shapes:
                c_point.neighbours.add(point)

    #Haal enkel de colorpoints eruit
    points = map(lambda (x, y): x, color_points_and_shapes)

    #Populate color_points with initial possible solutions
    for c_point in points:
        for i in range(0, grid.n_rows):
            for j in range(0, grid.n_columns):
                if not grid.get_point(i, j) is None:
                    if c_point.color == grid.get_point(i, j).color:
                        c_point.possible_positions[(i, j)] = grid.get_neighbour_points(pos=(i, j))

    possible_points = reduce_solutions(points)

    if len(possible_points) == 0:
        return (None, None), []

    builded_color_patterns = build_patterns(possible_points)

    best_patterns = find_closest_match(builded_color_patterns, color_points_and_shapes, grid)

    best_patterns_shape = map(lambda x: add_shapes_to_pattern(x, color_points_and_shapes), best_patterns)

    best_patterns_shape_and_pos = map(lambda x: (find_position(x), x), best_patterns_shape)
    _, pos, best_pattern = min(map(lambda (x, y): (calc_distance(x, _last_position), x, y),
                                   best_patterns_shape_and_pos))
    _last_position = pos
    return pos, best_pattern


def add_shapes_to_pattern(pattern, color_points_and_shapes):
    best_pattern_shape = []
    for colorpoint, pos in pattern:
        for colorpoint2, shape in color_points_and_shapes:
            if colorpoint == colorpoint2:
                best_pattern_shape.append((shape, pos))
    return best_pattern_shape


def map_to_mm((x, y)):
    if x % 2 == 0:
        return y*400, x*400*sin((1.0/3)*pi)
    else:
        return y*400+200, x*400*sin((1.0/3)*pi)


def calc_distance((x, y), (a, b)):
    return sqrt((x + a)**2 + (y+b)**2)


def reduce_solutions(points):
    changed = True
    while changed:
        changed = False
        for p in points:
            changed_tmp = reduce_single_point(p, points)
            if changed_tmp and not changed:
                changed = True
    return points


def reduce_single_point(p, points):
    changed = False
    for point in points:
        if point in p.neighbours:
            for value in p.possible_positions.keys():
                to_delete = True
                for neighbour in p.possible_positions[value]:
                    if neighbour in point.possible_positions:
                        to_delete = False
                if to_delete:
                    del p.possible_positions[value]
                    changed = True
    return changed


def build_patterns(solutions):

    patterns = map(lambda x: [(solutions[0], x)], solutions[0].possible_positions.keys())
    element = solutions[0]

    def same_size_stop_condition(pats, size):
        if False in map(lambda x: len(x) == size, pats):
            return True
        return False

    seen_patterns = set(copy(map(frozenset, patterns)))
    start_time = time()
    while same_size_stop_condition(patterns, len(solutions)):
        for current_pattern in patterns[:]:
            if time()-start_time > 0.7:
                return []
            patterns.remove(current_pattern)
            for element, position_element in current_pattern:
                for neighbour in element.neighbours:
                    for position_neighbour in neighbour.possible_positions.keys():
                        if position_element in neighbour.possible_positions[position_neighbour]\
                                and not neighbour in map(lambda (x, y): x, current_pattern)\
                                and not position_neighbour in map(lambda (x, y): y, current_pattern):
                            new_pattern = copy(current_pattern)
                            new_pattern.append((neighbour, position_neighbour))
                            if not frozenset(new_pattern) in seen_patterns:
                                patterns.append(new_pattern)
                                seen_patterns.add(frozenset(new_pattern))

    return list(set(map(tuple, map(sorted, patterns))))


def find_closest_match(patterns, colors_and_shapes, grid):
    mx, best_pattern = 0, [[]]
    for pattern in patterns:
        value = 0
        for element, element_position in pattern:
            _, shape = filter(lambda (x, y): x == element, colors_and_shapes)[0]
            if shape.eq_no_center(grid.get_point(pos=element_position)):
                value += 1

        if value == mx:
            best_pattern.append(pattern)
        elif value > mx:
            mx = value
            best_pattern = [pattern]
    return best_pattern


def find_position(best_pattern):
    mx = (cam_width / 2.0)
    my = (cam_height / 2.0)

    def middle_of_coordinates(coordinates1, coordinates2):
        return (coordinates1[0] + coordinates2[0])/float(2), (coordinates1[1] + coordinates2[1])/float(2)

    #calculate the middle of a triangle.
    def middle_of_triangle(coordinates1, coordinates2, coordinates3):
        return (coordinates1[0] + coordinates2[0] + coordinates3[0])/float(3),\
               (coordinates1[1] + coordinates2[1] + coordinates3[1])/float(3)

    middle_of_shapes = []
    for i in range(0, len(best_pattern)):
        for j in range(i, len(best_pattern)):
            #(shape,(px,py))
            tuple1 = best_pattern[i]
            tuple2 = best_pattern[j]
            #Do not compare shapes that are in a bigger triangle than the smallest possible.
            if fabs(tuple1[1][0]-tuple2[1][0]) < 2 and fabs(tuple1[1][1]-tuple2[1][1]) < 2:
                element = (middle_of_coordinates(tuple1[1], tuple2[1]),
                           middle_of_coordinates(tuple1[0].center, tuple2[0].center))
                #Add positions to the list which are in the middle between 2 shapes.
                if not(element in middle_of_shapes):
                    middle_of_shapes.append(element)
            #Add positions to the list which are in the middle of a triangle.
            if i != j:
                for k in range(j+1, len(best_pattern)):
                    tuple3 = best_pattern[k]
                    if fabs(tuple1[1][0]-tuple3[1][0]) < 2 and fabs(tuple1[1][1]-tuple3[1][1]) < 2\
                            and fabs(tuple2[1][0]-tuple3[1][0]) < 2 and fabs(tuple2[1][1]-tuple3[1][1]) < 2:
                        element = (middle_of_triangle(tuple1[1], tuple2[1], tuple3[1]),
                                   middle_of_triangle(tuple1[0].center, tuple2[0].center, tuple3[0].center))
                        if not(element in middle_of_shapes):
                            middle_of_shapes.append(element)
    length = 100000000000000000000000000000
    x = 0
    y = 0
    for (cx, cy), (ox, oy) in middle_of_shapes:
        length2 = sqrt((ox - mx)**2 + (oy - my)**2)
        if length2 < length:
            length = length2
            x = cx
            y = cy
    return map_to_mm((x, y))


def calc_rotation(shapes):
    global grd
    shape_2, q, z = None, None, None
    shape_1, x, y = None, None, None
    for shape1, (a, b) in shapes:
        for shape2, (c, d) in shapes:
            if (c, d) in grd.get_neighbour_points(a, b):
            #if (a, b) in _core.get_grid().get_neighbour_points(x, y):
                shape_1 = shape1
                x = a
                y = b
                shape_2 = shape2
                q = c
                z = d
                break
        if not (shape_2 is None and q is None and z is None):
            break

    if x >= q:
        lower_shape = shape_1
        (lx, ly) = (x, y)
        higher_shape = shape_2
        (hx, hy) = (q, z)
    else:
        higher_shape = shape_1
        (hx, hy) = (x, y)
        lower_shape = shape_2
        (lx, ly) = (q, z)

    if x != q:
        angle = diff_row_angle((lx, ly), (hx, hy))
        tx, ty = calc_theoretical_position_different(angle, lower_shape)
    else:
        tx, ty = calc_theoretical_position_same(ly, hy, lower_shape)

    a = sqrt((tx - higher_shape.center[0])**2 + (ty - higher_shape.center[1])**2)
    b = sqrt((tx - lower_shape.center[0])**2 + (ty - lower_shape.center[1])**2)
    c = sqrt((lower_shape.center[0] - higher_shape.center[0])**2 + (lower_shape.center[1] - higher_shape.center[1])**2)

    angle = find_angle(a, b, c)
    if left_turn(lower_shape.center, (tx, ty), higher_shape.center) > 0:
        left = True
    else:
        left = False

    if (lower_shape.center[1] > ty and not left)\
            or (ty > lower_shape.center[1] and left):
        angle = 2*pi-angle
    if lower_shape.center[1] == ty:
        if (lower_shape.center[0] > tx and higher_shape.center[1] < ty)\
                or (lower_shape.center[0] < tx and ty < higher_shape.center[1]):
            angle = 2*pi-angle
    return angle


#if negative => right turn in b, if positive => left turn in b, if 0 collinear
#caution when using this because this is used in the image coordination format
def left_turn(a, b, c):
    return (b[1] - a[1])*(c[0] - a[0]) - (b[0] - a[0])*(c[1] - a[1])


def calc_theoretical_position_different(angle, shape_low):
    x, y = shape_low.center
    if round(angle*180/pi) == 60:
        x += cos(angle)*50
        y -= sin(angle)*50
    elif round(angle*180/pi) == 120:
        x += cos(angle)*50
        y -= sin(angle)*50
    return x, y


def calc_theoretical_position_same(ly, hy, shape_low):
    if ly > hy:
        x = shape_low.center[0]-50
    else:
        x = shape_low.center[0]+50
    return x, shape_low.center[1]


def diff_row_angle((lx, ly), (hx, hy)):

    #Odd
    if lx % 2 == 0:

        #Left
        if ly == hy:
            angle = (1.0/3.0)*pi

        else:
            #Right
            angle = (2.0/3.0)*pi
    else:
        #left
        if ly == hy:
            angle = (2.0/3.0)*pi
        else:
            #right
            angle = (1.0/3.0)*pi

    return angle


def get_currentposition():
    global _last_position
    return _last_position


def find_angle(a, b, c):
    return acos((-a**2 + b**2 + c**2)/(2*b*c))


class ColorPoint(object):

    def __init__(self, color, possible_positions=None, neighbours=None):
        self._color = color
        if possible_positions is None:
            possible_positions = dict()
        self._possible_positions = possible_positions
        if neighbours is None:
            neighbours = set()
        self._neighbours = neighbours

    @property
    def possible_positions(self):
        return self._possible_positions

    @possible_positions.setter
    def set_possible_positions(self, possible_positions):
        self._possible_positions = possible_positions

    @property
    def color(self):
        return self._color

    @color.setter
    def set_color(self, color):
        self._color = color

    @property
    def neighbours(self):
        return self._neighbours

    @neighbours.setter
    def set_neighbours(self, neighbours):
        self._neighbours = neighbours

    def __repr__(self):
        build_string = ""
        for value in self.possible_positions:
            build_string += str(value) + " "
        return "Color: " + str(self.color) + " Positions: " + build_string
"""
if __name__ == '__main__':
    sim = Simulator(None)
    threading.Thread(target=sim.start, args=[False, False]).start()
    sim.start(False, False)
    os.chdir("C:\Users\Mattias\Desktop\_neural_network_oracle\Pi")
    for filee in sorted(glob.glob("*.jpeg"), key=len):
        if not 'a' in str(filee):
            continue
        print str(filee)
        set_core(None, True)
        pos, _, pangle = find_location(Image.open('C:\Users\Mattias\Desktop\_neural_network_oracle\Pi\\' + filee), True)
        if not pos is None:
            (x, y) = pos
            print str(pos)
            sim._our_zeppelin.set_current_position(x, y)
        raw_input()
"""
