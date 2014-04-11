from threading import Thread
from time import sleep, time
from datetime import datetime
from math import pow, sqrt, acos, degrees, pi, atan

import Hardware.Camera as Cam
import Hardware.DistanceSensor as DistanceSensor
import ImageProcessing.Positioner as Positioner
import ImageProcessing.Grid as Grid
from Hardware.Motors import MotorControl
from values import *
import Communication.ReceiverPi as ReceiverPi
import Communication.SenderPi as SenderPi


class Core(object):
    _sensor = None                  # The distance sensor
    _camera = None                  # The camera

    _motors = None                  # Motors (= MotorControl)

    _senderPi_position = None       # The sender-object used for sending position-messages to the server
    _senderPi_height = None         # The sender-object used for sending height-messages to the server
    _senderPi_direction = None      # The sender-object used for sending direction-messages to the server
    _SenderPi_Console = None        # The sender-object used for sending console-messages to the server

    _positioner = None              # Positioner

# ---------------------------------------------------------------------------------------------------------------------
    _stay_on_height_flag = None     # Flag to indicate the zeppelin should stay on the goal height or not.
    _stay_on_position_flag = None   # Flag to indicate the zeppelin should (try) to go to the goal position

    _grid = None                    # The grid

    _current_direction = (0, 0)       # The direction of the zeppelin
    _current_angle = 0                # The current angle of the zeppelin

    _goal_height = 100            # The height where the zeppelin has to be at the moment
    _goal_position = (0, 0)           # The (x,y)- coordinate the zeppelin has to be at the moment

    _prev_error = 0                 # Prev error for the PID algorithm
    _prev_errors = [0]*10           # List of integral values for PID
    _interval = 0.5                 # PID interval
    _prev_derivative = 0            # Prev derivative to substitute misreadings (0 values)
    _prev_error_soft = 0            # Prev error for the PID software algorithm
    _prev_errors_soft = [0]*10      # List of integral values for PID software
    _prev_derivative_soft = 0       # Prev derivative to substitute misreadings (0 values)

    _position_update_interval = 0.6 # The interval where after imageprocssing is ran

    def initialise(self):
        """
        Initialised all the variables, and initialises all the hardware components
        """

        # Start the server
        self._start_server()

        # Initialisation the motors
        self._motors = MotorControl(self)

        # Initialisation of the Distance Sensor
        self._sensor = DistanceSensor
        self._sensor.initialise(self)
        self._sensor.start()

        # Initialisation of the camera
        self._camera = Cam
        self._camera.initialise(self)

        # Sets the grid
        self._grid = Grid.Grid.from_file("/home/pi/P-O-Geel-2/Pi/grid.csv")

        # Start height control
        self._goal_height = ground_height
        self.set_height_control(True)

        # Get current position
        self._positioner = Positioner
        #   Boolean: true = offline, false= on the pi
        self._positioner.set_core(self, False)

        # Start navigation
        self.set_navigation_mode(True)

# ------------------------------------------ Height Control ------------------------------------------------------------
    def _stay_on_height_thread(self):
        """
        Runs the _steady_on_height algorithm every second and updates the current speed
        """
        while self._stay_on_height_flag:
            self._motors.set_pwm(self._pid())
            self._senderPi_height.sent_height(self._sensor.get_height()*10.0)
            sleep(pid_interval)                             # time in seconds

    def _pid(self):
        """
        Well we all know PID...
        """
        error = self._goal_height - self.get_height()
        integral = (sum(self._prev_errors[1:]) + self._prev_error) * pid_interval
        self._prev_errors = self._prev_errors[1:]
        self._prev_errors.append(error)

        derivative = (error - self._prev_error) / pid_interval
        if derivative == 0:
            derivative = self._prev_derivative*0.9
        else:
            self._prev_derivative = derivative

        self._prev_error = error

        # print "curr : " + str(self.get_height()) + " goal : " + str(self._goal_height)
        # print "Error : " + str(pid_error*error) + " integral : " + str(pid_integral*integral) + " derivative : " \
        #      + str(pid_derivative*derivative)
        return pid_error*error + pid_integral*integral + pid_derivative*derivative

# ------------------------------------------ Navigation Control --------------------------------------------------------
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

    def _pid_moving(self, start, finish):
        error = self._calculate_distance_between(start, finish)
        integral = (sum(self._prev_errors_soft[1:]) + self._prev_error_soft) * pid_interval
        self._prev_errors_soft = self._prev_errors_soft[1:]
        self._prev_errors_soft.append(error)

        derivative = (error - self._prev_error_soft) / pid_interval
        if derivative == 0:
            derivative = self._prev_derivative_soft*0.9
        else:
            self._prev_derivative_soft = derivative

        self._prev_error_soft = error

        # print "curr : " + str(self.get_height()) + " goal : " + str(self._goal_height)
        # print "Error : " + str(pid_error*error) + " integral : " + str(pid_integral*integral) + " derivative : " \
        #      + str(pid_derivative*derivative)
        return pid_error*error + pid_integral*integral + pid_derivative*derivative

    @staticmethod
    def _calculate_distance_between(start, end):
        vector = end[0] - start[0], end[1] - start[1]
        distance = sqrt(pow(vector[0], 2) + pow(vector[1], 2))
        return distance

    @staticmethod
    def _calculate_angle(start_point, destination_point, direction_point):
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

        if -1.0 <= x <= 1.0:
            angle = degrees(acos((pow(length_b, 2) + pow(length_c, 2) - pow(length_a, 2)) / (2 * length_b * length_c)))
        elif x <= -1.0:
            angle = -pi
        else:
            angle = 0

        cross = vector_b[0] * vector_c[1] - vector_b[1] * vector_c[0]       # Cross product

        if cross < 0:
            angle *= -1         # angle is negative if the goal lies to the right of the current direction
        return angle

# -------------------------------------------- Imageprocessing ---------------------------------------------------------
    def _update_position_thread(self):
        while self._stay_on_position_flag:
            start = time()
            pos, direc, angle = self._positioner.find_location(self._camera.take_picture(), False)
            if not (pos is None or direc is None or angle is None):
                self._update_position(pos, direc, angle)
           # if (self._position_update_interval - (time() - start)) > 0:
            #    sleep(self._position_update_interval - (time() - start))

# -------------------------------------------- Commands ----------------------------------------------------------------

    def add_to_console(self, line):
        """
        Adds a new line to the console
        """
        self._SenderPi_Console.sent_console_information(line)

    def quit_core(self):
        """
        Stops everything, console output still available. Zeppelin "lands"; Quit server should be called after this
        """
        self.set_navigation_mode(False)
        self.set_height_control(False)
        self.land()

        self._sensor.stop()
        self._motors.stop()
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "The core has gracefully quited")

    def _start_server(self):
        """
        Initialises everything to start the server
        """
        ReceiverPi.receive(self)
        sleep(0.1)
        self._senderPi_position = SenderPi.SenderPi()
        self._senderPi_height = SenderPi.SenderPi()
        self._SenderPi_Console = SenderPi.SenderPi()
        self._senderPi_direction = SenderPi.SenderPi()

    def land(self):
        """
        Lands the zeppelin and quits heightcontrol
        """
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "The zeppelin started the landing procedure")
        self.set_goal_height(ground_height)
        while self.get_height() > (ground_height+5):
            sleep(1)
        self.set_height_control(False)

    def _update_position(self, (x, y), (q, z), angle):
        """
        Updates the current position, direction and sends it to the server
        """
        if q % 2 == 0:
            self._current_direction = (q*400.0, z*400.0)
        else:
            self._current_direction = (q*400.0+200, z*400.0)
        print "core: ", str((x, y))
        self._senderPi_position.sent_position(x, y)
        self._senderPi_direction.sent_direction(self.get_angle())
        self._current_angle = (angle * 180.0) / pi
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] "
                            + "Current position: " + str(self.get_position()))

# ------------------------------------------ Getters -------------------------------------------------------------------
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
        return self._positioner.get_currentposition()

    def get_angle(self):
        return self._current_angle

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

    def get_fixed_motor_status(self):
        """
        Returns the status (movement) of the zeppelin
        """
        return self._motors.get_fixed_motors_status()

    def get_motor_z_pwm(self):
        """
        Returns the status of _pwm_motor in %
        """
        return self._motors.get_pwm()

    def get_motor1_status(self):
        """
        Returns the status of motor1
        """
        return self._motors.get_motor1_status()

    def get_motor2_status(self):
        """
        Returns the status of motor2
        """
        return self._motors.get_motor2_status()

# ---------------------------------------------- SETTERS --------------------------------------------------------------

    def set_motor1(self, pwm):
        self._motors.motor1_pwm(pwm)

    def set_motor2(self, pwm):
        self._motors.motor2_pwm(pwm)

    def set_motor3(self, pwm):
        self._motors.set_pwm(pwm)

    def set_goal_height(self, new_height):
        """
        Sets a new goal height (in cm)
        """
        try:
            self._goal_height = new_height/10.0
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Goal height is set to: "
                                + str(new_height/10.0) + " cm")
        except (ValueError, TypeError) as e:
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Error on new goal height "
                                + str(new_height/10.0) + " " + str(e))

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

    def set_navigation_mode(self, flag):
        if flag:
            self._stay_on_position_flag = True
            Thread(target=self._update_position_thread).start()
            #Thread(target=self._navigation_thread).start()
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Autonomous navigation has started")
        else:
            self._stay_on_position_flag = False
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Autonomous navigation has stopped")

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    core = Core()
    core.initialise()
    print "Job's done"
    core.add_to_console("Welcome to the zeppelin of TEAM GEEL")
    core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "The core on the raspberry pi has started")
    core.set_goal_height(1300)

# ---------------------------------------------------------------------------------------------------------------------