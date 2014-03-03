from kivy.factory import Factory

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import BooleanProperty, ListProperty

from network import NetworkManager


class BaseContainerGUI(FloatLayout):
    """
    The BaseContainerGUI serves as a base class for all container
    GUI elements. It provides methods to update itself, as well as a
    NetworkManager.
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        Initialize a new BaseContainerGUI.
        """
        super(BaseContainerGUI, self).__init__(**kwargs)
        self._current_update = self._update_passive

        self._network_manager = NetworkManager()
        self._network_manager.bind(has_connection=self._update_connection)

    #-------------------------------------------------------------------------
    # Properties and related methods
    #-------------------------------------------------------------------------
    is_active = BooleanProperty(False)
    """ Status of this view widget. """

    _passive_colour = ListProperty([0, 0, 0, 0.5])
    _active_colour = ListProperty([0, 0, 0, 0.0])
    _current_colour = ListProperty([0, 0, 0, 0.5])

    def on_is_active(self, instance, is_active):
        if is_active:
            self._set_active()
        else:
            self._set_passive()

    def _set_active(self):
        self._current_update = self._update_active
        self._current_colour = self._active_colour

    def _set_passive(self):
        self._current_update = self._update_passive
        self._current_colour = self._passive_colour

    #-------------------------------------------------------------------------
    # update methods
    #-------------------------------------------------------------------------
    def update(self, dt):
        """
        The update method of this BaseWidget
        """
        self._current_update(dt)

    def _update_passive(self, dt):
        pass

    def _update_active(self, dt):
        raise NotImplementedError

    #-------------------------------------------------------------------------
    # Misc methods
    #-------------------------------------------------------------------------
    def _update_connection(self, instance, value):
        """
        Update the activity of this BaseWidget.
        """
        self.is_active = value


class ContextBase(BaseContainerGUI):
    has_view = BooleanProperty(False)
    _modus_boolean = False

    def on_has_view(self, instance, has_view):
        if self.is_active:
            if has_view:
                self._set_active()
                print 'setting auto mode to: ' + str(self._modus_boolean)
                self._network_manager.set_auto_mode(self._modus_boolean)
            else:
                self._set_passive()

    def on_is_active(self, instance, is_active):
        if self.has_view:
            print 'ping'
            if is_active:
                self._set_active()
                print 'setting auto mode to: ' + str(self._modus_boolean)
                self._network_manager.set_auto_mode(self._modus_boolean)
            else:
                self._set_passive()

#====================================================================
# Register Operations
Factory.register('BaseContainerGUI', cls=BaseContainerGUI)
Factory.register('ContextBase', cls=ContextBase)
