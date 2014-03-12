from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput

from domain.network import NetworkManager


class Buttons(FloatLayout):
    goal_loc_x = NumericProperty(0)
    goal_loc_y = NumericProperty(0)

    goal_height = NumericProperty(50)


    def __init__(self, **kwargs):
        super(Buttons, self).__init__(**kwargs)

        self._network_manager = NetworkManager()

    def send_location(self, *args):
        print (self.goal_loc_x, self.goal_loc_y)
        #self._network_manager.send_goal_pos((self.goal_loc_x, self.goal_loc_y))

    def send_height(self, *args):
        print self.goal_height
        #self._network_manager.send_goal_height(self.goal_height)

    def _on_height_input(self, instance, value):
        try:
            value = float(value)
            if value > 500.0:
                value = 500.0
                instance.text = str(value)
                self.goal_height = value
        except (ValueError, TypeError) as e:
            instance.text = str(self.goal_height)

    def _on_x_input(self, instance, value):
        try:
            self.goal_loc_x = float(value)
        except (ValueError, TypeError) as e:
            instance.text = str(self.goal_height)

    def _on_y_input(self, instance, value):
        try:
            self.goal_loc_y = float(value)
        except (ValueError, TypeError) as e:
            instance.text = str(self.goal_height)


class NumberTextInput(TextInput):
    """
    HeightTextInput provides a textfield for the HeightControl widget.
    This field only allows the digits and '.' to be entered.
    """
    def __init__(self, **kwargs):
        super(NumberTextInput, self).__init__(**kwargs)
        self.bind(on_text_validate=self.on_enter)

    def insert_text(self, substring, from_undo=False):
        """
        See: TextInput.insert_text
        Modified to only allow numerical values.
        """
        if substring.isdigit() or substring == '':
            super(NumberTextInput, self).insert_text(substring, from_undo)

    def on_enter(self, instance):
        """
        Callback when pressed enter, defocus this widget.
        """
        self.focus = False
