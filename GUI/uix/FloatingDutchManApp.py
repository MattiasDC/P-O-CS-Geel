from __builtin__ import property
from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty, ListProperty

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder

from domain import InitialisationHandler
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
        self._zeppelin_handler = kwargs['zeppelin_handler']
        self._grid_handler = kwargs['grid_handler']

        super(FloatingDutchManGUI, self).__init__(**kwargs)

        #bind Window resize function
        #Window.bind(on_resize=self._on_resize)

        self.zeppelins = []

    @property
    def zeppelin_handler(self):
        return self._zeppelin_handler

    @property
    def grid_handler(self):
        return self._grid_handler

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

    def add_zeppelin(self, name):
        self.zeppelin_handler.add_new_zeppelin(name)

        zep = self.zeppelin_handler.get_zeppelin(name)

        self.prop_view.add_zeppelin(zep)
        self.grid_view.add_zeppelin(zep)


class FloatingDutchManApp(App):
    def build(self):
        Builder.load_file('./uix/FloatingDutchManApp.kv')
        Builder.load_file('./uix/grid_view.kv')
        Builder.load_file('./uix/zeppelin_handler.kv')
        Builder.load_file('./uix/console_view.kv')
        Builder.load_file('./uix/properties_view.kv')
        Builder.load_file('./uix/load_dialog.kv')

        init_handler = InitialisationHandler()
        interface = FloatingDutchManGUI(grid_handler=init_handler.grid_handler,
                                        zeppelin_handler=init_handler.zeppelin_handler)
        Clock.schedule_interval(interface.update, 0.5)

        return interface

