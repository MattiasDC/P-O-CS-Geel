from threading import Thread
from time import sleep
from datetime import datetime
from math import pow, sqrt, acos, degrees
from values import *

#TODO pas aan begonnen!


class VirtualZeppelin(object):

    _stay_on_height_flag = None     # Flag to indicate the zeppelin should stay on the goal height or not.
    _stay_on_position_flag = None   # Flag to indicate the zeppelin should (try) to go to the goal position

    _grid = None                    # The grid

    _current_position = None        # The current position of the zeppelin
    _current_direction = None       # The direction of the zeppelin

    _goal_height = None             # The height where the zeppelin has to be at the moment
    _current_height = None
    _goal_position = None           # The (x,y)- coordinate the zeppelin has to be at the moment

    _console = ""                   # String used to send info to the GUI
    _console2 = ""                  # Used as a double buffer to avoid conflict of simultaneous reading and writing
                                    # to the console

    def initialise(self):
        """
        Initialised all the variables, and initialises all the hardware components
        """

# ------------------------------------------ Height Control ------------------------------------------------------------
    #TODO send it to the server

    def _stay_on_height_thread(self):
        """
        Runs the _steady_on_height algorithm every second and updates the current speed
        """
        while self._stay_on_height_flag:
            self._current_height = self._goal_height
            sleep(0.5)

# ------------------------------------------ Navigation Control --------------------------------------------------------
        # TODO check this formulas

    def _navigation_thread(self):
        """
        SoftwarePWM thread
        Motor 1 is the left motor, motor 2 is the right motor.
        """
        while self._stay_on_position_flag:
            start = self.get_position()
            finish = self.get_goal_position()
            direction = self.get_direction()
            angle = self._calculate_angle(start, finish, direction)
            pid_value = self._pid_moving(start, finish)

            # The pwm value calculated with the pid method has a maximum and minimum boundary
            if pid_value > pid_boundary:
                pid_value = pid_boundary
            elif pid_value < -pid_boundary:
                pid_value = -pid_boundary

            if 0 <= angle <= 45:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value * (45-angle)/45)
                self._motors.motor2_pwm(pid_value)
            elif 45 < angle <= 135:
                # Right motor is used forwards, but because left motor is used backwards,
                # power ratio must be taken into account
                self._motors.motor1_pwm(pid_value * (angle-45) * -1/90)
                self._motors.motor2_pwm(pid_value * (angle-135) * -1/90 * power_ratio)
            elif 135 < angle <= 180:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value * -1)
                self._motors.motor2_pwm(pid_value * (angle-135) * -1/45)
            elif -45 <= angle < 0:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value)
                self._motors.motor2_pwm(pid_value * (45+angle)/45)
            elif -135 <= angle < -45:
                # Left motor is used forwards, but because right motor is used backwards,
                # power ratio must be taken into account
                self._motors.motor1_pwm(pid_value * (angle+135) * 1/90 * power_ratio)
                self._motors.motor2_pwm(pid_value * (angle+45) * 1/90)
            elif -180 <= angle < -135:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value * (angle+135) * 1/45)
                self._motors.motor2_pwm(pid_value * -1)
            sleep(pid_interval)



# -------------------------------------------- Imageprocessing ---------------------------------------------------------

    def _update_position_thread(self):
        while self._stay_on_position_flag:
            self._update_position(self._positioner.find_location(self._camera.take_picture()))
            sleep(0.8)

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
        self._current_direction = (x, y) #TODO
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
        return self._sensor.get_height()

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

# ---------------------------------------------- SETTERS --------------------------------------------------------------

    def set_goal_height(self, new_height):
        """
        Sets a new goal height (in cm)
        """
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

    def set_goal_position(self, (x, y)):
        """
        Sets a new position in (x,y)- coordinates
        """
        self._goal_position = (x, y)
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Goal position is set to: " + str((x, y)))

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print "Hi"
# ---------------------------------------------------------------------------------------------------------------------