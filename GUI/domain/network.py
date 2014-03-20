import SenderGUI
from util.decorators import singleton
from util.values import TEAMS, OUR_TEAM
from ReceiverGUI import receive
#from SenderGUI import SenderGUI


@singleton
class NetworkManager(object):
    """
    The NetworkManager allows the DomainLayer access to the network services, thus
    updating system.
    """

    def __init__(self):
        self._zeppelin_cat = {}
        self._console_buffer = NetworkConsoleInfo()

        #self._sender = SenderGUI()
        #receive(self)
        self.nl_to_en = {"geel"     : "yellow",
                         "paars"    : "purple",
                         "blauw"    : "blue",
                         "rood"     : "red",
                         "groen"    : "green",
                         "wit"      : "white",
                         "indigo"   : "indigo",
                         "brons"    : "bronze",
                         "silver"   : "silver",
                         "goud"     : "gold",
                         "koper"    : "copper",
                         "platinum" : "platinum",
                         "ijzer"    : "iron"}

    @property
    def zeppelin_cat(self):
        return self._zeppelin_cat

    @property
    def console_buffer(self):
        return self._console_buffer

    #-----------------------------------------------------------------------------
    # Setters | Interface for network
    def set_position(self, team, new_pos):
        self._check_team(self.nl_to_en[team])
        self.zeppelin_cat[self.nl_to_en[team]].pos = new_pos

    def set_height(self, team, new_height):
        self._check_team(self.nl_to_en[team])
        self.zeppelin_cat[self.nl_to_en[team]].height = new_height

    def set_goal_pos(self, team, new_goal_pos):
        self._check_team(self.nl_to_en[team])
        if self.nl_to_en[team] == OUR_TEAM:
            self.zeppelin_cat[self.nl_to_en[team]].goal_pos = new_goal_pos

    def set_goal_height(self, team, new_goal_height):
        self._check_team(self.nl_to_en[team])
        if self.nl_to_en[team] == OUR_TEAM:
            self.zeppelin_cat[self.nl_to_en[team]].goal_height = new_goal_height

    def set_direction(self, team, new_direction):
        self._check_team(team)
        self._check_team(self.nl_to_en[team])
        if self.nl_to_en[team] == OUR_TEAM:
            self.zeppelin_cat[self.nl_to_en[team]].direction = new_direction

    def add_to_console(self, new_str):
        self.console_buffer.add(new_str)

    #-----------------------------------------------------------------------------
    # Getters | Interface for GUI
    def get_position(self, team):
        self._check_team(team)
        return self.zeppelin_cat[team].pos

    def get_height(self, team):
        #self._check_team(team)
        return self.zeppelin_cat[team].height

    def get_goal_pos(self, team):
        if team == OUR_TEAM:
            self._check_team(team)
            return self.zeppelin_cat[team].goal_pos

    def get_goal_height(self, team):
        if team == OUR_TEAM:
            self._check_team(team)
            return self.zeppelin_cat[team].goal_height

    def get_direction(self, team):
        if team == OUR_TEAM:
            self._check_team(team)
            return self.zeppelin_cat[team].direction

    def get_console(self):
        return self.console_buffer.get_and_clean()


    #-------------------------------------------------------------------------
    # Senders | Interface for GUI
    def send_goal_pos(self, (x, y)):
        self._sender.move_command(x, y)

    def send_goal_height(self, height):
        self._sender.height_command(height)

    def _check_team(self, team):
        if not team in self.zeppelin_cat:
            if team != OUR_TEAM:
                self.zeppelin_cat[team] = NetworkZeppelinView()
            else:
                self.zeppelin_cat[team] = NetworkZeppelinViewYellow()


class NetworkZeppelinView(object):
    def __init__(self, pos=[0, 0], height=1000):
        self._pos = pos
        self._height = height

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new_pos):
        self._pos = new_pos

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height


class NetworkZeppelinViewYellow(NetworkZeppelinView):
    def __init__(self, pos=[0, 0], height=1000, goal_pos=[0, 0], goal_height=1000, direction=0):
        super(NetworkZeppelinViewYellow, self).__init__(pos, height)

        self._goal_height = goal_height
        self._goal_pos = goal_pos
        self._direction = direction

    @property
    def goal_height(self):
        return self._goal_height

    @goal_height.setter
    def goal_height(self, new_goal_height):
        self._goal_height = new_goal_height

    @property
    def goal_pos(self):
        return self._goal_pos

    @goal_pos.setter
    def goal_pos(self, new_goal_pos):
        self._goal_pos = new_goal_pos

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction


class NetworkConsoleInfo(object):
    def __init__(self):
        self._buffer_load = []

    @property
    def buffer(self):
        return self._buffer_load

    def add(self, string):
        print "in-add buffer"
        self.buffer.append(string)

    def get_and_clean(self):
        print 'get_and_clean'
        bufbuf = self._buffer_load
        self._buffer_load = []

        return bufbuf
