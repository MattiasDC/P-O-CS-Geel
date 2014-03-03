from kivy.properties import NumericProperty, ObjectProperty, BoundedNumericProperty, OptionProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

from uix.common import BaseContainerGUI


class BalloonProperties(BaseContainerGUI):
    """
    The Data Manager.
    """
    def _update_active(self, dt):
        """
        Request all information from the balloon through the network_interface.

        Parameters
        ----------
        dt : Double
            Time passed since last update.

        Pre-conditions
        --------------
        * NetworkManager().has_connection
        """
        network_interface = self._network_manager

        # Update height.
        self.goal_height = network_interface.get_goal_height()
        self.current_height = network_interface.get_current_height()

        self._height_graph.add_goal_height_value(height=self.goal_height)
        self._height_graph.add_current_height_value(height=self.current_height)

        self._height_graph.update(dt)

        # Update motors
        self.motor_z = network_interface.get_motor_z_pwm()

        new_motor_xy = network_interface.get_motors_xy_status()
        if new_motor_xy is not None:
            self.motor_xy = new_motor_xy

        # Update propellers
        self.propeller_right = network_interface.get_propeller_right_status()
        self.propeller_left = network_interface.get_propeller_left_status()

    #-------------------------------------------------------------------------
    # Height
    current_height = NumericProperty(0)
    """ The current height of the connected Zeppelin in the GUI in cm. """

    goal_height = NumericProperty(0)
    """ The goal height of the connected Zeppelin in the GUI in cm. """

    _height_graph = ObjectProperty(None)
    """ Graph of the goal and current height values."""

    #-------------------------------------------------------------------------
    # Motors
    motor_z = BoundedNumericProperty(0, min=-100, max=100)
    """ The pwm of the z-axis motor in percentages. """

    motor_xy = OptionProperty("Not moving", options=["Not moving", "Forward", "Backward",
                                                     "Turning left", "Turning right"])
    """ The direction the motor is causing the zeppelin to turn. """

    #-------------------------------------------------------------------------
    # Propellers
    propeller_left = OptionProperty("Not moving", options=["Not moving", "Forward", "Backward"])
    """ The status of the left propeller. """

    propeller_right = OptionProperty("Not moving", options=["Not moving", "Forward", "Backward"])
    """ The status of the right propeller. """

    #-------------------------------------------------------------------------
    # Position
    position =


class PropertiesHeader(GridLayout):
    """
    PropertiesHeader specifies a common set of properties that relate to
    the same concept, i.e. height, motors etc. It specifies the styling and
    provides the attributes to do this.
    """
    source_icon = StringProperty(None)
    """ The source of the icon that is used in this PropertiesHeader. """
    property_name = StringProperty('None')
    """ The name of this PropertiesHeader. """


class PropertyEntryDouble(GridLayout):
    """
    PropertyEntry specifies the variables and styling of a single entry of
    a property in the gui that uses a double as value.

    It specifies a name, unit and value for this property.
    """
    name = StringProperty('None')
    """ The name of this PropertyEntryDouble. """
    unit = StringProperty('None')
    """ The unit of this PropertyEntryDouble. """
    value = NumericProperty(0)
    """ The value of this PropertyEntryDouble. """


class PropertyEntryString(GridLayout):
    """
    PropertyEntryString specifies the variables and styling of a single entry of
    a property in the gui that has a string as value.

    It specifies a name, value for this property.
    """
    name = StringProperty('None')
    """ The name of this PropertyEntryString. """
    value = StringProperty('')
    """ The value of this PropertyEntryString. """

