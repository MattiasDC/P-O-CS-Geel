#TODO: ZeppelinProperties
#TODO: ProperitesContainer
#TODO: ZeppelinSwitch
from domain.zeppelin import ZeppelinView

from kivy.properties import StringProperty, NumericProperty, ListProperty, ObjectProperty, OptionProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from util.colour import *


class PropertiesView(ScrollView):
    view = ObjectProperty(None)
    """ The actual layout of the this PropertiesView. """

    the_root = ObjectProperty(None)

    _added_zeppelins = {}

    def __init__(self, **kwargs):
        super(PropertiesView, self).__init__(**kwargs)
        self._zeppelin_handler = None

        layout = StackLayout(orientation='lr-tb', size_hint_y=None)
        self.view = layout

        #layout.bind(minimum_height=layout.setter('height'))
        self.add_widget(layout)
        self.do_scroll_y = True
        self.do_scroll_x = False

        layout.bind(minimum_height=layout.setter('height'))

    def add_zeppelin(self, zeppelin):
        new_zep_prop = ZeppelinProperties(zeppelin=zeppelin, height=(0.8 * self.width))
        self.add_to_view(new_zep_prop)

    def add_to_view(self, zeppelin_property):
        #self.n_widgets += 1
        self.view.add_widget(zeppelin_property)
        self._added_zeppelins[zeppelin_property.name] = zeppelin_property

    def remove_from_view(self, zeppelin_name):
        if zeppelin_name in self._added_zeppelins:
            self.view.clear_widgets(children=self._added_zeppelins[zeppelin_name])
            del self._added_zeppelins[zeppelin_name]

    def update(self, dt):
        for c in self.view.children:
            c.update(dt)
    #def set_zeppelin_handler(self, zep_handler):
    #    self._zeppelin_handler = zep_handler


class ZeppelinProperties(FloatLayout):
    name = StringProperty("None")
    """ Identifier of this zeppelin. """

    colour = OptionProperty("red", options=["yellow",
                                            "red",
                                            "none"])

    _colour_map = {"yellow": YELLOW_ZEPPELIN,
                   "red": RED_ZEPPELIN}

    """ The colour of this zeppelin. """

    zep_pos_x = NumericProperty(0.0)
    """ The x pos of this zeppelin. """
    zep_pos_y = NumericProperty(0.0)
    """ The y pos of this zeppelin. """

    zep_height = NumericProperty(0)
    """ The z pos of this zeppelin. """

    def __init__(self, **kwargs):
        """
        Construct a new ZeppelinProperties with the specified ZeppelinView.

        Parameters
        ----------
        zeppelin : ZeppelinView
            The ZeppelinView of this new ZeppelinProperties

        Pre-conditions
        --------------
        * zeppelin != null
        """
        super(ZeppelinProperties, self).__init__(**kwargs)

        self._zeppelin = kwargs["zeppelin"]
        self.name = self._zeppelin.identifier
        self.colour = self.name
        self.height = kwargs["height"]
        self.size_hint = (1.0, None)

    @property
    def zeppelin(self):
        return self._zeppelin

    def update(self, dt):
        """
        Update this ZeppelinProperties.
        """
        self.zep_height = float(self.zeppelin.height) / 10.0
        pos = self.zeppelin.position
        self.zep_pos_x, self.zep_pos_y = pos


#-----------------------------------------------------------------------------
# Common Elements
#-----------------------------------------------------------------------------
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


class PropertyEntryStringTeam(GridLayout):
    """
    PropertyEntryStringTeam specifies the variables and styling of a single entry of
    a team in the gui that has a string as value.

    It specifies a name, value for this property.
    """
    name = StringProperty('None')
    """ The name of this PropertyEntryString. """
    value = StringProperty('')
    """ The value of this PropertyEntryString. """
    colour = ListProperty([1, 1, 1])
    """ The colour of the team. """


#-----------------------------------------------------------------------------
from kivy.app import App


class PropViewApp(App):
    def build(self):
        zep1 = ZeppelinView("Red", (0,0), 50.0)
        zep2 = ZeppelinView("Yellow", (0,0), 50.0)

        zep1_prop = ZeppelinProperties(zeppelin=zep1, size_hint=(None, None), size=(480, 300))
        zep2_prop = ZeppelinProperties(zeppelin=zep2, size_hint=(None, None), size=(480, 300))

        interface = PropertiesView()

        interface.bind(minimum_height=interface.setter('height'))
        print interface
        interface.add_to_view(zep1_prop)
        interface.add_to_view(zep2_prop)

        return interface

Builder.load_file('./uix/properties_view.kv')