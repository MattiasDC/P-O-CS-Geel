from util.colour import *

from kivy.properties import ObjectProperty, StringProperty, OptionProperty
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.button import Button


class ZeppelinManager(StackLayout):
    the_root = ObjectProperty(None)

    grid = ObjectProperty(None)
    zeppelin_properties = ObjectProperty(None)
    add_button = ObjectProperty(None)

    def on_add_button(self, *args):
        self.add_button.manager = self

    def add_zeppelin(self, name):
        self.remove_widget(self.add_button)

        new_zep = ZeppelinButton(name=name, height=self.width)
        self.add_widget(new_zep)
        self.add_widget(self.add_button)

        self.the_root.add_zeppelin(name)


class ZeppelinButton(Widget):
    def __init__(self, **kwargs):
        super(ZeppelinButton, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.colour = kwargs['name']

        self.size_hint = (1, None)
        self.height = kwargs['height']

    name = StringProperty("red")
    colour = OptionProperty("red", options=["yellow",
                                            "red",
                                            "none"])

    _colour_map = {"yellow": YELLOW_ZEPPELIN,
                   "red": RED_ZEPPELIN}

    def click(self, *args):
        print "WHAT?!"


class AddButton(Button):
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(AddButton, self).__init__(**kwargs)

        self.clicked = False
        self.trigger_pop = Clock.create_trigger(self.create_popup)

    def click(self, *args):
        if not self.clicked:
            self.clicked = True
            self.trigger_pop()
        else:
            print "ping"

    def create_popup(self, *args):
        content = AddPopUp(caller=self)
        popup = Popup(title='Add zeppelin',
                      content=content,
                      size_hint=(0.4, 0.2),
                      auto_dismiss=False)

        content.popup = popup

        popup.bind(on_dismiss=content.on_dismiss)

        popup.open()

    def add_new(self, name):
        self.manager.add_zeppelin(name)


class AddPopUp(FloatLayout):
    input_field = ObjectProperty(None)

    def __init__(self, **kwargs):
        print kwargs
        super(AddPopUp, self).__init__(**kwargs)

        self._caller = kwargs['caller']
        self.popup = None
        self.trigger_dismiss = Clock.create_trigger(self.dismiss_popup)

    def on_dismiss(self, *args):
        print("WOOOOOO")
        self._caller.clicked = False

    def on_accept(self, *args):
        print self.input_field.text
        self._caller.add_new(self.input_field.text)
        self.trigger_dismiss()

    def on_cancel(self, *args):
        self.trigger_dismiss()

    def dismiss_popup(self, *args):
        if not self.popup is None:
            self.popup.dismiss()
