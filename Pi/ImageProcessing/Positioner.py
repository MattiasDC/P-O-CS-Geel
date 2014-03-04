from math import sqrt
from ImageProcessing import Grid
from ImageProcessing.Shapes import *
from ImageProcessing import Recognizer
from copy import copy
from time import time

factor_edge_max_edge = 1.5      # The factor which determines how long an edge between points can be
                                # with respect to the minimum edge
_core = None                    # The core
_imageprocessor = None          # The image processing

# Eens we onze resolutie hebben bepaalt en onze hoogte kennen, kunnen we exact de afstand tussen de middes uitrekenen.
# Hierdoor is het mogelijk om de factor zeer nauwkeurig te bepalen.


def set_core(core):
    global _core, _imageprocessor

    _core = core
    _imageprocessor = Recognizer


def find_location(pil):
    global _core, _imageprocessor

    shapes = _imageprocessor.process_picture(pil)
    connected_shapes = interconnect_shapes(shapes)
    find_in_grid(connected_shapes)


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

        connected_shapes = map(lambda (d, a, b): (a, b),
                               filter(lambda (d, a, b): d <= factor_edge_max_edge*min_distance, edges_and_distance))

        return connected_shapes

    return []


def find_in_grid(shapes, grd):
    #Haal de echte nodes uit alle edges en maak een tuple met een bijhorende colorpoint
    color_points = map(lambda x: (ColorPoint(x.color), x), list(set(list(sum(shapes, ())))))

    def right_element(element, x, y):
        if not element.__eq__(x):
            return x
        return y

    #Add alle neighbour nodes van elk element aan de colorpoints
    for c_point, shape in color_points:
        connected_shapes = map(lambda (x, y): right_element(shape, x, y),
                               filter(lambda (x, y): x == shape or y == shape, shapes))
        for point, other_shape in color_points:
            if other_shape in connected_shapes:
                c_point.neighbours.add(point)

    #Haal enkel de colorpoints eruit
    points = map(lambda (x, y): x, color_points)

    #Populate color_points with initial possible solutions
    for c_point in points:
        for i in range(0, grd.n_rows):
            for j in range(0, grd.n_columns):
                if not grd.get_point(i, j) is None:
                    if c_point.color == grd.get_point(i, j).color:
                        c_point.possible_positions[(i, j)] = grd.get_neighbour_points(pos=(i, j))

    possible_points = reduce_solutions(points)

    builded_color_patterns = build_patterns(possible_points)

    find_closest_match(builded_color_patterns, color_points)


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

    while same_size_stop_condition(patterns, len(solutions)):
        for current_pattern in patterns[:]:
            if not len(current_pattern) == len(solutions):
                patterns.remove(current_pattern)
                for element, position_element in current_pattern:
                    for neighbour in element.neighbours:
                        for position_neighbour in neighbour.possible_positions.keys():

                            if position_element in neighbour.possible_positions[position_neighbour]\
                                    and not neighbour in map(lambda (x, y): x, current_pattern):
                                new_pattern = copy(current_pattern)
                                new_pattern.append((neighbour, position_neighbour))
                                patterns.append(new_pattern)

    return list(set(map(tuple, map(sorted, patterns))))


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

if __name__ == '__main__':
    grid = Grid.Grid.from_file('C:/Users/Mattias/Desktop/grid.csv')

    start_time = time()
    s_1 = Star('yellow', (5, 2))
    s_2 = Ellipse('blue', (5, 3))
    result = find_in_grid([(Rectangle('yellow', (4, 1)), s_1), (s_1, s_2), (s_2, Star('white', (5, 4)))], grid)
    print result
    print str(time()-start_time)