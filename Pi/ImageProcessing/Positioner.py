from math import sqrt

factor_edge_max_edge = 1.5      # The factor which determines how long an edge between points can be
                                # with respect to the minimum edge

# Eens we onze resolutie hebben bepaalt en onze hoogte kennen, kunnen we exact de afstand tussen de middes uitrekenen.
# Hierdoor is het mogelijk om de factor zeer nauwkeurig te bepalen.


def interconnect_points(points):
    """
    Connect the given points which are next to each other in a grid.
    This function connects points which can be represented in a matrix with equal distance.
    It get the minimal distance between two points and judges from that that this is the distance between points
    in the matrix. It filters out all other edges which are longer than factor_edge_max_edge*min_distance
    """
    if len(points) >= 2:
        edges_and_distance = [(sqrt(abs(x_1-x_2)**2+abs(y_1-y_2)**2), (x_1, y_1), (x_2, y_2))
                              for (x_1, y_1) in points for (x_2, y_2) in points if (x_1, y_1) < (x_2, y_2)]

        min_distance, _, _ = min(edges_and_distance)

        connected_points = map(lambda (d, a, b): (a, b),
                               filter(lambda (d, a, b): d <= factor_edge_max_edge*min_distance, edges_and_distance))

        return connected_points

    return []

def find_in_grid(points):
