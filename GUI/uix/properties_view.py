#TODO: ZeppelinProperties
#TODO: ProperitesContainer
#TODO: ZeppelinSwitch
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout


class PropertiesView(ScrollView):
    pass


class ZeppelinProperties(RelativeLayout):
    name = StringProperty("None")
    """ Identifier of this zeppelin. """

    colour = ListProperty([1, 1, 1])
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

    @property
    def zeppelin(self):
        return self._zeppelin

    def update(self, dt):
        """
        Update this ZeppelinProperties.
        """
        self.zep_height = self.zeppelin.height;
        self.zep_pos_x, self.zep_pos_y = self.zeppelin.position


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


#-----------------------------------------------------------------------------
class GridViewApp(App):
    def build(self):
        interface = ZeppelinProperties(zeppelin=None)
        return interface

Builder.load_file('./uix/properties_view.kv')