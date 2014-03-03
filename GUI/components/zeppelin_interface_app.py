"""
This module provides the ZeppelinInterfaceApp and its directly related child widgets.
The styling can be found in zeppelininterfaceapp.kv

 Author : Martinus Wilhelmus Tegelaers
 Team : Geel
"""

import kivy

kivy.require('1.7.2')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.properties import NumericProperty, ListProperty, ObjectProperty


class ZeppelinInterfaceRoot(Widget):
    """
    The root of the GUI that holds all the references to the individual
    components.
    """

    def __init__(self, **kwargs):
        """
        Initialize a new ZeppelinInterfaceRoot widget.
        """
        super(ZeppelinInterfaceRoot, self).__init__(**kwargs)
        #bind Window resize function
        Window.bind(on_resize=self._on_resize)

    def update(self, dt):
        """
        Update all relevant child widgets.

        Parameters
        ----------
        dt : double
            Time since last update in seconds.
        """
        pass


    #--------------------------------------------------------------------------
    # Components of the GUI
    #--------------------------------------------------------------------------
    balloon_properties = ObjectProperty(None)

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
    # Resize information
    def _on_resize(self, inst, width, height):
        """
        updates variables when the window is resized.

        param
        -----
        inst : WindowPygame
            instance of the WindowPygame.
        width: int
            Current width of the window of this app.
        height: int
            Current height of the window of this app.

        Pre-conditions
        --------------
        * window is resized

        Post-conditions
        ---------------
        * (new self).window_width = width
        * (new self).window_height = height
        * (new self).window_center = inst.center
        * | IF width / height > WIDTH_RATIO -> (new self).application_height = width / WIDTH_RATIO
          |                                    (new self).application_width = width
        * | ELSE (new self).application_height = height
          |      (new self).application_width = height * WIDTH_RATIO
        """
        #set the new dimensions of the window.
        self.window_width = width
        self.window_height = height
        self.window_center = inst.center

        #calculate and set new dimensions of the application window.
        if float(width) / float(height) < self.WIDTH_RATIO:
            self.application_width = width
            self.application_height = width / self.WIDTH_RATIO

            self.application_pos_x = 0
            self.application_pos_y = height - self.application_height
        else:
            self.application_width = height * self.WIDTH_RATIO
            self.application_height = height

            self.application_pos_x = 0.5 * (width - self.application_width)
            self.application_pos_y = 0


class ZeppelinInterfaceApp(App):

    def build(self):
        Window.set_title('Yellow Balloon Bionic Interface')
        Window.set_icon('img\\gui\\icon_big.png')

        interface = ZeppelinInterfaceRoot()
        Clock.schedule_interval(interface.update, 0.5)

        return interface

if __name__ == '__main__':
    ZeppelinInterfaceApp().run()