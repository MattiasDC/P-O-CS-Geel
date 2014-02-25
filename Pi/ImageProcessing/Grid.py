from Shapes import *


class Grid(object):
    _points = None          # The grid

    """
    Grid datastructure that stores the triangle grid used in the P&O project.

    The first row of the grid is flushed-left, and each row contains the same
    number of elements.
    """
    #-------------------------------------------------------------------------
    # Constructors
    #-------------------------------------------------------------------------
    def __init__(self, points):
        self._points = points

    @classmethod
    def from_file(cls, path_to_grid_file):
        """
        Load a grid object from a file.
        """
        shape_map = {"R": Rectangle,
                             "S": Star,
                             "H": Heart,
                             "C": Ellipse}

        color_map = {'W': 'white',
                     'B': 'blue',
                     'G': 'green',
                     'R': 'red',
                     'Y': 'yellow'}
        points = list()

        with open(path_to_grid_file, 'r') as grid_file:
            for line in grid_file.readline.split('\n'):
                row = list()
                for shape in enumerate(line.split(',')):
                    row.append(shape_map.get(shape[0])(color_map.get(shape[1])))
                points.append(row)

        return Grid(points)

    @classmethod
    def from_empty(cls, n_cols, n_rows):
        """
        Create an empty grid object.
        """
        points = list(list(None for _ in range(n_cols)) for _ in range(n_rows))
        return Grid(points)

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    @property
    def n_rows(self):
        return len(self._points)

    @property
    def n_columns(self):
        if self.n_rows < 1:
            return 0
        else:
            return len(self._points[0])

    def get_point(self, x=None, y=None, pos=None):
        """
        Get the point at (x, y)

        Parameters
        ----------
        x : Int
            x position of the point.
        y : Int
            y position of the point

        Pre-conditions
        --------------
        | self.is_valid_position(x, y)

        Return
        ------
        | (<colour>, <shape>) or None
        """
        if not pos is None:
            x = pos[0]
            y = pos[1]
        if not self.is_valid_position(x, y):
            return None
        return self._points[y][x]

    def get_neighbour_points(self, x=None, y=None, pos=None):
        if not pos is None:
            x = pos[0]
            y = pos[1]

        neighbours = [(x, y-1), (x+1, y-1), (x+1, y), (x+1, y+1), (x, y+1), (x-1, y)]

        return filter(lambda (a, b): self.is_valid_position(a, b), neighbours)

    #-------------------------------------------------------------------------
    # Methods
    #-------------------------------------------------------------------------

    def is_valid_position(self, x=None, y=None, pos=None):
        if not pos is None:
            x = pos[0]
            y = pos[1]
        return (0 <= x < self.n_columns) and (0 <= y < self.n_rows)


if __name__ == '__main__':
    grid = Grid.from_file("./test1.txt")