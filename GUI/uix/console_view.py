from kivy.properties import ListProperty, ObjectProperty
from domain.network import NetworkManager

from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout


class Console(ScrollView):
    MAX = 100

    items = ListProperty([])
    view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Console, self).__init__(**kwargs)

        #manages the actual log items.
        layout = StackLayout(orientation='lr-tb', size_hint_y=None)
        self.view = layout

        self.add_widget(layout)
        self.do_scroll_y = True
        self.do_scroll_x = False

        layout.bind(minimum_height=layout.setter('height'))

        self._network_interface = NetworkManager()
        self.n_items = 0

    @property
    def log_items(self):
        """ The log items currently displayed. """
        return self._log_items

    def add_log_items(self, items):
        if len(items) >= self.MAX:
            nmb_to_many = len(items) - self.MAX
            items = items[nmb_to_many:]

            to_del = self.items
            self.n_items = len(items)
        else:
            nmb_to_del = min(0, self.n_items - self.MAX)
            to_del = self.items[:nmb_to_del]

            self.n_items += (len(items) - len(to_del))

        if to_del is []:
            self.view.clear_widgets(children=to_del)

        for txt in items:
            new_widget = ConsoleItem(text=txt, height=(0.04 * self.width))
            self.view.add_widget(new_widget)

    def update(self, dt):
        new_strings = self._network_interface.get_console()
        #for string in self._network_interface.get_console():
        #    new_strings.extend(filter(lambda x: x != '',  string.split('#')))
        self.add_log_items(new_strings)
        #self.add_log_items(['fuck this shit'])


#class ConsoleItem(GridLayout):
#    item_text = StringProperty("")
#    nmb = StringProperty("")
#
#    def __init__(self, **kwargs):


class ConsoleItem(Label):
    def __init__(self, **kwargs):
        super(ConsoleItem, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = 38.4#kwargs['height']
        self.text = kwargs['text']
        self.halign = 'left'
        self.valign = 'middle'
        self.color = [1.0, 1.0, 1.0, 1.0]

        self.font_size = 0.8 * self.height

