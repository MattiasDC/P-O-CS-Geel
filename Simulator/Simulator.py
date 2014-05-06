from threading import Thread
from time import sleep, time
from datetime import datetime
from math import sqrt, cos, sin, acos, degrees, atan2, pi
from values import *
import random
import ReceiverPi
import SenderPi
import QRProcessing
import io
from PIL import Image
import urllib, cStringIO

from math import copysign
import logging

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
    _senderPi_direction = None      # The sender-object used for sending direction-messages to the server
    _senderPi_tablets = None        # The sender-object used for sending tablet-messages to the server
    _senderPi_goal_position = None

    qr_processor = None

    _last_tablet = False
    _prev_request = None

    def __init__(self, x, y, goal_x, goal_y, height, dir_x, dir_y, color):
        self._senderPi_position = SenderPi.SenderPi(color)
        self._senderPi_height = SenderPi.SenderPi(color)
        self._senderPi_direction = SenderPi.SenderPi(color)
        self._senderPi_tablets = SenderPi.SenderPi(color)
        self._senderPi_goal_position = SenderPi.SenderPi(color)
        self._current_position = (x, y)
        self._goal_position = (goal_x, goal_y)
        self._goal_tablet = 1
        self._goal_height = height
        self._current_height = height
        self._current_direction = (dir_x, dir_y)
        self._color = color
        self._prev_error_soft = 0
        self._prev_errors_soft = [0]*10
        self._prev_derivative_soft = 0
        self.qr_processor = QRProcessing.QRProcessing()

    def get_current_position(self):
        return self._current_position

    def set_current_position(self, x, y):
        self._current_position = (x,y)
        self._senderPi_position.sent_position(x, y)

    def get_goal_position(self):
        return self._goal_position

    def set_goal_position(self, x, y):
        self._senderPi_goal_position.sent_goal_position(x, y)
        self._goal_position = (x, y)

    def get_goal_tablet(self):
        return self._goal_tablet

    def set_goal_tablet(self, i):
        self._goal_tablet = i

    def get_goal_height(self):
        return self._goal_height

    def set_goal_height(self, h):
        self._goal_height = h

    def get_current_height(self):
        return self._current_height

    def set_current_height(self, h):
        self._current_height = h
        self._senderPi_height.sent_height(h)

    def get_current_direction(self):
        return self._current_direction

    def set_current_direction(self, direction):
        self._current_direction = direction
        self._senderPi_direction.sent_direction(Simulator._direction_to_degrees(self))

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

    def land(self):
        self.set_goal_height(10)

class Simulator(object):

    _stay_on_height_flag = False     # Flag to indicate the zeppelin should stay on the goal height or not.
    _stay_on_position_flag = False   # Flag to indicate the zeppelin should (try) to go to the goal position
    _with_other_zeppelin_flag = False

    _our_zeppelin = None
    _other_zeppelin = None

    _senderPi_Console = SenderPi.SenderPi(team)        # The sender-object used for sending console-messages to the server
    _tablets = None


    def __init__(self, other_zep, tablets):
        """
        Initialised all the variables, and initialises all the hardware components
        """

        self._tablets = tablets

        self._our_zeppelin = VirtualZeppelin(500, 500, 1000, 1000, 1000, 600, 700, team)
        goal = random.randint(1, len(self._tablets))
        self._our_zeppelin.set_goal_position(tablets[goal-1][0], tablets[goal-1][1])
        self._our_zeppelin.set_goal_tablet(goal)

        ReceiverPi.receive(self._our_zeppelin)
        if not other_zep is None:
            self._other_zeppelin = other_zep
            self._with_other_zeppelin_flag = True
            goal = random.randint(1, len(self._tablets))
            self._other_zeppelin.set_goal_position(tablets[goal-1][0], tablets[goal-1][1])
            self._other_zeppelin.set_goal_tablet(goal)

    def start(self, height_flag, pos_flag):
        self.set_height_control(height_flag)
        self.set_navigation_mode(pos_flag)
        self.add_to_console('Simulator started')

# ------------------------------------------ Height Control ------------------------------------------------------------
    def _stay_on_height_thread(self):
        """
        Runs the _steady_on_height algorithm every second and updates the current speed
        """
        sleep_interval = 1

        while self._stay_on_height_flag:
            self._stay_on_height_thread_zep(self._our_zeppelin)
            if self._with_other_zeppelin_flag == True:
                self._stay_on_height_thread_zep(self._other_zeppelin)
            sleep(sleep_interval)

    def _stay_on_height_thread_zep(self, zeppelin):
        #Fluctuation of maximum 10cm
        new_height = self._deviation(zeppelin.get_goal_height(), 50)
        zeppelin.set_current_height(new_height)

# -------------------------------------------- Imageprocessing ---------------------------------------------------------

    def _update_position_thread(self):
        sleep_interval = 0.8
        while self._stay_on_position_flag:
            self._update_position_thread_zep(self._our_zeppelin, sleep_interval)
            if self._with_other_zeppelin_flag == True:
                self._update_position_thread_zep(self._other_zeppelin, sleep_interval)
            sleep(sleep_interval)


    def _update_position_thread_zep(self, zeppelin, sleep_interval):
        angle = self._calculate_angle(zeppelin)
        #print 'angle: ' + str(angle)
        pid_value = self._pid_moving(zeppelin, sleep_interval)
        # The pwm value calculated with the pid method has a maximum and minimum boundary
        if pid_value > pid_boundary:
            pid_value = pid_boundary
        elif pid_value < -pid_boundary:
            pid_value = -pid_boundary
        #print 'pid_value: ' + str(pid_value)

        pid_value = pid_value / 100.0

        current_degrees = self._direction_to_degrees(zeppelin)
        #print 'current_degrees: ' + str(degrees(current_degrees))
        speed_backward = max_speed * power_ratio

        motor1_x = 0
        motor1_y = 0
        motor2_x = 0
        motor2_y = 0


        if 0 <= angle <= 45:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * pid_value * (45-angle)/45.0
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * pid_value * (45-angle)/45.0
            motor2_x = cos(current_degrees + 3*pi/4) * max_speed * sleep_interval * pid_value
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * pid_value
            #print 'PID motor1: ' + str(pid_value * (45-angle)/45)
            #print 'PID motor2: ' + str(pid_value)
        elif 45 < angle <= 135:
            # Right motor is used forwards, but because left motor is used backwards,
            # power ratio must be taken into account
            motor1_x = cos(current_degrees + pi/4) * speed_backward * sleep_interval * pid_value * (angle-45) * -1/90.0
            motor1_y = sin(current_degrees + pi/4) * speed_backward * sleep_interval * pid_value * (angle-45) * -1/90.0
            motor2_x = cos(current_degrees + 135) * max_speed * sleep_interval * pid_value * (angle-135) * -1/90.0 * power_ratio
            motor2_y = sin(current_degrees + 135) * max_speed * sleep_interval * pid_value * (angle-135) * -1/90.0 * power_ratio
            #print 'PID motor1: ' + str(pid_value * (angle-45) * -1/90)
            #print 'PID motor2: ' + str(pid_value * (angle-135) * -1/90 * power_ratio)

        elif 135 < angle <= 180:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * -1)
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * -1)
            motor2_x = cos(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (angle-135) * -1/45.0)
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (angle-135) * -1/45.0)
            #print 'PID motor1: ' + str(pid_value * -1)
            #print 'PID motor2: ' + str(pid_value * (angle-135) * -1/45)
        elif -45 <= angle < 0:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * pid_value
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * pid_value
            motor2_x = cos(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (45+angle)/45.0)
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * (45+angle)/45.0)
            #print 'PID motor1: ' + str(pid_value)
            #print 'PID motor2: ' + str(pid_value * (45+angle)/45)

        elif -135 <= angle < - 45:
            # Left motor is used forwards, but because right motor is used backwards,
            # power ratio must be taken into account
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * (angle+135) * 1/90.0 * power_ratio
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * (angle+135) * 1/90.0 * power_ratio
            motor2_x = cos(current_degrees + 3*pi/4) * speed_backward * sleep_interval * (angle+45) * 1/90.0
            motor2_y = sin(current_degrees + 3*pi/4) * speed_backward * sleep_interval * (angle+45) * 1/90.0
            #print 'PID motor1: ' + str(pid_value * (angle+135) * 1/90 * power_ratio)
            #print 'PID motor2: ' + str(pid_value * (angle+45) * 1/90)

        elif -180 <= angle < -135:
            # Both motors are used forwards
            motor1_x = cos(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * (angle+135) * 1/45)
            motor1_y = sin(current_degrees + pi/4) * max_speed * sleep_interval * (pid_value * (angle+135) * 1/45)
            motor2_x = cos(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * -1)
            motor2_y = sin(current_degrees + 3*pi/4) * max_speed * sleep_interval * (pid_value * -1)
            #print 'PID motor1: ' + str(pid_value * (angle+135) * 1/45)
            #print 'PID motor2: ' + str(pid_value * -1)
        #print 'motor1_x: ' + str(motor1_x)
        #print 'motor1_y: ' + str(motor1_y)
        #print 'motor2_x: ' + str(motor2_x)
        #print 'motor2_y: ' + str(motor2_y)
        change_x = motor1_x + motor2_x
        change_y = motor1_y + motor2_y
        #print 'change_x: ' + str(change_x)
        #print 'change_y: ' + str(change_y)
        new_x = zeppelin.get_current_position()[0] + change_x
        new_y = zeppelin.get_current_position()[1] + change_y
        #print 'new_x without error: ' + str(new_x)
        #print 'new_y without error: ' + str(new_y)
        #The movement of the zeppelin is not exact
        new_x = self._deviation(new_x, change_x/2)
        new_y = self._deviation(new_y, change_y/2)
        #print 'new_x with error: ' + str(new_x)
        #print 'new_y with error: ' + str(new_y)
        #The zeppelin will also turn a bit while moving
        new_dir_x = self._deviation(zeppelin.get_current_direction()[0] + change_x, 2*change_x)
        new_dir_y = self._deviation(zeppelin.get_current_direction()[1] + change_y, 2*change_y)
        if -drift_threshold<pid_value< drift_threshold:
            #If the pid_value is low, there is a chance the zeppelin wil start to drift away
            drift = self._drift(new_x, new_y, new_dir_x, new_dir_y, sleep_interval)
            new_x = drift[0]
            new_y = drift[1]
            new_dir_x = drift[2]
            new_dir_y = drift[3]
        zeppelin.set_current_position(new_x, new_y)
        zeppelin.set_current_direction((new_dir_x, new_dir_y))

        self._handle_tablets(zeppelin)

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
    def _deviation(value, range):
        return value + random.uniform(-range, range)

    @staticmethod
    def _drift(x, y, dir_x, dir_y, sleep_interval):
        max_drift = sleep_interval*max_speed
        drift_angle = random.uniform(-2*pi, 2*pi)
        if random.uniform(0,1) < drift_chance:
            #print "I drifted away"
            actual_drift = random.gauss(0, max_drift/1.65)
            drift = [0]*4
            drift[0] = x + actual_drift*cos(drift_angle)
            drift[1] = y + actual_drift*sin(drift_angle)
            drift[2] = dir_x + random.gauss(0, dir_x)
            drift[3] = dir_y + random.gauss(0, dir_y)
            #print "drift_x:" + str(drift[0])
            #print "drift_y:" + str(drift[1])
            #print "drift_dir_x:" + str(drift[2])
            #print "drift_dir_y:" + str(drift[3])
            return drift
        return [x, y, dir_x, dir_y]

    def _handle_tablets(self, zeppelin):
        distance = self._calculate_distance_between(zeppelin.get_current_position(), zeppelin.get_goal_position())
        if distance < distance_threshold:
            if zeppelin._last_tablet == True:
                zeppelin.land()
                self.add_to_console(zeppelin.get_color() + 'has landed')
                return "zeppelin "+ zeppelin.get_color() + " landed"
            if (zeppelin._prev_request is None):
                zeppelin._prev_request = time()
                zeppelin._senderPi_tablets.sent_tablet(zeppelin.get_goal_tablet(), zeppelin.qr_processor.pub_key)
                sleep(2)
            if time() - zeppelin._prev_request > 5:
                zeppelin._prev_request = None
            try:
                uri = host + ":5000/static/" + zeppelin.get_color() + zeppelin.get_goal_tablet() + ".png"
                img = urllib.urlretrieve(uri)[0]
                pil = Image.open(img).convert('L')
                qr_string = zeppelin.qr_processor.decrypt_pil(pil)
            except Exception:
                qr_string = None
            if not (qr_string is None):
                if (str(qr_string.split(":")[0]) == "tablet"):
                    #move to tablet
                    tablet_number = int(qr_string.split(":")[1])
                    x = self._tablets[tablet_number-1][0]
                    y = self._tablets[tablet_number-1][1]
                    zeppelin.set_goal_position((x,y))
                    zeppelin.set_goal_tablet(tablet_number)
                if (str(qr_string.split(":")[0]) == "position"):
                    #move to position
                    x = int(qr_string.split(":")[1].split(",")[0])
                    y = int(qr_string.split(":")[1].split(",")[1])
                    zeppelin.set_goal_position((x,y))
                    zeppelin.set_goal_tablet(0)
                    zeppelin._last_tablet = True


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

        x = (pow(length_b, 2) + pow(length_c, 2) - pow(length_a, 2)) / (2 * length_b * length_c)
        if x <= 1.0 and x >= -1.0:
            angle = degrees(acos((pow(length_b, 2) + pow(length_c, 2) - pow(length_a, 2)) / (2 * length_b * length_c)))
        elif x <= -1.0:
            angle = -pi
        else:
            angle = 0

        cross = vector_b[0] * vector_c[1] - vector_b[1] * vector_c[0]       # Cross product

        if cross < 0:
            angle *= -1         # angle is negative if the goal lies to the right of the current direction
        return angle

# -------------------------------------------- Commands ----------------------------------------------------------------
    def add_to_console(self, line):
        """
        Adds a new line to the console
        """
        self._senderPi_Console.sent_console_information(line)

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
    #Sets the tablets
    tablets = []
    with open("grid.csv", 'r') as tablet_file:
        for line in tablet_file.read().split('\n'):
            if (line is ""):
                pass
            elif not (str(line[0]) is "X" or str(line[0]) is "Y" or str(line[0]) is "B" or str(line[0]) is "R" or str(line[0]) is "G" or str(line[0]) is "W"):
                tablets.append((int(line.split(",")[0]), int(line.split(",")[1])))
    _simulator = Simulator(None, tablets)
    _simulator.start(True, True)


# ---------------------------------------------------------------------------------------------------------------------
















