from math import sqrt

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

def find_location(PIL):
    global _core, _imageprocessor

    shapes = _imageprocessor.process_picture(PIL)
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
        edges_and_distance = [shape1.distance_to_other(shape2), (shape1, shape2)
                              for shape1 in shapes for shape2 in shapes if shape1.center < shape2.center]

        min_distance, _, _ = min(edges_and_distance)

        connected_shapes = map(lambda (d, a, b): (a, b),
                               filter(lambda (d, a, b): d <= factor_edge_max_edge*min_distance, edges_and_distance))

        return connected_shapes

    return []

def find_in_grid(shapes):
    global _core

    grid = _core.get_grid()
    found_patterns = []

    start_element = shapes[0][0]

    for i in grid.n_rows:
        for j in grid.n_columns:
            if grid.get_point(i,j).color == start_element.color:
                found_patterns.append([((i, j), start_element)])

    for pattern in found_patterns:
        for pos, elem in pattern:
            colors = map(lambda (x, y): if x != elem: y.color else x.color,
                        filter(lambda (x, y): x == elem or y == elem, shapes))
            


















    for i in (0 .. grid.n_rows):
        for j in (0 .. grid.n_columns):
            candidate = grid.get_point(i,j)
            if candidate.color = shape[0].color:
                found_shapes.append((shape, (i,j)))

    for (_, (x,y)) in found_shapes:
        for shape in shapes[1:]:






