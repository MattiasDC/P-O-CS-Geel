#TODO: GridContainerWidget
#TODO: GridPointWidget
#TODO: ZeppelinGridView
from math import tan, pi
from kivy.uix.scatter import Scatter

from domain.grid_handler import GridController
from util import colour as col
from kivy.graphics import *
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import OptionProperty, NumericProperty, ListProperty, ObjectProperty, StringProperty

from kivy.clock import Clock

from util.colour import *

from kivy.lang import Builder


class ZeppelinScatter(Scatter):
    direction = NumericProperty(0)
    speed = NumericProperty(10.0)

    location_local = (0, 0)
    grid = ObjectProperty(None)

    x_left_bound = NumericProperty(0)
    x_right_bound = NumericProperty(0)

    y_top_bound = NumericProperty(0)
    y_bottom_bound = NumericProperty(0)
    team = StringProperty("None")

    colour_map = {"yellow": YELLOW_ZEPPELIN,
                  "red": RED_ZEPPELIN}

    img = ObjectProperty(None)

    def on_team(self, instance, value):
        self.img.color = self.colour_map[value]

    def __init__(self, **kwargs):
        super(ZeppelinScatter, self).__init__(**kwargs)

        ##self.grid = kwargs['grid']
        #self.calculate_bounds()

        self._zeppelin = kwargs['zeppelin']
        self.team = self._zeppelin.identifier

        self.trigger_resize = Clock.create_trigger(self.calculate_bounds, 0)
        self.trigger_reposition = Clock.create_trigger(self.calculate_bounds, 0)

    def on_grid(self, instance, value):
        self.grid.bind(size=self.trigger_resize)
        self.grid.bind(pos=self.trigger_reposition)

    def update(self, dt):
        x_l, x_r, y_b, y_t = self.grid.get_bounds()

        loc_x, loc_y = self._zeppelin.position
        grid = self.grid.grid_handler.grid

        self.location_local = (float(loc_x) / (float(400 * grid.n_columns) + 0.5), float(loc_y) / (float(400 * grid.n_rows)))
        width = x_r - x_l
        height = y_t - y_b
        self.pos = (x_l + width * self.location_local[0] - 0.5 * self.size[0], y_t - height * self.location_local[1] - 0.5 * self.size[1])

        if self._zeppelin.identifier == "yellow":
            self.direction = self._zeppelin.direction

        #if self.pos[0] <= x_l and self.speed == -10:
        #    if self.direction <= 0:
        #        self.direction = 0
        #        self.speed *= -1
        #    else:
        #        self.direction -= 5
        #elif self.pos[0] >= x_r and self.speed == 10:
        #    if self.direction >= 180:
        #        self.direction = 180
        #        self.speed *= -1
        #    else:
        #        self.direction += 5
        #else:
        #    self.pos = (self.pos[0] + self.speed, self.pos[1])

    def calculate_bounds(self, *args):
        (x_l, x_r, y_b, y_t) = self.grid.get_bounds()
        self.pos = [x_l - 0.5 * self.size[0], y_t - 0.5 * self.size[1]]


class GridViewContainer(FloatLayout):
    view = ObjectProperty(None)
    the_root = ObjectProperty(None)
    zeppelin_scatters = ListProperty([])

    def add_zeppelin(self, zeppelin):
        new_scatter = ZeppelinScatter(zeppelin=zeppelin)
        new_scatter.grid = self.view

        self.zeppelin_scatters.append(new_scatter)
        self.add_widget(new_scatter)

    def update(self, dt):
        for w in self.zeppelin_scatters:
            w.update(dt)


class GridView(FloatLayout):
    def __init__(self, **kwargs):
        super(GridView, self).__init__(**kwargs)

        self._lines = None
        self._grid_controller = GridController()
        self._grid = None

        self.trigger_init_point = Clock.create_trigger(self._on_init_point)
        self.trigger_resize = Clock.create_trigger(self._on_resize)
        self.trigger_redraw = Clock.create_trigger(self._on_redraw_lines)

    @property
    def grid_handler(self):
        return self._grid_controller

    def load_new_grid(self, file_path):
        if not self._grid is None:
            self.unbind(size=self.trigger_resize)

        self._clear_old_grid()
        self._grid_controller.load_grid(file_path)
        self._draw_grid_points()
        #add draw instruction once widgets initialised.
        self._grid[0][0].bind(pos=self.trigger_init_point)

    def _on_init_point(self, *args):
        self._grid[0][0].unbind(pos=self.trigger_init_point)
        self._draw_grid_lines()
        self.bind(size=self.trigger_resize)

    def _on_resize(self, *args):
        print "ping <====================================="
        # LEAVE THIS PRINT STATEMENT IT FIXES A WEIRD BUG.
        # and so my descent into madness continues
        self._draw_grid_points()
        self._grid[0][0].bind(pos=self.trigger_redraw)

    def _on_redraw_lines(self, *args):
        self._grid[0][0].unbind(pos=self.trigger_redraw)
        self._redraw_lines()

    def _clear_old_grid(self):
        self._grid = None
        self._lines = None
        self.canvas.clear()
        self.clear_widgets()

    def _draw_grid_points(self):
        grid = self._grid_controller.grid

        is_building = self._grid is None

#        if is_building:
        x_hint_height = 2.0 * ((1.0 / float(grid.n_rows)) / tan(pi/3.0))
        x_hint_width = 1.0 / (float(grid.n_columns) + 0.5)
        x_hint = min(x_hint_height, x_hint_width)
        y_hint = (x_hint / 2.0) * tan(pi/3.0)

        # THIS LINE FUCKS THINGS UP, LEAVE IT COMMENTED IF YOU VALUE YOUR SANITY.
        self.size_hint = (x_hint * (float(grid.n_columns) + 0.5), y_hint * float(grid.n_rows))
        self.pos_hint = {'x': .5 * (1.0 - self.size_hint[0]),
                         'top': 1.0 - (.5 * (1.0 - self.size_hint[1]))}

        size_x = self.size_hint[0] / float(grid.n_columns + 0.5) * 0.4
        size_y = self.size_hint[1] / float(grid.n_rows) * 0.4

        x_dist = .92 / (float(grid.n_columns-1) + 0.5)
        y_dist = .92 / float(grid.n_rows-1)

        if is_building:
            print "ping"
            self._grid = list(list(None for i in range(grid.n_columns)) for j in range(grid.n_rows))

            def flyfly_the_great_def(x, y, x_hint, y_hint):
                point = grid.get_point(x=x, y=y)
                if point is None:
                    colour = "None"
                    shape = "None"
                else:
                    colour = point.color
                    shape = point.shape

                new_grid_point = GridPoint(coord=(x, y), shape=shape, colour=colour)
                new_grid_point.pos_hint = {'x': x_hint,
                                           'top': y_hint}
                new_grid_point.size_hint_x = size_x
                new_grid_point.size_hint_y = size_y

                self.add_widget(new_grid_point)
                self._grid[y][x] = new_grid_point

        else:
            def flyfly_the_great_def(x, y, pos_hint_x, pos_hint_y):
                point = self._grid[y][x]
                point.pos_hint = {'x': pos_hint_x, 'top': pos_hint_y}
                point.size_hint_x = size_x
                point.size_hint_y = size_y

        #build create actual points on the grid.
        y_pos_hint = 1.0
        for i in range(grid.n_rows):
            x_pos_hint = - .5 * size_x + .04

            #FIXME I changed this because of fucky behaviour
            if i % 2 == 1:
                x_pos_hint += 0.5 * x_dist

            for j in range(grid.n_columns):
                flyfly_the_great_def(j, i, x_pos_hint, y_pos_hint)

                x_pos_hint += x_dist
            y_pos_hint -= y_dist

    def _draw_grid_lines(self):
        n_rows = self._grid_controller.grid.n_rows
        n_cols = self._grid_controller.grid.n_columns

        self._lines = []

        #FIXME I changed this because of fucky behaviour
        is_flushed_left = True
        for i in range(n_rows):
            for j in range(n_cols):
                cur_point = self._grid[i][j]

                #horizontal line
                if j > 0:
                    other_point = self._grid[i][j-1]
                    self._draw_line_between(cur_point, other_point)

                #vertical lines
                if i > 0:
                    next_points = [self._grid[i-1][j]]
                    if is_flushed_left and j > 0:
                        next_points.append(self._grid[i-1][j-1])
                    if (not is_flushed_left) and j < (n_cols-1):
                        next_points.append(self._grid[i-1][j+1])

                    for other_point in next_points:
                        self._draw_line_between(cur_point, other_point)

            is_flushed_left = not is_flushed_left

    def _draw_line_between(self, this_point, other_point):
        if this_point.shape == "None" or other_point.shape == "None":
            line = self._draw_line(this_point.center_in_window_coord,
                                   other_point.center_in_window_coord,
                                   col.DARK_GRAY, 1)
        else:
            line = self._draw_line(this_point.center_in_window_coord,
                                   other_point.center_in_window_coord,
                                   col.DARK_BLUE, 1.5)
        self._lines.append((line, this_point, other_point))

    def _draw_line(self, pos_a, pos_b, colour, width):
        with self.canvas.before:
            Color(colour[0], colour[1], colour[2])
            line = Line(points=[pos_a[0], pos_a[1], pos_b[0], pos_b[1]], width=width)
        return line

    def _redraw_lines(self, *args):
        for (line, this_point, other_point) in self._lines:
            this_x, this_y = this_point.center_in_window_coord
            other_x, other_y = other_point.center_in_window_coord
            line.points = [this_x, this_y, other_x, other_y]

    def get_bounds(self):
        x_left_bound, y_top_bound = self._grid[0][0].center_in_window_coord
        print "-------\nlength: " + str(len(self._grid))
        #if len(self._grid) > 1:
        #    x_right_bound = self._grid[1][-1].center_in_window_coord[0]
        #else:
        #    x_right_bound = self._grid[0][-1].center_in_window_coord[0]
        x_right_bound = self._grid[1][-1].center_in_window_coord[0]


        y_bottom_bound = self._grid[-1][0].center_in_window_coord[1]

        return x_left_bound, x_right_bound, y_bottom_bound, y_top_bound

class GridPoint(Widget):
    side_size = NumericProperty(0)

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

    def on_size(self, *args):
        self.side_size = min(self.size)

#
#from kivy.app import App
#from kivy.uix.floatlayout import FloatLayout


#class GridViewApp(App):
#    def build(self):
#        interface = FloatLayout()
#        herpyderpelderpderp = GridView()
#        interface.add_widget(herpyderpelderpderp)
#        #
#        #interface = RelativeLayout()
#        #new_point = GridPoint(coord=(0, 0), shape="Heart", colour="Red")
#        #new_point.pos_hint = {'x': 0.5,
#        #                      'top': 0.8}
#        #new_point.size_hint_y = 0.1
#        #new_point.size_hint_x = 0.1
#        #interface.add_widget(new_point)
#        #
#        #other_new_point = GridPoint(coord=(0, 0), shape="Star", colour="Blue")
#        #other_new_point.pos_hint = {'x': 0.2,
#        #                      'top': 0.4}
#        #other_new_point.size_hint_y = 0.1
#        #other_new_point.size_hint_x = 0.1
#        #interface.add_widget(other_new_point)
#        herpyderpelderpderp.load_new_grid('./grid.csv')
#
#        return interface