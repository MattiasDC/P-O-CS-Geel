from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty, ListProperty

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder

from domain.zeppelin import ZeppelinHandler
from uix.properties_view import ZeppelinProperties


class FloatingDutchManGUI(FloatLayout):
    """ The actual GUI class that draws the complete application. """
    #--------------------------------------------------------------------------
    # Components of the GUI
    #--------------------------------------------------------------------------
    prop_view = ObjectProperty(None)
    """ The properties widget. """
    zeppelin_graph = ObjectProperty(None)
    """ The graph displaying the heights of the zeppelins. """
    zeppelin_manager = ObjectProperty(None)
    """ The zeppelin manager widget. """
    grid_view = ObjectProperty(None)
    """ The context view widget. """
    console = ObjectProperty(None)
    """ The console widget. """
    network_view = ObjectProperty(None)
    """ The network view widget."""

    def on_zeppelin_manager(self, *args):
        self.zeppelin_manager.set_zeppelin_handler(self)

    #--------------------------------------------------------------------------
    # Properties and methods related to the window and application size
    #--------------------------------------------------------------------------
    #The size of the window
    window_width = NumericProperty(Window.width)
    """ The current width of the window of this ZeppelinInterfaceRoot. """
    window_height = NumericProperty(Window.height)
    """ The current height of the window of this ZeppelinInterfaceRoot. """
    #Do not ask me where these values come from, but they seem to work.
    window_center = ListProperty([50, 50])
    """ The current centre of the window of this ZeppelinInterfaceRoot. """

    #The size the application will use.
    application_width = NumericProperty(800.0)
    """ The width of the actual application within the window of this ZeppelinInterfaceRoot. """
    application_height = NumericProperty(450.0)
    """ The height of the actual application within the window of this ZeppelinInterfaceRoot. """
    application_pos_x = NumericProperty(0)
    """ The x-axis position of the actual application within the window of this ZeppelinInterfaceRoot. """
    application_pos_y = NumericProperty(150)
    """ The y-axis position of the actual application within the window of this ZeppelinInterfaceRoot. """

    WIDTH_RATIO = 1920.0 / 1080.0
    """ The ratio used for the actual application. """

    #--------------------------------------------------------------------------
    # Properties and methods related to the window and application size
    #--------------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        Initialize a new ZeppelinInterfaceRoot widget.
        """
        super(FloatingDutchManGUI, self).__init__(**kwargs)
        #bind Window resize function
        #Window.bind(on_resize=self._on_resize)
        self.zeppelin_handler = ZeppelinHandler()
        self.zeppelins = []

    def update(self, dt):
        """
        Update all relevant child widgets.

        Parameters
        ----------
        dt : double
            Time since last update in seconds.

        effects
        -------
        * self.balloon_properties.update(dt)
        * self.console.update(dt)
        """
        self.zeppelin_handler.update_zeppelins(dt)
        self.prop_view.update(dt)
        self.grid_view.update(dt)
        self.console.update(dt)



    #--------------------------------------------------------------------------
    # Resize information
    #def _on_resize(self, inst, width, height):
    #    """
    #    updates variables when the window is resized.
    #
    #    param
    #    -----
    #    inst : WindowPygame
    #        instance of the WindowPygame.
    #    width: int
    #        Current width of the window of this app.
    #    height: int
    #        Current height of the window of this app.
    #
    #    Pre-conditions
    #    --------------
    #    * window is resized
    #
    #    Post-conditions
    #    ---------------
    #    * (new self).window_width = width
    #    * (new self).window_height = height
    #    * (new self).window_center = inst.center
    #    * | IF width / height > WIDTH_RATIO -> (new self).application_height = width / WIDTH_RATIO
    #      |                                    (new self).application_width = width
    #    * | ELSE (new self).application_height = height
    #      |      (new self).application_width = height * WIDTH_RATIO
    #    """
    #    #set the new dimensions of the window.
    #    self.window_width = width
    #    self.window_height = height
    #    self.window_center = inst.center
    #
    #    #calculate and set new dimensions of the application window.
    #    if float(width) / float(height) < self.WIDTH_RATIO:
    #        self.application_width = width
    #        self.application_height = width / self.WIDTH_RATIO
    #
    #        self.application_pos_x = 0
    #        self.application_pos_y = height - self.application_height
    #    else:
    #        self.application_width = height * self.WIDTH_RATIO
    #        self.application_height = height
    #
    #        self.application_pos_x = 0.5 * (width - self.application_width)
    #        self.application_pos_y = 0
    #
    #    if not self.grid_view is None:
    #        self.grid_view.redraw

    #--------------------------------------------------------------------------
    # initialization
    def on_grid_view(self, *args):
        self.grid_view.view.load_new_grid('./grid.csv')

    def add_zeppelin(self, name):
        self.zeppelin_handler.add_new_zeppelin(name)

        zep = self.zeppelin_handler.get_zeppelin(name)

        self.prop_view.add_zeppelin(zep)
        self.grid_view.add_zeppelin(zep)


class Test(FloatLayout):
    pass


class FloatingDutchManApp(App):
    def build(self):
        Builder.load_file('./uix/FloatingDutchManApp.kv')
        Builder.load_file('./uix/grid_view.kv')
        Builder.load_file('./uix/zeppelin_handler.kv')
        Builder.load_file('./uix/console_view.kv')

        #interface = FloatingDutchManGUI()
        #print "x: " + str(interface.application_pos_x)
        #print "y: " + str(interface.application_pos_y)
        interface = FloatingDutchManGUI()
        Clock.schedule_interval(interface.update, 0.5)

        return interface

