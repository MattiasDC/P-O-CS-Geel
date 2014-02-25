from math import sqrt
from ImageProcessing import Grid
from ImageProcessing.Shapes import *
from ImageProcessing import Recognizer
from copy import deepcopy

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


def find_in_grid(shapes, grid):
    #global _core

    #grid = _core.get_grid()
    found_patterns = []

    start_element = shapes[0][0]

    for i in range(grid.n_rows):
        for j in range(grid.n_columns):
            if grid.get_point(i, j).color == start_element.color:
                found_patterns.append([((i, j), start_element)])

    def right_element(element, x, y):
        if not element.__eq__(x):
            return x
        return y

    for pattern in found_patterns:
        old_pattern = pattern
        for position, elem in pattern:
            connected_to = map(lambda (x, y): right_element(elem, x, y),
                               filter(lambda (x, y): x == elem or y == elem, shapes))
            to_connect = filter(lambda x: not x in map(lambda (_, a): a, pattern), connected_to)

            neighbour_colors = map(lambda (x, y):
                                   (grid.get_point(x, y).color, (x, y)), grid.get_neighbour_points(pos=position))

            for shape in to_connect:
                can_place_positions = map(lambda (x, pos): pos,
                                          filter(lambda (x, pos): x == shape.color, neighbour_colors))
                for place_position in can_place_positions:
                    pattern = deepcopy(old_pattern)
                    pattern.append((place_position, shape))
                    found_patterns.append(pattern)

        found_patterns.remove(old_pattern)

    return found_patterns


if __name__ == '__main__':
    grid = Grid.Grid.from_file('/home/nooby4ever/Desktop/grid.csv')


    print find_in_grid([(Rectangle('white'), Rectangle('blue')), (Rectangle('white'), Rectangle('yellow'))], grid)