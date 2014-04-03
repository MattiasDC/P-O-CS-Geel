from network import NetworkManager
from zeppelin import ZeppelinHandler
from grid import GridHandler


class InitialisationHandler(object):
    """
    InitialisationHandler initialises all other handlers at the beginning of the app.
    """
    def __init__(self):
        self._network_manager = NetworkManager()
        self._zeppelin_handler = ZeppelinHandler(self._network_manager)
        self._grid_handler = GridHandler()

    @property
    def zeppelin_handler(self):
        """
        Get the zeppelin handler.

        return
        ------
        * The zeppelin handler of this application.
        """
        return self._zeppelin_handler

    @property
    def grid_handler(self):
        return self._grid_handler