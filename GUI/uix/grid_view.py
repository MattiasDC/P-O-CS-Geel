from math import pi, sin
from kivy.uix.scatter import Scatter

from util import colour as col
from util import values as val

from kivy.graphics import *
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import OptionProperty, NumericProperty, ListProperty, ObjectProperty, StringProperty

from kivy.clock import Clock


class GridObject(Scatter):
    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    grid = ObjectProperty(None)
    """ The internal grid object that this zeppelin is displayed on. """

    img = ObjectProperty(None)
    """ The image that represents this GridObject on the GridView. """
    img_path = StringProperty("")
    """ The path to the image that represents this GridObject. """
    location_local = (0, 0)
    """ The local location of this GridObject on the grid. """

    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        Create a new instance of this GridObject.
        """
        super(GridObject, self).__init__(**kwargs)

        self.trigger_resize = Clock.create_trigger(self.calculate_bounds, 0)
        self.trigger_reposition = Clock.create_trigger(self.calculate_bounds, 0)

    #-------------------------------------------------------------------------
    # Callback methods.
    #-------------------------------------------------------------------------
    def on_grid(self, instance, value):
        """
         Reposition this ZeppelinScatter on the grid when the window resizes.
        """
        self.grid.bind(size=self.trigger_resize)
        self.grid.bind(pos=self.trigger_reposition)

    def calculate_bounds(self, *args):
        (x_l, x_r, y_b, y_t) = self.grid.get_bounds()
        self.pos = [x_l - 0.5 * self.size[0], y_t - 0.5 * self.size[1]]

    #-------------------------------------------------------------------------
    # Update methods.
    #-------------------------------------------------------------------------
    def _get_position(self):
        return NotImplemented

    def update(self, dt):
        """
        Update the position and rotation ofthis zeppelinScatter.

        Parameters
        ----------
        dt : int
            The time that has passed since the last update.
        """
        x_l, x_r, y_b, y_t = self.grid.get_bounds()

        loc_x, loc_y = self._get_position()
        grid = self.grid.grid

        # There are n-1 + 0.5 steps of 400 mm to get the size of grid.
        location_local_x = float(loc_x) / (float(400 * (grid.n_columns - 0.5)))
        # we take the sin of 1/3 pi because the edge of 400 mm has a hook of
        location_local_y = float(loc_y) / (sin((1.0/3.0) * pi) * float(400 * (grid.n_rows - 1)))
        self.location_local = (location_local_x, location_local_y)

        width = x_r - x_l
        height = y_t - y_b
        self.pos = (x_l + width * self.location_local[0] - 0.5 * self.size[0],
                    y_t - height * self.location_local[1] - 0.5 * self.size[1])


class GoalPositionScatter(GridObject):
    team = StringProperty("None")
    """ The team colour of this zeppelin scatter. """

    def __init__(self, **kwargs):
        """
        Create a new instance of this GridObject.
        """
        self.img_path = './img/grid_goal.png'
        super(GoalPositionScatter, self).__init__(**kwargs)

        self._zeppelin = kwargs['zeppelin']
        self.team = self._zeppelin.identifier

    def on_team(self, instance, value):
        """
        Change the colour to the team colour when the team is set.
        """
        self.img.color = col.COLOUR_MAP_ZEP[value]

    def _get_position(self):
        return self._zeppelin.goal_position

    def update(self, dt):
        super(GoalPositionScatter, self).update(dt)
        self.pos[1] += 0.5 * self.width


class EnemyZeppelinScatter(GridObject):
    team = StringProperty("None")
    """ The team colour of this zeppelin scatter. """

    def __init__(self, **kwargs):
        """
        Create a new instance of this GridObject.
        """
        self.img_path = './img/grid_enemy.png'
        super(EnemyZeppelinScatter, self).__init__(**kwargs)

        self._zeppelin = kwargs['zeppelin']
        self.team = self._zeppelin.identifier

    def on_team(self, instance, value):
        """
        Change the colour to the team colour when the team is set.
        """
        self.img.color = col.COLOUR_MAP_ZEP[value]

    def _get_position(self):
        return self._zeppelin.position


class OurZeppelinScatter(GridObject):
    team = StringProperty("None")
    """ The team colour of this zeppelin scatter. """

    direction = NumericProperty(0)
    """ The direction of this zeppelin. """

    def __init__(self, **kwargs):
        """
        Create a new instance of this GridObject.
        """
        self.img_path = './img/grid_zeppelin.png'
        super(OurZeppelinScatter, self).__init__(**kwargs)

        self._zeppelin = kwargs['zeppelin']
        self.team = self._zeppelin.identifier

    def on_team(self, instance, value):
        """
        Change the colour to the team colour when the team is set.
        """
        self.img.color = col.COLOUR_MAP_ZEP[value]

    def _get_position(self):
        return self._zeppelin.position

    def _get_direction(self):
        return self._zeppelin.direction

    def update(self, dt):
        super(OurZeppelinScatter, self).update(dt)
        self.direction = self._get_direction()


#=============================================================================
# Grid Container
#=============================================================================
class GridViewContainer(FloatLayout):
    """
    The GridViewContainer manages everything related to the Grid in the gui.
    It contains a single GridView as well as all zeppelins currently displayed
    on the grid.
    """
    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    grid_handler = ObjectProperty(None)
    """ The grid handler of this GridViewContainer. """
    grid_view = ObjectProperty(None)
    """ The object that draws the grid. """

    the_root = ObjectProperty(None)
    """ The root of this interface. """

    zeppelin_scatters = ListProperty([])
    """ A list of the zeppelin scatters on this grid. """

    #-------------------------------------------------------------------------
    # Grid methods
    #-------------------------------------------------------------------------
    def load_grid(self, path_to_file):
        """
        Load a new grid from the specified csv file.

        Parameters
        ----------
        path_to_file : String
            The path (with the file name) to the grid csv file.

        Post-conditions
        ---------------
        * New grid is loaded and displayed.
        """
        self.grid_handler.load_grid(path_to_file)
        self.grid_view.load_new_grid(self.grid_handler.grid)

    #-------------------------------------------------------------------------
    # Zeppelin methods
    #-------------------------------------------------------------------------
    def add_zeppelin(self, zeppelin):
        """
        Add and display the specified zeppelin to the grid.

        Paramaters
        ----------
        zeppelin : ZeppelinView
            The new zeppelin that is added to this GridView
        """
        if zeppelin.identifier == val.OUR_TEAM:
            new_zep_scatter = OurZeppelinScatter(zeppelin=zeppelin)
            new_zep_scatter.grid = self.grid_view

            new_goal_scatter = GoalPositionScatter(zeppelin=zeppelin)
            new_goal_scatter.grid = self.grid_view

            self.zeppelin_scatters.append(new_zep_scatter)
            self.zeppelin_scatters.append(new_goal_scatter)
        else:
            new_scatter = EnemyZeppelinScatter(zeppelin=zeppelin)
            new_scatter.grid = self.grid_view

            self.zeppelin_scatters.append(new_scatter)
            self.add_widget(new_scatter)

    def update(self, dt):
        """
        Update this GridViewContainer by updating all of the zeppelins
        that are placed in it.

        Parameters
        ----------
        dt : int
            the time that has passed since the last update.
        """
        for w in self.zeppelin_scatters:
            w.update(dt)

    def on_grid_handler(self, instance, value):
        new_grid_view = GridView()

        self.add_widget(new_grid_view)
        self.grid_view = new_grid_view

        self.grid_view.load_new_grid(value.grid)

    #-------------------------------------------------------------------------
    grid_load_button = ObjectProperty(None)
    """ The grid load button in this GridViewContainer."""

    def on_grid_load_button(self, _, value):
        value.bind(current_csv_path=self.on_load)

    def on_load(self, _, value):
        self.load_grid(value)


class GridView(FloatLayout):
    """
    The class that draws the actual grid in the GUI.
    Provides method to load and draw a new grid, and resize everything when
    the window is updated.
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, **kwargs):
        super(GridView, self).__init__(**kwargs)

        self._grid = None

        # Widgets
        self._grid_widgets = None
        self._lines = None

        self.trigger_init_point = Clock.create_trigger(self._on_init_point)
        self.trigger_resize = Clock.create_trigger(self._on_resize)
        self.trigger_redraw = Clock.create_trigger(self._on_redraw_lines)

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    @property
    def grid(self):
        """
        The grid of that is currently displayed in this GridView.
        """
        return self._grid

    #-------------------------------------------------------------------------
    # Grid loading
    #-------------------------------------------------------------------------
    def load_new_grid(self, grid):
        """
        Load the specified grid into this GridView.

        Paramaters
        ----------
        grid : Grid
            The new grid to be loaded.
        """
        self._clear_old_grid()

        self._set_grid(grid)

        self._draw_grid_points()
        #add draw instruction once widgets initialised.
        self._grid_widgets[0][0].bind(pos=self.trigger_init_point)

    def _set_grid(self, grid):
        """
        Set the current grid of this GridView to specified grid.

        Parameters
        ----------
        grid : Grid
            The new grid of this GridView.

        Post-conditions
        * | (new self).grid == grid
        """
        self._grid = grid

    #-------------------------------------------------------------------------
    # Trigger methods.
    #-------------------------------------------------------------------------
    def _on_init_point(self, *args):
        self._grid_widgets[0][0].unbind(pos=self.trigger_init_point)
        self._draw_grid_lines()
        self.bind(size=self.trigger_resize)

    def _on_resize(self, *args):
        self._draw_grid_points()
        self._grid_widgets[0][0].bind(pos=self.trigger_redraw)

    def _on_redraw_lines(self, *args):
        self._grid_widgets[0][0].unbind(pos=self.trigger_redraw)
        self._redraw_lines()

    def _clear_old_grid(self):
        if not self._grid_widgets is None:
            self.unbind(size=self.trigger_resize)

        self.clear_widgets()
        self._grid_widgets = None

        self.canvas.before.clear()
        self._lines = None
        self._grid = None

    #-------------------------------------------------------------------------
    # Drawing methods.
    #-------------------------------------------------------------------------
    def _draw_grid_points(self):
        grid = self.grid
        is_building = self._grid_widgets is None

        #---------------------------------------------------------------------
        # calculate x and y offset.
        x_hint_height = ((1.0 / float(grid.n_rows - 1)) / sin(pi/3.0))
        x_hint_width = 1.0 / (float(grid.n_columns) - 0.5)
        x_hint = min(x_hint_height, x_hint_width)
        y_hint = x_hint * sin(pi/3.0)

        #---------------------------------------------------------------------
        # calculate pos and size hints of this grid widget.
        self.size_hint = (x_hint * (float(grid.n_columns) - 0.5),
                          y_hint * float(grid.n_rows - 1))
        self.pos_hint = {'x': .5 * (1.0 - self.size_hint[0]),
                         'top': 1.0 - (.5 * (1.0 - self.size_hint[1]))}

        #---------------------------------------------------------------------
        # calculate
        size_x = self.size_hint[0] / float(grid.n_columns + 0.5) * 0.4
        size_y = self.size_hint[1] / float(grid.n_rows) * 0.4

        x_dist = .92 / (float(grid.n_columns-1) + 0.5)
        y_dist = .92 / float(grid.n_rows-1)

        #---------------------------------------------------------------------
        # Define action depending on if it's drawing a new grid or not.
        if is_building:
            self._grid_widgets = list(list(None for _ in range(grid.n_columns)) for _ in range(grid.n_rows))

            def update_point(x, y, pos_x_hint, pos_y_hint):
                point = grid.get_point(x=x, y=y)
                if point is None:
                    colour = "None"
                    shape = "None"
                else:
                    colour = point.color
                    shape = point.shape

                new_grid_point = GridPoint(coord=(x, y), shape=shape, colour=colour)
                new_grid_point.pos_hint = {'x': pos_x_hint,
                                           'top': pos_y_hint}
                new_grid_point.size_hint_x = size_x
                new_grid_point.size_hint_y = size_y

                self.add_widget(new_grid_point)
                self._grid_widgets[y][x] = new_grid_point

        else:
            def update_point(x, y, pos_hint_x, pos_hint_y):
                point = self._grid_widgets[y][x]
                point.pos_hint = {'x': pos_hint_x, 'top': pos_hint_y}
                point.size_hint_x = size_x
                point.size_hint_y = size_y

        #---------------------------------------------------------------------
        #build create actual points on the grid.
        y_pos_hint = 1.0
        for i in range(grid.n_rows):
            x_pos_hint = - .5 * size_x + .04

            if i % 2 == 1:
                x_pos_hint += 0.5 * x_dist

            for j in range(grid.n_columns):
                update_point(j, i, x_pos_hint, y_pos_hint)

                x_pos_hint += x_dist
            y_pos_hint -= y_dist

    def _draw_grid_lines(self):
        n_rows = self.grid.n_rows
        n_cols = self.grid.n_columns

        self._lines = []

        is_flushed_left = True
        for i in range(n_rows):
            for j in range(n_cols):
                cur_point = self._grid_widgets[i][j]

                #horizontal line
                if j > 0:
                    other_point = self._grid_widgets[i][j-1]
                    self._draw_line_between(cur_point, other_point)

                #vertical lines
                if i > 0:
                    next_points = [self._grid_widgets[i-1][j]]
                    if is_flushed_left and j > 0:
                        next_points.append(self._grid_widgets[i-1][j-1])
                    if (not is_flushed_left) and j < (n_cols-1):
                        next_points.append(self._grid_widgets[i-1][j+1])

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
        print("This should not print")
        for (line, this_point, other_point) in self._lines:
            this_x, this_y = this_point.center_in_window_coord
            other_x, other_y = other_point.center_in_window_coord
            line.points = [this_x, this_y, other_x, other_y]

    def get_bounds(self):
        x_left_bound, y_top_bound = self._grid_widgets[0][0].center_in_window_coord

        x_right_bound = self._grid_widgets[1][-1].center_in_window_coord[0]
        y_bottom_bound = self._grid_widgets[-1][0].center_in_window_coord[1]

        return x_left_bound, x_right_bound, y_bottom_bound, y_top_bound


class GridPoint(Widget):
    """
    The GridPoint displays a single point of the grid on the ui.

    Invariants
    ----------
    * | coord[0] >= 0
    * | coord[1] >= 0
    """
    side_size = NumericProperty(0)

    def __init__(self, **kwargs):
        super(GridPoint, self).__init__(**kwargs)
        self._coord = kwargs["coord"]
        self.shape = kwargs["shape"]
        self.colour = kwargs["colour"]

    @property
    def coord(self):
        """
        The coordinate of this GridPoint.
        """
        return self._coord

    def click(self):
        """
        Action associated with clicking on this GridPoint.
        """
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
        """
        Get the colour of this GridPoint.

        return : (r, g, b)
        """
        return self._colour_map[self.colour]

    _colour_map = {"White": col.WHITE,
                   "Blue": col.BLUE,
                   "Green": col.GREEN,
                   "Red": col.RED,
                   "Yellow": col.YELLOW,
                   "None": col.GRAY}

    @property
    def center_in_window_coord(self):
        pos = self.to_window(self.pos[0], self.pos[1])
        return pos[0] + 0.5 * self.size[0], pos[1] + 0.5 * self.size[1]

    def on_size(self, *args):
        self.side_size = min(self.size)