from shapes import *


class Grid(object):
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
        with open(path_to_grid_file, 'r') as grid_file:
            grid_str = grid_file.read().replace('\n', '').strip(';')
            grid_rows = (row.split(',') for row in grid_str.split(';'))

            def convert(x):
                if x is "-":
                    return None
                colour, shape = x.split("$")

                shape_map = {"rectangle": Rectangle,
                             "star": Star,
                             "heart": Heart,
                             "ellipse": Ellipse}

                return shape_map[shape](color=colour)

            points = list(map(convert, row) for row in grid_rows)
        return Grid(points)

    @classmethod
    def from_empty(cls, n_cols, n_rows):
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
        return self._points[y][x]

    #-------------------------------------------------------------------------
    # Methods
    #-------------------------------------------------------------------------
    def write_to_file(self, path_to_grid_file):
        """
        Save the grid to a file.
        """
        grid_str = ""
        for y in range(self.n_rows):
            for x in range(self.n_columns):
                point = self.get_point(x=x, y=y)
                if not point is None:
                    grid_str += (point[0] + "$" + point[1])
                else:
                    grid_str += "-"
                grid_str += ","
            grid_str = grid_str[:-1] + ";\n"

        with open(path_to_grid_file, 'w') as grid_file:
            grid_file.write(grid_str)

    def is_valid_position(self, x=None, y=None, pos=None):
        if not pos is None:
            x = pos[0]
            y = pos[1]
        return (0 <= x < self.n_columns) and (0 <= y < self.n_rows)


if __name__ == '__main__':
    grid = Grid.from_file("./test1.txt")

    grid.write_to_file("./test3.txt")