from threading import Thread
from time import sleep
from datetime import datetime
from math import sqrt
from values import *
from random import randrange
import ReceiverPi
import SenderPi


class VirtualZeppelin(object):

    _stay_on_height_flag = None     # Flag to indicate the zeppelin should stay on the goal height or not.
    _stay_on_position_flag = None   # Flag to indicate the zeppelin should (try) to go to the goal position

    _goal_position = (0, 0)         # The (x,y)- coordinate the zeppelin has to be at the moment
    _current_position = None        # The current position of the zeppelin
    _current_direction = None       # The direction of the zeppelin

    _goal_height = None             # The height where the zeppelin has to be at the moment
    _current_height = 10

    _senderPi = None

    _console = ""                   # String used to send info to the GUI
    _console2 = ""                  # Used as a double buffer to avoid conflict of simultaneous reading and writing
                                    # to the console

    def initialise(self, curr_pos):
        """
        Initialised all the variables, and initialises all the hardware components
        """

        self._current_position = curr_pos
        self._goal_height = 50

        #self.set_height_control(True)
        #self.set_navigation_mode(True)'
        #Initialisation and start of the communication with the shared server
        ReceiverPi.receive(self)
        sleep (0.1)
        self._senderPi = SenderPi.SenderPi()

# ------------------------------------------ Height Control ------------------------------------------------------------
    #TODO send it to the server

    def _stay_on_height_thread(self):
        """
        Runs the _steady_on_height algorithm every second and updates the current speed
        """
        diviation = 5
        sleep_interval = 1

        while self._stay_on_height_flag:
            self._current_height = self._goal_height * (1 + ((randrange(10) - diviation) / 10.0))
            sleep(sleep_interval)

# -------------------------------------------- Imageprocessing ---------------------------------------------------------

    def _update_position_thread(self):
        sleep_interval = 0.8
        speed = 20  # cm/s

        while self._stay_on_position_flag:
            # once the goal is reached do nothing
            if self._goal_height != self._current_height:
                # distance to goal < speed*sleep_interval -> goal reached
                if sqrt(abs(self._current_position[0] - self._goal_position[0])**2 + abs(self._current_position[1]
                        - self._goal_position[1])**2) < (speed*sleep_interval):
                    self._update_position(self._goal_position)
                else:
                    # take speed*sleep_interval off the distance -> calculate new pos
                    rico = (self._current_position[1] - self._goal_position[1])/(self._current_position[0] -
                                                                                 self._goal_position[0])
                    x = ((speed*sleep_interval) / rico) + self._current_position[0]
                    y = rico*x - rico*self._current_position[0] + self._current_position[1]
                    self._update_position((x, y))
            sleep(sleep_interval)

# -------------------------------------------- Commands ----------------------------------------------------------------

    def add_to_console(self, line):
        """
        Adds a new line to the console
        """
        self._console += delimiter + line

    def _clean_console(self):
        """
        Clean the current console commands
        """
        self._console2 = self._console
        self._console = ""

    def land(self):
        """
        Lands the zeppelin and quits heightcontrol
        """
        self.set_goal_height(ground_height)
        self._current_height = ground_height
        self.set_height_control(False)

    def _update_position(self, (x, y)):
        """
        Updates the current position, direction and sends it to the server
        """
        self._current_direction = (x, y)        # TODO
        self._current_position = (x, y)
        #TODO send it to the server

# ------------------------------------------ Getters -------------------------------------------------------------------
    def get_console_output(self):
        """
        Returns the console text
        """
        self._clean_console()
        return self._console2

    def get_grid(self):
        """
        Returns the grid
        """
        return self._grid

    def get_height(self):
        """
        Returns the current height in cm
        """
        return self._current_height

    def get_goal_height(self):
        """
        Returns the goal height in cm
        """
        return self._goal_height

    def get_position(self):
        """
        Returns the current position in (x,y) coordinates
        """
        return self._current_position

    def get_direction(self):
        """
        Returns a point in front of the current position  of the zeppelin in (x,y) coordinates
        """
        return self._current_direction

    def get_goal_position(self):
        """
        Returns the goal position in (x,y) coordinates
        """
        return self._goal_position

    def quit_core(self):
        self.land()
        self.set_navigation_mode(False)

# ---------------------------------------------- SETTERS --------------------------------------------------------------

    def set_goal_height(self, new_height):
        """
        Sets a new goal height (in cm)
        """
        print "nieuwe doelhoogte"
        try:
            self._goal_height = new_height
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Goal height is set to: "
                                + str(new_height) + " cm")
        except (ValueError, TypeError) as e:
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Error on new goal height "
                                + str(new_height) + " " + str(e))



    def set_height_control(self, flag):
        if flag:
            self._stay_on_height_flag = True
            Thread(target=self._stay_on_height_thread).start()
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Height control is activated")
        else:
            self._stay_on_height_flag = False
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Height control is turned off")

    def set_navigation_mode(self, flag):
        if flag:
            self._stay_on_position_flag = True
            Thread(target=self._update_position_thread()).start()
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Autonomous navigation has started")
        else:
            self._stay_on_position_flag = False
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Autonomous navigation has stopped")

    def set_goal_position(self, (x, y)):
        """
        Sets a new position in (x,y)- coordinates
        """
        print "nieuwe doelpositie"
        self._goal_position = (x, y)
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Goal position is set to: " + str((x, y)))

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    _simulator = VirtualZeppelin()
    _simulator.initialise(curr_pos=(100, 50))
    _simulator.set_goal_height(130)


# ---------------------------------------------------------------------------------------------------------------------
















