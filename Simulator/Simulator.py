from threading import Thread
from time import sleep
from datetime import datetime
from math import sqrt, cos, sin, acos, degrees, atan2, pi
from values import *
import random
import ReceiverPi
import SenderPi
from math import copysign

class VirtualZeppelin(object):

    _current_position = None
    _current_direction = None
    _goal_position = None
    _goal_height = None
    _current_height = None
    _speed_x = None
    _speed_y = None
    _color = None

    _prev_error_soft = 0             # Prev error for the PID software algorithm
    _prev_errors_soft = [0]*10      # List of integral values for PID software
    _prev_derivative_soft = 0       # Prev derivative to substitute misreadings (0 values)

    _senderPi_position = None       # The sender-object used for sending position-messages to the server
    _senderPi_height = None         # The sender-object used for sending height-messages to the server

    def __init__(self, x, y, goal_x, goal_y, height, dir_x, dir_y, color):
        #self._senderPi_position = SenderPi.SenderPi(color)
        #self._senderPi_height = SenderPi.SenderPi(color)
        self._current_position = (x, y)
        self._goal_position = (goal_x, goal_y)
        self._goal_height = height
        self._current_height = height
        self._current_direction = (dir_x, dir_y)
        self._color = color
        self._prev_error_soft = 0
        self._prev_errors_soft = [0]*10
        self._prev_derivative_soft = 0

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

    def get_current_direction(self):
        return self._current_direction

    def set_current_direction(self, dir):
        self._current_direction = dir

    def get_color(self):
        return self._color

    def get_prev_error_soft(self):
        return self._prev_error_soft

    def set_prev_error_soft(self, value):
        self._prev_error_soft = value

    def get_prev_errors_soft(self):
        return self._prev_errors_soft

    def set_prev_errors_soft(self, value):
        self._prev_errors_soft = value

    def get_prev_derivative_soft(self):
        return self._prev_derivative_soft

    def set_prev_derivative_soft(self, value):
        self._prev_derivative_soft = value


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

        self._our_zeppelin = VirtualZeppelin(0, 0, 0, 100, 100, 0, 10, team)
        if not other_zep is None:
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
        new_height = self._deviation(zeppelin.get_goal_height(), 0.1, 10)
        zeppelin.set_current_height(new_height)

# -------------------------------------------- Imageprocessing ---------------------------------------------------------

    def _update_position_thread(self):
        sleep_interval = 3
        while self._stay_on_position_flag:
            self._update_position_thread_zep(self._our_zeppelin, sleep_interval)
            if self._with_other_zeppelin_flag == True:
                self._update_position_thread_zep(self._other_zeppelin, sleep_interval)
            sleep(sleep_interval)

    def _update_position_thread_zep(self, zeppelin, sleep_interval):
        angle = self._calculate_angle(zeppelin)
        print 'angle: ' + str(angle)
        pid_value = self._pid_moving(zeppelin, sleep_interval)
        # The pwm value calculated with the pid method has a maximum and minimum boundary
        if pid_value > pid_boundary:
            pid_value = pid_boundary
        elif pid_value < -pid_boundary:
            pid_value = -pid_boundary
        print 'pid_value: ' + str(pid_value)

        pid_value = pid_value / 100.0

        current_degrees = self._direction_to_degrees(zeppelin)
        print 'current_degrees: ' + str(degrees(current_degrees))
        speed_backward = max_speed * power_ratio

        motor1_x = 0
        motor1_y = 0
        motor2_x = 0
        motor2_y = 0

        if 0 <= angle <= 45:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * pid_value * (45-angle)/45.0
            print 'motor1_x: ' + str(motor1_x)
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * pid_value * (45-angle)/45.0
            print 'motor1_y: ' + str(motor1_y)
            motor2_x = cos(current_degrees + 3*pi/4) * max_speed * sleep_interval * pid_value
            print 'motor2_x: ' + str(motor2_x)
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * pid_value
            print 'motor2_y: ' + str(motor2_y)

        elif 45 < angle <= 135:
            # Right motor is used forwards, but because left motor is used backwards,
            # power ratio must be taken into account
            motor1_x = cos(current_degrees + pi/4) * speed_backward * sleep_interval * pid_value * (angle-45) * -1/90.0
            motor1_y = sin(current_degrees + pi/4) * speed_backward * sleep_interval * pid_value * (angle-45) * -1/90.0
            motor2_x = cos(current_degrees + 135) * max_speed * sleep_interval * pid_value * (angle-135) * -1/90.0 * power_ratio
            motor2_y = sin(current_degrees + 135) * max_speed * sleep_interval * pid_value * (angle-135) * -1/90.0 * power_ratio

        elif 135 < angle <= 180:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * -1)
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * -1)
            motor2_x = cos(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (angle-135) * -1/45.0)
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (angle-135) * -1/45.0)

        elif -45 <= angle < 0:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * pid_value
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * pid_value
            motor2_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * (45+angle)/45.0)
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (45+angle)/45.0)

        elif 135 <= angle < - 45:
            # Left motor is used forwards, but because right motor is used backwards,
            # power ratio must be taken into account
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * (angle+135) * 1/90.0 * power_ratio
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * (angle+135) * 1/90.0 * power_ratio
            motor2_x = cos(current_degrees + 3*pi/4) * speed_backward * sleep_interval * (angle+45) * 1/90.0
            motor2_y = sin(current_degrees + 3*pi/4) * speed_backward * sleep_interval * (angle+45) * 1/90.0

        elif -180 <= angle < -135:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * (pid_value * (angle+135) * 1/45)
            motor1_y = sin(current_degrees + pi/4) * (pid_value * (angle+135) * 1/45)
            motor2_x = cos(current_degrees + 3*pi/4) * (pid_value * -1)
            motor2_y = sin(current_degrees + 3*pi/4) * (pid_value * -1)

        change_x = motor1_x + motor2_x
        change_y = motor1_y + motor2_y
        print 'change_x: ' + str(change_x)
        print 'change_y: ' + str(change_y)
        new_x = zeppelin.get_current_position()[0] + change_x
        new_y = zeppelin.get_current_position()[1] + change_y
        print 'new_x without error: ' + str(new_x)
        print 'new_y without error: ' + str(new_y)
        new_x = self._deviation(new_x, 0.1, 400)
        new_y = self._deviation(new_y, 0.1, 400)
        print 'new_x with error: ' + str(new_x)
        print 'new_y with error: ' + str(new_y)
        zeppelin.set_current_position(new_x, new_y)
        new_dir_x = self._deviation(zeppelin.get_current_direction()[0], 0.1, 45)
        new_dir_y = self._deviation(zeppelin.get_current_direction()[1], 0.1, 45)
        zeppelin.set_current_direction((new_dir_x, new_dir_y))

    def _pid_moving(self, zeppelin, sleep_interval):
        error = self._calculate_distance_between(zeppelin.get_current_position(), zeppelin.get_goal_position())
        integral = (sum(zeppelin.get_prev_errors_soft()[1:]) + zeppelin.get_prev_error_soft()) * sleep_interval
        zeppelin.set_prev_errors_soft(zeppelin.get_prev_errors_soft()[1:])
        zeppelin.get_prev_errors_soft().append(error)

        derivative = (error - zeppelin.get_prev_error_soft()) / sleep_interval
        if derivative == 0:
            derivative = zeppelin.get_prev_derivative_soft()*0.9
        else:
            zeppelin.set_prev_derivative_soft(derivative)

        zeppelin.set_prev_error_soft(error)

        # print "curr : " + str(self.get_height()) + " goal : " + str(self._goal_height)
        # print "Error : " + str(pid_error*error) + " integral : " + str(pid_integral*integral) + " derivative : " \
        #      + str(pid_derivative*derivative)
        return pid_error*error + pid_integral*integral + pid_derivative*derivative

    @staticmethod
    def _direction_to_degrees(zeppelin):
        x = zeppelin.get_current_direction()[0] - zeppelin.get_current_position()[0]
        y = zeppelin.get_current_direction()[1] - zeppelin.get_current_position()[1]
        return atan2(y, x) - pi/2

    @staticmethod
    def _deviation(value, deviation, zero_range):
        if value != 0:
            return value * (1 + random.uniform(-deviation, deviation))
        return random.uniform(-zero_range, zero_range)

    @staticmethod
    def _calculate_distance_between(start, end):
        vector = end[0] - start[0], end[1] - start[1]
        distance = sqrt(pow(vector[0], 2) + pow(vector[1], 2))
        return distance

    @staticmethod
    def _calculate_angle(zeppelin):
        start_point = zeppelin.get_current_position()
        destination_point = zeppelin.get_goal_position()
        direction_point = zeppelin.get_current_direction()

        vector_a = destination_point[0] - direction_point[0], destination_point[1] - direction_point[1]
        vector_b = direction_point[0] - start_point[0], direction_point[1] - start_point[1]
        vector_c = destination_point[0] - start_point[0], destination_point[1] - start_point[1]

        length_a = sqrt(pow(vector_a[0], 2) + pow(vector_a[1], 2))
        length_b = sqrt(pow(vector_b[0], 2) + pow(vector_b[1], 2))
        length_c = sqrt(pow(vector_c[0], 2) + pow(vector_c[1], 2))

        # Angle between the current direction and the direction to the goal point in degrees.
        if length_b == 0 or length_c == 0:
            return 0

        angle = degrees(acos((pow(length_b, 2) + pow(length_c, 2) - pow(length_a, 2)) / (2 * length_b * length_c)))

        cross = vector_b[0] * vector_c[1] - vector_b[1] * vector_c[0]       # Cross product

        if cross < 0:
            angle *= -1         # angle is negative if the goal lies to the right of the current direction
        return angle



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
    _other_zep = VirtualZeppelin(400, 400, 300, 300, 100, 0, 0, 'rood')
    _simulator = Simulator(None)
    _simulator.start(False, True)


# ---------------------------------------------------------------------------------------------------------------------
















