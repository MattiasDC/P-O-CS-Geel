#TODO: GridContainerWidget
#TODO: GridPointWidget
#TODO: ZeppelinGridView
from math import tan, pi

from domain.grid_handler import GridController
from util import colour as col
from kivy.graphics import *
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import OptionProperty

from kivy.lang import Builder


class GridView(RelativeLayout):
    def __init__(self, **kwargs):
        super(GridView, self).__init__(**kwargs)

        self._grid_controller = GridController()
        self._grid = None
        self._build_grid_points()
        self._draw_grid_lines()

    #-------------------------------------------------------------------------
    # Methods related to the grid representation.
    #-------------------------------------------------------------------------
    def load_new_grid(self, file_path):
        self._clear_old_grid()

        self._grid_controller.load_grid(file_path)
        self._build_grid_points()
        #add draw instruction once widgets initialised.
        self._grid[0][0].bind(pos=self._on_init_point)

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

        size_x = x_dist * 0.4
        size_y = (self.height / float(self.width)) * size_x

        #build create actual points on the grid.
        self._grid = []
        y_pos_hint = 1.0
        for i in range(grid.n_rows):
            x_pos_hint = 0.0
            self._grid.append([])
            if i % 2 == 1:
                x_pos_hint += 0.5 * x_dist

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
                new_grid_point.size_hint_x = size_x
                new_grid_point.size_hint_y = size_y

                self.add_widget(new_grid_point)
                self._grid[i].append(new_grid_point)

                x_pos_hint += x_dist

            y_pos_hint -= y_dist

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
                        self._draw_line(cur_point.center_in_window_coord,
                                        other_point.center_in_window_coord,
                                        col.DARK_GRAY, 1)
                    else:
                        self._draw_line(cur_point.center_in_window_coord,
                                        other_point.center_in_window_coord,
                                        col.DARK_BLUE, 1.5)

                #vertical lines
                if i > 0:
                    next_points = [self._grid[i-1][j]]
                    if is_flushed_left and j > 0:
                        next_points.append(self._grid[i-1][j-1])
                    if (not is_flushed_left) and j < (n_cols-1):
                        next_points.append(self._grid[i-1][j+1])

                    for other_point in next_points:
                        if cur_point.shape == "None" or other_point.shape == "None":
                            self._draw_line(cur_point.center_in_window_coord,
                                            other_point.center_in_window_coord,
                                            col.DARK_GRAY, 1)
                        else:
                            self._draw_line(cur_point.center_in_window_coord,
                                            other_point.center_in_window_coord,
                                            col.DARK_BLUE, 1.5)
            is_flushed_left = not is_flushed_left

    def _draw_line(self, pos_a, pos_b, colour, width):
        with self.canvas.before:
            Color(colour[0], colour[1], colour[2])
            Line(points=[pos_a[0], pos_a[1], pos_b[0], pos_b[1]], width=width)

    def _on_init_point(self, *args):
        self._draw_grid_lines()
        self._grid[0][0].unbind(pos=self._on_init_point)

    #-------------------------------------------------------------------------
    # Methods related to the zeppelin representation on the grid.
    #-------------------------------------------------------------------------


class GridPoint(Widget):
    def __init__(self, **kwargs):
        super(GridPoint, self).__init__(**kwargs)
        self._coord = kwargs["coord"]
        self.shape = kwargs["shape"]
        self.colour = kwargs["colour"]

    @property
    def coord(self):
        return self._coord

    def click(self):
        print self.to_window(self.pos[0], self.pos[1])

    shape = OptionProperty("None", options=["Star",
                                            "Rectangle",
                                            "Ellipse",
                                            "Heart",
                                            "None"])

    colour = OptionProperty("None", options=["White",
                                             "Blue",
                                             "Green",
                                             "Red",
                                             "Yellow",
                                             "None"])

    def _get_colour(self):
        return self._colour_map[self.colour]

    _colour_map = {"White": col.WHITE,
                   "Blue": col.BLUE,
                   "Green": col.GREEN,
                   "Red": col.RED,
                   "Yellow": col.YELLOW,
                   "None": col.GRAY} #FIXME

    @property
    def center_in_window_coord(self):
        pos = self.to_window(self.pos[0], self.pos[1])
        return pos[0] + 0.5 * self.size[0], pos[1] + 0.5 * self.size[1]


from kivy.app import App
from kivy.uix.floatlayout import FloatLayout


class GridViewApp(App):
    def build(self):
        interface = GridView()
        #
        #interface = RelativeLayout()
        #new_point = GridPoint(coord=(0, 0), shape="Heart", colour="Red")
        #new_point.pos_hint = {'x': 0.5,
        #                      'top': 0.8}
        #new_point.size_hint_y = 0.1
        #new_point.size_hint_x = 0.1
        #interface.add_widget(new_point)
        #
        #other_new_point = GridPoint(coord=(0, 0), shape="Star", colour="Blue")
        #other_new_point.pos_hint = {'x': 0.2,
        #                      'top': 0.4}
        #other_new_point.size_hint_y = 0.1
        #other_new_point.size_hint_x = 0.1
        #interface.add_widget(other_new_point)
        interface.load_new_grid('./grid.csv')

        return interface

Builder.load_file('./uix/grid_view.kv')