from network import NetworkManager


#=============================================================================
class ZeppelinHandler(object):
    """
    Controller Object for access to the Domain Logic of the zeppelins.
    """
    def __init__(self):
        self._zeppelin_catalog = {}

    def add_new_zeppelin(self, team_colour):
        """
        Add a new zeppelin with the given team_colour to this ZeppelinHandler.

        Parameters
        ----------
        team_colour : String
            the colour of the team that has build this Zeppelin that is added.

        * Factory method *
        """
        if team_colour != "yellow":
            self._zeppelin_catalog[team_colour] = Zeppelin(team_colour)
        else:
            self._zeppelin_catalog[team_colour] = ZeppelinControlled(team_colour)

    def get_zeppelin(self, team_colour):
        """
        Get the ZeppelinView of team_colour team.

        Parameters
        ----------
        team_colour : String
            the colour of the team that has build this Zeppelin

        return : ZeppelinView
            the zeppelin of that team .
        """
        return self._zeppelin_catalog[team_colour]

    def update_zeppelins(self, dt):
        """
        Update all zeppelins contained within this ZeppelinController

        Parameters
        ----------
        dt : float
            Time between update.
        """
        for zeppelin in self._zeppelin_catalog.values():
            zeppelin.update(dt)


#=============================================================================
class ZeppelinView(object):
    """
    A DataObject that has the properties of a single zeppelin.

    Invariants
    ----------
    * self.height >= 0.0
    * !\exists (zeppelin) zeppelin.identifier == self.identifier && zeppelin != self
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, identifier, pos, height):
        """
        Construct a new ZeppelinView with the specified identifier, position and height.

        Parameters
        ----------
        identifier : String
            Unique identifier that is coupled to this ZeppelinView. Currently the
            colour of the team that has created that specific zeppelin.
        pos : (Float, Float)
            The position of this new ZeppelinView
        height : Float
            The height of this new ZeppelinView

        Pre-conditions
        --------------
        * height >= 0.0
        * !\exists (zeppelin) zeppelin.identifier == identifier && zeppelin != (new self)

        Return
        ------
        * (new ZeppelinView) zeppelin
          where | zeppelin.position == pos
                | zeppelin.height == height
                | zeppelin.identifier == identifier
        """
        self._pos = pos
        self._height = height
        self._id = identifier

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    @property
    def position(self):
        """ The position of this Zeppelin. """
        return self._pos

    @property
    def height(self):
        """ The height of this Zeppelin. """
        return self._height

    @property
    def identifier(self):
        """ The identifier of this Zeppelin. """
        return self._id


#=============================================================================
class Zeppelin(ZeppelinView):
    """
    Data object that represents the logic and properties of a zeppelin (within
    the domain layer.)
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, identifier):
        self._network_manager = NetworkManager()
        pos = self._network_manager.get_position(identifier)
        height = self._network_manager.get_height(identifier)

        super(Zeppelin, self).__init__(identifier=identifier,
                                       pos=pos,
                                       height=height)


    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    @ZeppelinView.position.setter
    def position(self, new_pos):
        """
        Set self.position to new_pos

        Parameters
        ----------
        new_pos : (Float, Float)
            The new value for self.position

        Post-conditions
        ---------------
        * (new self).position == new_pos
        """
        self._pos = new_pos

    @ZeppelinView.height.setter
    def height(self, new_height):
        """
        Set self.height to new_height

        Parameters
        ----------
        new_height : Float
            The new height for self.height

        Pre-conditions
        --------------
        * new_height >= 0.0

        Post-conditions
        ---------------
        * (new self).height == new_height
        """
        self._height = new_height

    #-------------------------------------------------------------------------
    # Methods.
    #-------------------------------------------------------------------------
    def update(self, dt):
        self.position = self._network_manager.get_position(self.identifier)
        self.height = self._network_manager.get_height(self.identifier)


#=============================================================================
class ZeppelinControlled(Zeppelin):
    """
    Data object that represents the zeppelin that is constructed by Team
    Yellow.
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, identifier):
        super(ZeppelinControlled, self).__init__(identifier)
        self._goal_height = 100
        self._goal_pos = (0, 0)
        self._direction = 0

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
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
    def goal_pos(self, new_pos):
        self._goal_pos = new_pos

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction

    #TODO: add internal decisions system to this class.