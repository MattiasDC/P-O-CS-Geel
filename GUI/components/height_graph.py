from kivy.app import App

from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, StringProperty
from kivy.uix.label import Label

from kivy.uix.widget import Widget

from graph import Graph, MeshLinePlot
from math import radians
from math import log10, sin
from kivy.graphics.transformation import Matrix

from util.values import HEIGHT_MAX

from kivy.factory import Factory
from kivy.lang import Builder
import os


class HeightGraphWidget(Widget):
    """
    The HeightGraphWidget is the container for the HeightGraph, it provides
    the methods for interacting, with the height graph.
    """
    #-------------------------------------------------------------------------
    # Update Method
    #-------------------------------------------------------------------------
    def update(self, dt):
        """
        Update function, called each time interval.
        """
        self._height_graph.update(dt)

    #-------------------------------------------------------------------------
    # Internal Widgets
    #-------------------------------------------------------------------------
    _height_graph = ObjectProperty(None)
    """ The actual HeightGraph displayed in this HeightGraphWidget. """
    _timer = ObjectProperty(None)
    """ The timer that shows the time passed since start up. """

    #-------------------------------------------------------------------------
    # Interaction Methods
    #-------------------------------------------------------------------------
    def add_current_height_value(self, time=None, height=None):
        """
        see: HeightPlot add_value documentation.
        """
        self._height_graph.current_height_plot.add_value(time=time, height=height)

    def add_goal_height_value(self, time=None, height=None):
        """
        see: HeightPlot add_value documentation.
        """
        self._height_graph.goal_height_plot.add_value(time=time, height=height)

    #-------------------------------------------------------------------------
    # Layout Properties and Methods
    #-------------------------------------------------------------------------
    time_span = NumericProperty(120.0)
    """ The amount of time in seconds that is displayed on the x-axis. """
    max_height = NumericProperty(HEIGHT_MAX)
    """ The maximum height in cm that is displayed on the y-axis. """

    #-------------------------------------------------------------------------
    # Ticks
    x_ticks_major = NumericProperty(20.0)
    """ Distance between major ticks on the X-axis of this HeightGraphWidget. """

    x_n_ticks = NumericProperty(0)
    """ Number of ticks on the x-axis of this HeightGraph. """

    def on_x_n_ticks(self, instance, value):
        self.x_ticks_major = float(self.time_span) / float(value - 1)

    #-------------------------------------------------------------------------
    y_ticks_major = NumericProperty(20.0)
    """ Distance between major ticks on the Y-axis of this HeightGraphWidget. """

    y_n_ticks = NumericProperty(0)
    """ Number of ticks on the y-axis of this HeightGraph. """

    def on_y_n_ticks(self, instance, value):
        self.y_ticks_major = float(self.max_height) / float(value - 1)

    #-------------------------------------------------------------------------
    # Layout options.
    font_size = NumericProperty('15sp')
    """ Font size of the labels of this HeightGraphWidget. """

    goal_height_colour = ListProperty((0.2, 0.2, 1, 1))
    """ Colour of the goal height line in this HeightGraph. """
    current_height_colour = ListProperty((0.2, 1, 0.2, 1))
    """ Colour of the current height line in this HeightGraph. """


class HeightGraph(Graph):
    """
    The HeightGraph Widget provides a Graph with two dynamic plots that
    show the goal and current height of the Balloon.
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, **kwargs):
        super(HeightGraph, self).__init__(**kwargs)
        self.xmin = -self.time_span
        self.xmax = 0

        #Goal Height plot.
        self.goal_height_plot = HeightPlot(color=self.goal_height_colour)
        self.add_plot(self.goal_height_plot)

        #Current Height plot.
        self.current_height_plot = HeightPlot(color=self.current_height_colour)
        self.add_plot(self.current_height_plot)

    #-------------------------------------------------------------------------
    # Update Method
    #-------------------------------------------------------------------------
    def update(self, dt):
        self.xmin += dt
        self.xmax = self.xmin + self.time_span

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    time_span = NumericProperty(120.0)
    goal_height_colour = ListProperty((0.2, 0.2, 1, 1))
    current_height_colour = ListProperty((0.2, 1, 0.2, 1))

    #-------------------------------------------------------------------------
    # Internal Overridden functions
    #-------------------------------------------------------------------------
    def _update_labels(self):
        #IMPORTANT
        #---------------------------------------------------------------------
        # This particular function is not written by me, but obtained
        # from the superclass of heightwidget, it is overridden to modify the
        # x_major_points labels.
        #---------------------------------------------------------------------

        xlabel = self._xlabel
        ylabel = self._ylabel
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        padding = self.padding
        x_next = padding + x
        y_next = padding + y
        xextent = x + width
        yextent = y + height
        ymin = self.ymin
        ymax = self.ymax
        xmin = self.xmin
        precision = self.precision
        x_overlap = False
        y_overlap = False
        # set up x and y axis labels
        if xlabel:
            xlabel.text = self.xlabel
            xlabel.texture_update()
            xlabel.size = xlabel.texture_size
            xlabel.pos = (x + width / 2. - xlabel.width / 2., padding + y)
            y_next += padding + xlabel.height
        if ylabel:
            ylabel.text = self.ylabel
            ylabel.texture_update()
            ylabel.size = ylabel.texture_size
            ylabel.x = padding + x - (ylabel.width / 2. - ylabel.height / 2.)
            x_next += padding + ylabel.height
        xpoints = self._ticks_majorx
        #print len(xpoints)
        xpoints_name = list(-self.time_span + i * self.x_ticks_major for i in xrange(int(self.time_span / self.x_ticks_major) + 1))

        xlabels = self._x_grid_label
        xlabel_grid = self.x_grid_label
        ylabel_grid = self.y_grid_label
        ypoints = self._ticks_majory
        ylabels = self._y_grid_label
        # now x and y tick mark labels
        if len(ylabels) and ylabel_grid:
            # horizontal size of the largest tick label, to have enough room
            ylabels[0].text = precision % ypoints[0]
            ylabels[0].texture_update()
            y1 = ylabels[0].texture_size
            y_start = y_next + (padding + y1[1] if len(xlabels) and xlabel_grid
                                else 0) +\
                                (padding + y1[1] if not y_next else 0)
            yextent = y + height - padding - y1[1] / 2.
            if self.ylog:
                ymax = log10(ymax)
                ymin = log10(ymin)
            ratio = (yextent - y_start) / float(ymax - ymin)
            y_start -= y1[1] / 2.
            func = (lambda x: 10 ** x) if self.ylog else lambda x: x
            y1 = y1[0]
            for k in xrange(len(ylabels)):
                ylabels[k].text = precision % func(ypoints[k])
                ylabels[k].texture_update()
                ylabels[k].size = ylabels[k].texture_size
                y1 = max(y1, ylabels[k].texture_size[0])
                ylabels[k].pos = (x_next, y_start + (ypoints[k] - ymin) *
                                  ratio)
            if len(ylabels) > 1 and ylabels[0].top > ylabels[1].y:
                y_overlap = True
            else:
                x_next += y1 + padding

        if len(xlabels) and xlabel_grid:
            func = log10 if self.xlog else lambda x: x
            # find the distance from the end that'll fit the last tick label
            xlabels[0].text = precision % func(xpoints_name[-1])
            xlabels[0].texture_update()
            xextent = x + width - xlabels[0].texture_size[0] / 2. - padding
            # find the distance from the start that'll fit the first tick label
            if not x_next:
                xlabels[0].text = precision % func(xpoints_name[0])
                xlabels[0].texture_update()
                x_next = padding + xlabels[0].texture_size[0] / 2.
            xmin = func(xmin)
            ratio = (xextent - x_next) / float(func(self.xmax) - xmin)
            func = (lambda x: 10 ** x) if self.xlog else lambda x: x
            right = -1
            for k in xrange(len(xlabels)):
                xlabels[k].text = precision % func(xpoints_name[k])
                # update the size so we can center the labels on ticks
                xlabels[k].texture_update()
                xlabels[k].size = xlabels[k].texture_size
                xlabels[k].pos = (x_next + (xpoints[k] - xmin) * ratio -
                                  xlabels[k].texture_size[0] / 2., y_next)
                if xlabels[k].x < right:
                    x_overlap = True
                    break
                right = xlabels[k].right
            if not x_overlap:
                y_next += padding + xlabels[0].texture_size[1]
        # now re-center the x and y axis labels
        if xlabel:
            xlabel.x = x_next + (xextent - x_next) / 2. - xlabel.width / 2.
        if ylabel:
            ylabel.y = y_next + (yextent - y_next) / 2. - ylabel.height / 2.
            t = Matrix().translate(ylabel.center[0], ylabel.center[1], 0)
            t = t.multiply(Matrix().rotate(-radians(270), 0, 0, 1))
            ylabel.transform = t.multiply(Matrix().translate(-ylabel.center[0],
                                                             -ylabel.center[1],
                                                             0))
        if x_overlap:
            for k in xrange(len(xlabels)):
                xlabels[k].text = ''
        if y_overlap:
            for k in xrange(len(ylabels)):
                ylabels[k].text = ''
        return x_next, y_next, xextent, yextent


class HeightPlot(MeshLinePlot):
    """
    The height plot provides the methods add_value and remove_points_until
    to add and remove points from the plot.
    """
    def add_value(self, time=None, height=None):
        """
        Add the point (time, height) to the point list of this HeightPlot
        If no time is specified, boot time of the app is used.

        Parameters
        ----------
        time : Double
            time of the point
        height : Double
            height of the point

        Post-conditions
        ---------------
        * (new self).points[-1] == (time, height)
        """
        if not height is None:
            if time is None:
                time = Clock.get_boottime()
            self.points.append((time, height))

    def remove_points_until(self, time):
        """
        Remove the points until the specified time.
        Used to clear the points that are no longer visible.

        Parameters
        ----------
        time : double
            Time to be used to clean the points of this Heightplot

        Post-conditions
        ---------------
        * \forall point \in self.points \\ self.points[0] point[0] > time
        """
        while len(self.points) > 2:
            if self.points[1][0] < time:
                self.points.pop(0)
            else:
                break

#===============================================================================
# Updates for loading the file
#===============================================================================
Factory.register('HeightGraphWidget', cls=HeightGraphWidget)
Builder.load_file(os.path.dirname(os.path.realpath(__file__)) + '\heightgraph.kv')