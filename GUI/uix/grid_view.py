#TODO: GridContainerWidget
#TODO: GridPointWidget
#TODO: ZeppelinGridView
from math import tan, pi

from domain.grid_handler import GridController

from util import colour as col
from kivy.graphics import *
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.properties import OptionProperty


class GridView(RelativeLayout):
    def __init__(self, **kwargs):
        super(GridView, self).__init__(kwargs)

        self._grid_controller = GridController()
        self._grid = None
        self._build_grid_points()
        self._draw_grid_lines()

    #-------------------------------------------------------------------------
    # Methods related to the grid representation.
    #-------------------------------------------------------------------------
    def load_new_grid(self, file_path):
        self._grid_controller.load_grid(file_path)

        self._clear_old_grid()
        self._build_grid_points()
        self._draw_grid_lines()

    def _clear_old_grid(self):
        self._grid = None
        self.canvas.clear()
        self.clear_widgets()

    def _build_grid_points(self):
        grid = self._grid_controller.grid

        #calculate distance between grid points.
        if self.width / (float(grid.n_columns) + 0.5) <= 2 * ((self.height / float(grid.n_rows)) / tan(pi/3.0)):
            x_dist = 1.0 / (float(grid.n_columns) + 0.5)
            y_dist = (.5 * x_dist) * tan(pi/3.0)
        else:
            y_dist = 1.0 / float(grid.n_rows)
            x_dist = (2 * y_dist) / tan(pi/3.0)

        #build create actual points on the grid.
        self._grid = []
        y_pos_hint = 0.0
        for i in range(grid.n_rows):
            x_pos_hint = 0.0
            self._grid.append([])
            if i % 2 == 1:
                x_pos_hint + 0.5 * x_dist

            for j in range(grid.n_columns):
                point = grid.get_point(x=j, y=i)
                if point is None:
                    colour = "None"
                    shape = "None"
                else:
                    colour = point.color
                    shape = point.shape

                new_grid_point = GridPoint(coord=(j, i), shape=shape, colour=colour)
                new_grid_point.pos_hint = {'x': x_pos_hint,
                                           'top': y_pos_hint}
                self.add_widget(new_grid_point)
                self._grid[i].append(new_grid_point)

            y_pos_hint += y_dist

    def _draw_grid_lines(self):
        n_rows = self._grid_controller.grid.n_rows
        n_cols = self._grid_controller.grid.n_columns

        is_flushed_left = True
        for i in range(n_rows):
            for j in range(n_cols):
                cur_point = self._grid[i][j]

                #horizontal line
                if j > 0:
                    other_point = self._grid[i][j-1]
                    if cur_point.shape == "None" or other_point.shape == "None":
                        self._draw_line(cur_point.pos, other_point.pos, col.GRAY)
                    else:
                        self._draw_line(cur_point.pos, other_point.pos, col.LIGHT_BLUE)

                #vertical lines
                if i > 0:
                    next_points = [self._grid[i-1][j]]
                    if is_flushed_left and j > 0:
                        next_points.append(self._grid[i-1][j-1])
                    if (not is_flushed_left) and j < (n_cols-1):
                        next_points.append(self._grid[i-1][j+1])

                    for other_point in next_points:
                        if cur_point.shape == "None" or other_point.shape == "None":
                            self._draw_line(cur_point.pos, other_point.pos, col.GRAY)
                        else:
                            self._draw_line(cur_point.pos, other_point.pos, col.LIGHT_BLUE)
            is_flushed_left = not is_flushed_left

    def _draw_line(self, pos_a, pos_b, colour):
        with self.canvas:
            Color(colour[0], colour[1], colour[2])
            Line(points=pos_a[0], pos_a[1], pos_b[0], pos_b[1])

    #-------------------------------------------------------------------------
    # Methods related to the zeppelin representation on the grid.
    #-------------------------------------------------------------------------


class GridPoint(Button):
    def __init__(self, **kwargs):
        super(GridPoint, self).__init__(kwargs)
        self._coord = kwargs["coord"]
        self.shape = kwargs["shape"]
        self.colour = kwargs["colour"]

    @property
    def coord(self):
        return self._coord

    shape = OptionProperty("None", options=["Star",
                                            "Rectangle",
                                            "Circle",
                                            "Heart",
                                            "None"])

    colour = OptionProperty("None", options=["White",
                                             "Blue",
                                             "Green",
                                             "Red",
                                             "Yellow",
                                             "None"])

    shape_img = {'Star': './img/grid_star.png',
                 'Rectangle': './img/grid_rectangle.png',
                 'Circle': './img/grid_circle.png',
                 'Heart': './img/grid_heart.png'}