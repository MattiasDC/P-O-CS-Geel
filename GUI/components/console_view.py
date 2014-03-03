from kivy.uix.codeinput import CodeInput
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, OptionProperty, NumericProperty


class ConsoleView(CodeInput):
    """
    The console view displays the log of the balloon. It provides methods for adding
    new items to itself with the add_log_item method. The current log is can be
    accessed with log_items.
    """
    def __init__(self, **kwargs):
        super(ConsoleView, self).__init__(**kwargs)
        self._core_log_list = LogList("core")
        self._gui_log_list = LogList("GUI")

        self._core_log_list.bind(text=self._on_active_log_text_update)
        self._gui_log_list.bind(text=self._on_active_log_text_update)

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    active_log = OptionProperty("GUI", options=["GUI", "core"])
    """ The current active text in this console view. """

    def on_active_log(self, instance, new_active_log):
        if new_active_log == "GUI":
            self.text = self._gui_log_list.text
        elif new_active_log == "core":
            self.text = self._core_log_list.text

    #-------------------------------------------------------------------------
    # Methods for updating the LogLists
    #-------------------------------------------------------------------------
    def add_core_log_items(self, new_log_items_string):
        """
        Add the new_log_items_string items to the core_log of
        this ConsoleView.

        See: LogList - add_log_items
        """
        self._core_log_list.add_log_items(new_log_items_string)

        if self.active_log == "core":
            self.text = self._core_log_list.text

    def add_gui_log_items(self, new_log_items_string):
        """
        Add the new_log_items_string items to the gui_log of
        this ConsoleView.

        See: LogList - add_log_items
        """
        self._gui_log_list.add_log_items(new_log_items_string)

        if self.active_log == "GUI":
            self.text = self._gui_log_list.text

    def _on_active_log_text_update(self, instance, new_text):
        if instance.name == self.active_log:
            self.text = new_text


class LogList(EventDispatcher):
    """
    The LogList keeps a specified number of log items seperated by
    item seperators in a string.
    Additional items can be added with the add_log_items method.

    Invariants
    ----------
    * len(self.log_items) <= self.n_items
    * text = fold(item for item in self.log_items)
    """
    def __init__(self, name):
        """
        Construct a new LogList object.
        """
        self._log_items = []
        self.name = name

    @property
    def log_items(self):
        """ The log items currently displayed. """
        return self._log_items

    n_items = NumericProperty(20)
    """ The maximum number of log items displayed at any moment. """

    item_separator = StringProperty("-------------------------------------\n")
    """ The separator used to distinguish between items in the console.  """

    text = StringProperty('')
    """ The current log that is kept in memory. """

    def add_log_items(self, new_log_items_string):
        """
        Adds the log_item to this ConsoleView.

        Parameters
        ----------
        log_item : String
            The item that is added to this view. It should be formatted in "(item)#(item)#...)"

        Post-Conditions
        ---------------
        | log_item != '' -> \forall i \in log_item.split(\n) i \in self.log_item
        """
        log_items = self.log_items
        item_separator = self.item_separator
        n_items = self.n_items

        new_log_items = filter(lambda x: x != '',  new_log_items_string.split('#'))
        if len(new_log_items) >= n_items:
            # clear old log.
            del log_items[:]
            text = ''
            new_log_items = new_log_items[:n_items]
        else:
            n_items_to_remove = len(new_log_items) + len(log_items) - n_items
            text = self.text
            for i in xrange(n_items_to_remove):
                old_item = log_items.pop()
                text = text.replace(old_item + item_separator, '', 1)

        for item in new_log_items:
            log_items.insert(0, item)
            text = (item + item_separator) + text
        self.text = text