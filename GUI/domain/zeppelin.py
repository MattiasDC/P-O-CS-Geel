from util.values import OUR_TEAM, TEAMS
from util.exceptions import IllegalArgumentException


#=============================================================================
# Handler
#=============================================================================
class ZeppelinHandler(object):
    """
    Controller Object for access to the Domain Logic of the zeppelins.
    """
    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, network_manager):
        """
        Construct a new (empty) zeppelin Handler.
        """
        self._zeppelin_catalog = {}
        self._network_manager = network_manager

    #-------------------------------------------------------------------------
    # Methods
    #-------------------------------------------------------------------------
    def add_new_zeppelin(self, team_colour):
        """
        Add a new zeppelin with the given team_colour to this ZeppelinHandler.

        Parameters
        ----------
        team_colour : String
            the colour of the team that has build this Zeppelin that is added.

        * Factory method *

        Throws
        ------
        IllegalArgumentException | not team_colour in TEAMS.
        """
        if not team_colour in TEAMS:
            raise IllegalArgumentException()

        if team_colour != OUR_TEAM:
            self._zeppelin_catalog[team_colour] = Zeppelin(team_colour, self._network_manager)
        else:
            self._zeppelin_catalog[team_colour] = ZeppelinControlled(team_colour, self._network_manager)

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
# Zeppelin View and Domain.
#=============================================================================
class Zeppelin(object):
    """
    A DataObject that has the properties of a single zeppelin.

    Invariants
    ----------
    * self.height >= 0.0
    * !\exists (zeppelin) zeppelin.identifier == self.identifier &&
                          zeppelin != self
    """

    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, identifier, network_manager):
        """
        Construct a new ZeppelinView with the specified identifier, position
        and height.

        Parameters
        ----------
        identifier : String
            Unique identifier that is coupled to this ZeppelinView. Currently
            the colour of the team that has created that specific zeppelin.
        network_manager : NetworkManager
            The network manager that keeps the information of the zeppelins as
            send by the server.

        Pre-conditions
        --------------
        * not network_manager is None
        * !\exists (zeppelin) zeppelin.identifier == identifier &&
                              zeppelin != (new self)

        Return
        ------
        * (new ZeppelinView) zeppelin
          where | zeppelin.identifier == identifier
        """
        # Set basic variables
        self._network_manager = network_manager
        self._id = identifier

        # Obtain position and and height from the network manager.
        self._pos = self._network_manager.get_position(self.identifier)
        self._height = self._network_manager.get_height(self.identifier)

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

    #-------------------------------------------------------------------------
    # Internal Setters
    #-------------------------------------------------------------------------
    def _set_pos(self, new_pos):
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

    def _set_height(self, new_height):
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
    # Updater
    #-------------------------------------------------------------------------
    def update(self, dt):
        """
        Update this zeppelins position and height.

        Parameters
        ----------
        dt : float
            Time since last update.
        """
        self._set_pos(self._network_manager.get_position(self.identifier))
        self._set_height(self._network_manager.get_height(self.identifier))


class ZeppelinControlled(Zeppelin):
    """
    A DataObject that has the properties of a single zeppelin that is owned by this team.

    Invariants
    ----------
    * self.height >= 0.0
    * self.goal_height >= 0.0
    * !\exists (zeppelin) zeppelin.identifier == self.identifier && zeppelin != self
    """

    #-------------------------------------------------------------------------
    # Constructor
    #-------------------------------------------------------------------------
    def __init__(self, identifier, network_manager):
        super(ZeppelinControlled, self).__init__(identifier, network_manager)

        self._goal_pos = self._network_manager.get_goal_pos(self.identifier)
        self._goal_height = self._network_manager.get_goal_height(self.identifier)
        self._direction = self._network_manager.get_direction(self.identifier)

    #-------------------------------------------------------------------------
    # Properties
    #-------------------------------------------------------------------------
    @property
    def goal_height(self):
        """
        The goal position of this Controlled Zeppelin.
        """
        return self._goal_height

    @property
    def goal_pos(self):
        """
        The goal position of this zeppelin.
        """
        return self._goal_pos

    @property
    def direction(self):
        """
        The direction of this zeppelin.
        """
        return self._direction

    #-------------------------------------------------------------------------
    # Internal Setters
    #-------------------------------------------------------------------------
    def _set_goal_pos(self, new_goal_pos):
        """
        Set self.goal_position to new_goal_pos

        Parameters
        ----------
        new_goal_pos : (Float, Float)
            The new value for self.goal_position

        Post-conditions
        ---------------
        * (new self).goal_position == new_goal_pos
        """
        self._goal_pos = new_goal_pos

    def _set_goal_height(self, new_goal_height):
        """
        Set self.goal_height to new_goal_height

        Parameters
        ----------
        new_goal_height : Float
            The new goal height for self.goal_height

        Pre-conditions
        --------------
        * new_goal_height >= 0.0

        Post-conditions
        ---------------
        * (new self).goal_height == new_goal_height
        """
        self._goal_height = new_goal_height

    def _set_direction(self, new_direction):
        """
        Set self.direction to new_direction

        Paramaters
        ----------
        new_direction : Float
            The new direction of this ZeppelinControlled in radians

        Post-conditions
        ---------------
        * (new self).direction = new_direction
        """
        self._direction = new_direction

    #-------------------------------------------------------------------------
    # Updater
    #-------------------------------------------------------------------------
    def update(self, dt):
        """
        Update this zeppelins position and height.

        Parameters
        ----------
        dt : float
            Time since last update.
        """
        super(ZeppelinControlled, self).update(dt)

        self._set_goal_pos(self._network_manager.get_goal_pos(self.identifier))
        self._set_goal_height(self._network_manager.get_goal_height(self.identifier))
        self._set_direction(self._network_manager.get_direction(self.identifier))