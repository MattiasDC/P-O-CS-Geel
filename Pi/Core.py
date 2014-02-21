
from threading import Thread
from time import sleep
from datetime import datetime
import hardware.Camera as Cam
import hardware.DistanceSensor as DistanceSensor
from hardware.Motors import MotorControl
from QRHandeling.QRParser import QRParser
import QRHandeling.CommandController as CommandController
from communication.NetworkConnection import PIServer
from math import pow, sqrt, acos, degrees
from values import *


class Core(object):
    _sensor = None                  # The distance sensor
    _camera = None                  # The camera

    _motors = None                  # Motors (= MotorControl)
    _qr_parser = None               # QR parser
    _command_controller = None      # Command controller

    _handler = None                 # The handler for the connection
    _server = None                  # The server for the connection

# ---------------------------------------------------------------------------------------------------------------------

    _stay_on_height_flag = None     # Flag to indicate the zeppelin should stay automatically on the same height
    _camera_mode_flag = None        # False = dir mode; True = normal camera mode
    _auto_mode_flag = None          # False = manual mode with arrow keys; True = automatically seeking for qr codes and
                                    # execute them.
    _stay_on_position_flag = None # Flag to indicate the zeppelin has a new position to move to.

    _goal_height = None             # The height where the zeppelin has to be at the moment

    _goal_position = None           # The (x,y)- coordinate the zeppelin has to be at the moment

    _console = ""                   # String used to send info to the GUI
    _console2 = ""                  # Used as a double buffer to avoid conflict of simultaneous reading and writing
                                    # to the console

    _prev_error = 0                 # Prev error for the PID algorithm
    _prev_errors = [0]*10           # List of integral values for PID
    _interval = 0.5                 # PID interval
    _prev_derivative = 0            # Prev derivative to substitute misreadings (0 values)
    _prev_error_soft = 0            # Prev error for the PID software algorithm
    _prev_errors_soft = [0]*10      # List of integral values for PID software
    _prev_derivative_soft = 0       # Prev derivative to substitute misreadings (0 values)

    _nr_exec_qr = 0                 # The number of executed qr command after the last time this value has been read
                                    # by the GUI
    _nr_exec_qr2 = 0                # Double buffer...

    def initialise(self):
        """
        Initialised all the variables, and initialises all the hardware components
        """

        # Initialisation the motors
        self._motors = MotorControl(self)

        # Initialisation of the Distance Sensor
        self._sensor = DistanceSensor
        self._sensor.initialise(self)
        self._sensor.start()

        # Initialisation of the camera
        self._camera = Cam
        self._camera.initialise(self)
        self.set_picture_mode(False)

        # Initialise QR handling + CommandController
        self._qr_parser = QRParser(self)
        self._command_controller = CommandController
        self._command_controller.initialise(self)
        self.set_auto_mode(False)

        # Start the server
        self._start_server()

        # Start height control
        self._goal_height = ground_height
        self.set_height_control(True)

# ------------------------------------------ Height Control ------------------------------------------------------------

    def _stay_on_height_thread(self):
        """
        Runs the _steady_on_height algorithm every second and updates the current speed
        """
        while self._stay_on_height_flag:
            self._motors.set_pwm(self._pid())
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

# ------------------------------------------ Control Commands ----------------------------------------------------------
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
            if angle >= 0 and angle <= 45:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value * (45-angle)/45)
                self._motors.motor2_pwm(pid_value)
            elif angle > 45 and angle <=135:
                # Right motor is used forwards, but because left motor is used backwards,
                # power ratio must be taken into account
                self._motors.motor1_pwm(pid_value * (angle-45) * -1/90)
                self._motors.motor2_pwm(pid_value * (angle-135) * -1/90 * power_ratio)
            elif angle > 135 and angle <= 180:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value * -1)
                self._motors.motor2_pwm(pid_value * (angle-135) * -1/45)
            elif angle < 0 and angle >= -45:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value)
                self._motors.motor2_pwm(pid_value * (45+angle)/45)
            elif angle < -45 and angle >= -135:
                # Left motor is used forwards, but because right motor is used backwards,
                # power ratio must be taken into account
                self._motors.motor1_pwm(pid_value * (angle+135) * 1/90 * power_ratio)
                self._motors.motor2_pwm(pid_value * (angle+45) * 1/90)
            elif angle < -135 and angle >= -180:
                # Both motors are used forwards
                self._motors.motor1_pwm(pid_value * (angle+135) * 1/45)
                self._motors.motor2_pwm(pid_value * -1)
            sleep(pid_interval)

    def _pid_moving(self, start, finish):
        """
        Well we all know PID...
        """
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
    def _calculate_distance_between(self, start, end):
        vector = end[0] - start[0], end[1] - start[1]
        distance = sqrt(pow(vector[0], 2) + pow(vector[1], 2))
        return distance

    @staticmethod
    def _calculate_angle(self, start_point, destination_point, direction_point):
        vector_a = destination_point[0] - direction_point[0], destination_point[1] - direction_point[1]
        vector_b = direction_point[0] - start_point[0], direction_point[1] - start_point[1]
        vector_c = destination_point[0] - start_point[0], destination_point[1] - start_point[1]

        length_a = sqrt(pow(vector_a[0], 2) + pow(vector_a[1], 2))
        length_b = sqrt(pow(vector_b[0], 2) + pow(vector_b[1], 2))
        length_c = sqrt(pow(vector_c[0], 2) + pow(vector_c[1], 2))

        # Angle between the current direction and the direction to the goal point in degrees.
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
        self._console += delimiter + line

    def _clean_console(self):
        """
        Clean the current console commands
        """
        self._console2 = self._console
        self._console = ""

    def add_to_qr_nr(self):
        """
        Adds 1 to the nr of executed qr commands
        """
        self._nr_exec_qr += 1

    def _clean_qr_exec_nr(self):
        """
        Resets the current nr of executed qr commands
        """
        self._nr_exec_qr2 = self._nr_exec_qr
        self._nr_exec_qr = 0

    def add_command(self, command):
        """
        Adds an command to the command handler to be executed
        """
        self._command_controller.add_to_queue(command)

    def take_picture(self):
        """
        Take a picture with the camera
        """
        self._camera.take_picture()
        return self._camera.get_last_picture()

    def take_picture_from_file(self):
        """
        Take a picture from the dir
        """
        return self._camera.take_picture_from_file()

    def take_parse_picture(self):
        """
        Takes a picture (dir or camera depending on the flag) and parses it
        """
        return self._qr_parser.take_picture()

    def quit_core(self):
        """
        Stops everything, console output still available. Zeppelin "lands"; Quit server should be called after this
        """

        self._command_controller.stop_command_control()

        # Lands the zeppelin (they like that!)
        self.set_goal_height(ground_height)
        while self.get_height() > (ground_height + 1):
            sleep(1)
        self.set_height_control(False)

        self._sensor.stop()
        self._motors.stop()
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "The core has gracefully quited")

    def quit_server(self):
        """
        Quits the server; this should be called as last function AFTER quit_core
        """
        self._server.stop_server()

    def _start_server(self):
        """
        Initialises everything to start the server
        """
        self._handler = CoreHandler(self)
        self._server = PIServer(self._handler, self)
        self._server.start_server()

# ------------------------------------------ Getters -------------------------------------------------------------------
    def get_console_output(self):
        """
        Returns the console text
        """
        self._clean_console()
        return self._console2

    def get_qr_exec_nr(self):
        """
        Returns the nr of executed commands (as string)
        """
        self._clean_qr_exec_nr()
        return self._nr_exec_qr2

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
        # TODO

    def get_direction(self):
        """
        Returns a point in front of the current position  of the zeppelin in (x,y) coordinates
        """
        # TODO

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

    def get_last_qr_code(self):
        """
        Returns the last picked QR code from the last taken picture
        """
        return self._qr_parser.get_last_qr()

    def get_last_qr_code_raw(self):
        """
        Returns all the decoded QR codes from the last take picture
        """
        return self._qr_parser.get_last_qr_raw()

    def get_current_command(self):
        """
        Returns the command that is currently executed by the command controller
        """
        return self._command_controller.get_command()

    def get_last_picture(self):
        """
        Returns the last taken picture as pil object
        """
        return self._camera.get_last_picture()

    def get_last_qr_number(self):
        """
        Returns the number of the last parsed qr code
        """
        return self._qr_parser.get_last_number()

    def get_last_qr_pil(self):
        """
        Returns the last parsed qr code, encoded as a new qr code (pil object is returned)
        """
        return self._qr_parser.get_last_qr_pil()

    def get_camera_mode(self):
        """
        Returns the current camera mode flag
        """
        return self._camera_mode_flag

    def get_auto_mode(self):
        """
        Returns the current auto mode flag
        """
        return self._auto_mode_flag

    def get_height_mode(self):
        """
        Returns the current height mode flag
        """
        return self._stay_on_height_flag

# ---------------------------------------------- SETTERS --------------------------------------------------------------

    def set_picture_mode(self, flag):
        """
        Changes the picture mode to the given argument (boolean, no check)
        """
        if flag is True:
            self._camera_mode_flag = True
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Camera mode set to normal")
        else:
            self._camera_mode_flag = False
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Camera mode set to read from dir")

    def set_auto_mode(self, mode):
        """
        Changes the mode of the zeppelin to auto or manual, no check on given argument (must be boolean)
        """
        if mode:
            self._auto_mode_flag = True
            self._command_controller.start_command_control()
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Autonomous mode is activated")

            # Searches for qr codes as long as there are  none found or the and auto mode is on
            while self._auto_mode_flag & (self.take_parse_picture() is None):
                sleep(1)

        else:
            self._auto_mode_flag = False
            self._command_controller.stop_command_control()
            self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Manual mode is activated")

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

    def set_goal_position(self, new_position):
        """
        Sets a new position in (x,y)- coordinates
        """
        self._goal_height = new_position

    def set_navigation_mode(self, flag):
        if flag:
            self._stay_on_position_flag = True
            Thread(target=self._navigation_thread()).start()
        else:
            self._stay_on_position_flag = False

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    core = Core()
    core.add_to_console("Welcome to the zeppelin of TEAM GEEL")
    core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "The core on the raspberry pi has started")
    core.initialise()
    core._goal_height = 50

# ---------------------------------------------------------------------------------------------------------------------