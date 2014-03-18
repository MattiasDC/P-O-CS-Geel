from threading import Thread
from time import sleep
from datetime import datetime
from math import sqrt
from values import *
import random
import ReceiverPi
import SenderPi
from math import copysign

class VirtualZeppelin(object):

    _current_position = None
    #_current_direction = None
    _goal_position = None
    _goal_height = None
    _current_height = None
    _speed_x = None
    _speed_y = None
    _color = None
    _senderPi_position = None       # The sender-object used for sending position-messages to the server
    _senderPi_height = None         # The sender-object used for sending height-messages to the server

    def __init__(self, x, y, goal_x, goal_y, height, v_x, v_y, color):
        #self._senderPi_position = SenderPi.SenderPi(color)
        #self._senderPi_height = SenderPi.SenderPi(color)
        self._current_position = (x,y)
        self._goal_position = (goal_x, goal_y)
        self._goal_height = height
        self._current_height = height
        self._speed_x = v_x
        self._speed_y = v_y
        self._color = color

    def get_current_position(self):
        return self._current_position

    def set_current_position(self, x, y):
        self._current_position = (x,y)
        #self._senderPi_position.sent_position(x, y)

    def get_goal_position(self):
        return self._goal_position

    def set_goal_position(self, x, y):
        self._goal_position = (x, y)

    def get_goal_height(self):
        return self._goal_height

    def set_goal_height(self, h):
        self._goal_height = h

    def get_current_height(self):
        return self._current_height

    def set_current_height(self, h):
        self._current_height = h
        #self._senderPi_position.sent_height(h)

    def get_speed_x(self):
        return self._speed_x

    def set_speed_x(self, v_x):
        self._speed_x = v_x

    def get_speed_y(self):
        return self._speed_y

    def set_speed_y(self, v_y):
        self._speed_y = v_y

    def get_color(self):
        return self._color

    def random_behaviour(self):
        pass

class Simulator(object):

    _stay_on_height_flag = False     # Flag to indicate the zeppelin should stay on the goal height or not.
    _stay_on_position_flag = False   # Flag to indicate the zeppelin should (try) to go to the goal position
    _with_other_zeppelin_flag = False

    _our_zeppelin = None
    _other_zeppelin = None

    #_senderPi_Console = None        # The sender-object used for sending console-messages to the server

    def __init__(self, other_zep):
        """
        Initialised all the variables, and initialises all the hardware components
        """
        #Initialisation and start of the communication with the shared server
        #self._senderPi_Console = SenderPi.SenderPi()
        #ReceiverPi.receive(self)

        self._our_zeppelin = VirtualZeppelin(0, 0, 100, 100, 100, speed_start, speed_start, team)
        if not (other_zep.get_color() is None or other_zep.get_color() == team):
            self._other_zeppelin = other_zep
            self._with_other_zeppelin_flag = True

    def start(self, height_flag, pos_flag):
        self.set_height_control(height_flag)
        self.set_navigation_mode(pos_flag)
        self.add_to_console('Simulator started')


# ------------------------------------------ Height Control ------------------------------------------------------------

    def _stay_on_height_thread(self):
        """
        Runs the _steady_on_height algorithm every second and updates the current speed
        """
        sleep_interval = 3

        while self._stay_on_height_flag:
            self._stay_on_height_thread_zep(self._our_zeppelin)
            if self._with_other_zeppelin_flag == True:
                self._stay_on_height_thread_zep(self._other_zeppelin)
            sleep(sleep_interval)

    def _stay_on_height_thread_zep(self, zeppelin):

        #Fluctuation of maximum 10%
        new_height = zeppelin.get_goal_height() * (1 + random.uniform(-0.1, 0.1))
        zeppelin.set_current_height(new_height)

# -------------------------------------------- Imageprocessing ---------------------------------------------------------

    def _update_position_thread(self):
        sleep_interval = 3
        while self._stay_on_position_flag:
            self._update_position_thread_zep(self._our_zeppelin, sleep_interval)
            if self._with_other_zeppelin_flag == True:
                self._update_position_thread_zep(self._other_zeppelin, sleep_interval)
                self._other_zeppelin.random_behaviour()
            sleep(sleep_interval)

    def _update_position_thread_zep(self, zeppelin, sleep_interval):
            #new_position = old_position*speed
            x = zeppelin.get_speed_x()*sleep_interval + zeppelin.get_current_position()[0]
            y = zeppelin.get_speed_y()*sleep_interval + zeppelin.get_current_position()[1]
            #At goal position: stop
            if x == zeppelin.get_goal_position()[0]:
                zeppelin.set_speed_x(0)
            #At goal position: stop
            if y == zeppelin.get_goal_position()[1]:
                zeppelin.set_speed_y(0)
            #Move away from goal for x (change direction)
            if abs(zeppelin.get_current_position()[0] - zeppelin.get_goal_position()[0]) < abs(x - zeppelin.get_goal_position()[0]):
                zeppelin.set_speed_x(-zeppelin.get_speed_x())
            #Move over goal-position in x-direction => stop op goal-position
            if (zeppelin.get_current_position()[0] - zeppelin.get_goal_position()[0]) > 0 and (x - zeppelin.get_goal_position()[0]) < 0 :
                zeppelin.set_speed_x(0)
                x = zeppelin.get_goal_position()[0]
            #Move over goal-position in x-direction => stop op goal-position
            if (zeppelin.get_current_position()[0] - zeppelin.get_goal_position()[0]) < 0 and (x - zeppelin.get_goal_position()[0]) > 0:
                zeppelin.set_speed_x(0)
                x = zeppelin.get_goal_position()[0]
            #Move away from goal for y (change direction)
            if abs(zeppelin.get_current_position()[1] - zeppelin.get_goal_position()[1]) < abs(y - zeppelin.get_goal_position()[1]):
                zeppelin.set_speed_y(-self.get_speed_y())
            #Move over goal-position in y-direction (change of sign) => stop op goal-position
            if (zeppelin.get_current_position()[1] - zeppelin.get_goal_position()[1] < 0) and (y - zeppelin.get_goal_position()[1] > 0):
                zeppelin.set_speed_y(0)
                y = zeppelin.get_goal_position()[1]
            #Move over goal-position in y-direction (change of sign) => stop op goal-position
            if (zeppelin.get_current_position()[1] - zeppelin.get_goal_position()[1] > 0) and (y - zeppelin.get_goal_position()[1] < 0):
                zeppelin.set_speed_y(0)
                y = zeppelin.get_goal_position()[1]
            #Update the position
            zeppelin.set_current_position(x, y)


# -------------------------------------------- Commands ----------------------------------------------------------------
    def add_to_console(self, line):
        """
        Adds a new line to the console
        """
        #self._senderPi_Console.sent_console_information(line)

    def quit_core(self):
        self._our_zeppelin.set_goal_height(ground_height)
        self._our_zeppelin.set_current_height = ground_height
        self.add_to_console('The zeppelin of team ' + team + ' has landed')
        self.set_height_control(False)
        self.set_navigation_mode(False)

# ---------------------------------------------- SETTERS --------------------------------------------------------------
    def set_goal_height(self, new_height):
        """
        Sets a new goal height (in cm)
        """
        try:
            self._our_zeppelin.set_goal_height(new_height)
            self.add_to_console("Goal height for team " + team + "is set to: " + str(new_height) + " mm")
        except (ValueError, TypeError) as e:
            self.add_to_console("Error on new goal height")

    def set_height_control(self, flag):
        if flag:
            self._stay_on_height_flag = True
            Thread(target=self._stay_on_height_thread).start()
            self.add_to_console("Height control is activated")
        else:
            self._stay_on_height_flag = False
            self.add_to_console("Height control is turned off")

    def set_goal_position(self, pos):
        """
        Sets a new goal height (in cm)
        """
        try:
            self._our_zeppelin.set_goal_position(pos[0], pos[1])
            self.add_to_console("Goal position for team " + team + "is set to: " + str(pos[0]) + "","" + str(pos[1]))
        except (ValueError, TypeError) as e:
            self.add_to_console("Error on new goal position")

    def set_navigation_mode(self, flag):
        if flag:
            self._stay_on_position_flag = True
            t = Thread(target=self._update_position_thread)
            t.start()
            self.add_to_console("Navigation is activated")
        else:
            self._stay_on_position_flag = False
            self.add_to_console("Navigation is turned off")

    #Set motor1 to the pwm-value determined by the parameter
    #Not used normally
    def set_motor1(self, pwm):
        #Do nothing
        pass

    #Set motor2 to the pwm-value determined by the parameter
    #Not used normally
    def set_motor2(self, pwm):
        #Do nothing
        pass

    #Set motor3 to the pwm-value determined by the parameter
    #Not used normally
    def set_motor3(self, pwm):
        #Do nothing
        pass

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    _other_zep = VirtualZeppelin(400, 400, 300, 300, 100,  -speed_start, -speed_start, 'rood')
    _simulator = Simulator(_other_zep)
    _simulator.start(True, True)


# ---------------------------------------------------------------------------------------------------------------------
















