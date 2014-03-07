#FIXME: proper import when refactored.
from grid import Grid


class GridController(object):
    """
    Grid controller forms the interface between the UI
    and the domain objects.
    """
    def __init__(self):
        self._grid = Grid.from_empty(10, 10)

    #FIXME: might not be nicest way to do this
    @property
    def grid(self):
        return self._grid

    def load_grid(self, file_path):
        """
        Load a new grid from the specified file.

        Parameters
        ----------
        file_path : String
            Path + File name to the file that specifies the grid.
        """
        self._grid = Grid.from_file(file_path)