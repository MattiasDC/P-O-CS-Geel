from threading import Thread
from time import sleep, time
from datetime import datetime
from math import pow, sqrt, acos, degrees, pi, atan2
import Hardware.Camera as Cam
import QRProcessing.QRProcessing as QRProcessing
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
    _senderPi_goal_position = None
    _senderPi_tablets = None

    _positioner = None              # Positioner

    _last_tablet = False


    _tablets = None
    qr_processor = QRProcessing.QRProcessing()
    _prev_request = None

    _goal_tablet = 1

# ---------------------------------------------------------------------------------------------------------------------
    _stay_on_height_flag = None     # Flag to indicate the zeppelin should stay on the goal height or not.
    _stay_on_position_flag = None   # Flag to indicate the zeppelin should (try) to go to the goal position

    _grid = None                    # The grid

    _current_position = (0, 0)
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

        #Sets the tablets
        self._tablets = []
        with open("grid.csv", 'r') as tablet_file:
            for line in tablet_file.read().split('\n'):
                if (line is ""):
                    pass
                elif not (str(line[0]) is "X" or str(line[0]) is "Y" or str(line[0]) is "B" or str(line[0]) is "R" or str(line[0]) is "G" or str(line[0]) is "W"):
                    self._tablets.append((int(line.split(",")[0]), int(line.split(",")[1])))
        # Start the server
        self._start_server()
        self.set_goal_position((self._tablets[self._goal_tablet][0], self._tablets[self._goal_tablet][1]))
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
            sleep(software_pid_interval)                             # time in seconds

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
    def _navigation_thread_motor1(self):
        """
        SoftwarePWM thread
        Motor 1 is the left motor, motor 2 is the right motor.
        """
        while self._stay_on_position_flag:
            start = self.get_position()
            finish = self.get_goal_position()
            angle_zeppelin_vertical = self.get_angle()
            angle_finish_vertical = self._calculate_vertical_angle(start, finish)
            angle = angle_finish_vertical-angle_zeppelin_vertical
            pid_value = self._pid_moving(start, finish)
            if angle < 0:
                angle += 360
            # The pwm value calculated with the pid method has a maximum and minimum boundary
            # if pid_value > pid_boundary:
            #     pid_value = pid_boundary
            # elif pid_value < -pid_boundary:
            #     pid_value = -pid_boundary
            # print "pid: " + str(pid_value)

            if 0 <= angle <= 45:
                 # Both motors are used forwards
                self.set_motor1(pid_value)
                print "motor1: " + str(pid_value)
                # self.set_motor1(pid_value * (45-angle)/45)
                # print "motor1: " + str(pid_value * (45-angle)/45)
            elif 45 < angle <= 135:
                # Right motor is used forwards, but because left motor is used backwards,
                # power ratio must be taken into account
                self.set_motor1(pid_value * (angle-135) * -1.0/90 * power_ratio)
                print "motor1: " + str(pid_value * (angle-135) * -1.0/90 * power_ratio)
                # self.set_motor1(pid_value * (angle-45) * -1/90)
                # print "motor1: " + str(pid_value * (angle-45) * -1/90)
            elif 135 < angle <= 180:
                # Both motors are used backwards
                self.set_motor1(pid_value * (angle-135) * -1.0/45)
                print "motor1: " + str(pid_value * (angle-135) * -1.0/45)
                # self.set_motor1(pid_value * -1)
                # print "motor1: " + str(pid_value * -1)
            elif 180 < angle <= 225:
                # Both motors are used backwards
                self.set_motor1(-pid_value)
                print "motor1: " + str(-pid_value)
                # self.set_motor1(pid_value * (angle-225) * 1/45)
                # print "motor1: " + str(pid_value * (angle-225) * 1/45)
            elif 225 < angle <= 315:
                # Left motor is used forwards, but because right motor is used backwards,
                # power ratio must be taken into account
                self.set_motor1(pid_value * (angle-315) * 1.0/90)
                print "motor1: " + str(pid_value * (angle-315) * 1.0/90)
                # self.set_motor1(pid_value * (angle-225) * 1/90 * power_ratio)
                # print "motor1: " + str(pid_value * (angle-225) * 1/90 * power_ratio)
            elif 315 < angle <= 360:
                # Both motors are used forwards
                self.set_motor1(pid_value * (angle-315) * 1.0/45)
                print "motor1: " + str(pid_value * (angle-315) * 1.0/45)
                # self.set_motor1(pid_value)
                # print "motor1: " + str(pid_value)
            # elif -45 <= angle < 0:
            #    # Both motors are used forwards
            #    self.set_motor1(pid_value)
            #    print "motor1: " + str(pid_value)
            # elif -135 <= angle < -45:
            #    # Left motor is used forwards, but because right motor is used backwards,
            #    # power ratio must be taken into account
            #    self.set_motor1(pid_value * (angle+135) * 1/90 * power_ratio)
            #    print "motor1: " + str(pid_value * (angle+135) * 1/90 * power_ratio)
            # elif -180 <= angle < -135:
            #    # Both motors are used forwards
            #    self.set_motor1(pid_value * (angle+135) * 1/45)
            #    print "motor1: " + str(pid_value * (angle+135) * 1/45)
            sleep(software_pid_interval)

    def _navigation_thread_motor2(self):
        """
        SoftwarePWM thread
        Motor 1 is the left motor, motor 2 is the right motor.
        """
        while self._stay_on_position_flag:
            start = self.get_position()
            finish = self.get_goal_position()
            angle_zeppelin_vertical = self.get_angle()
            angle_finish_vertical = self._calculate_vertical_angle(start, finish)
            angle = angle_finish_vertical-angle_zeppelin_vertical
            if angle < 0:
                angle += 360
            pid_value = self._pid_moving(start, finish)
            # The pwm value calculated with the pid method has a maximum and minimum boundary
            # if pid_value > pid_boundary:
            #     pid_value = pid_boundary
            # elif pid_value < -pid_boundary:
            #     pid_value = -pid_boundary
            # print "pid: " + str(pid_value)

            if 0 <= angle <= 45:
                # Both motors are used forwards
                self.set_motor2(pid_value * (angle-45) * -1.0/45)
                print "motor2: " + str(pid_value * (angle-45) * -1.0/45)
                # self.set_motor2(pid_value)
                # print "motor2: " + str(pid_value)
            elif 45 < angle <= 135:
                # Right motor is used forwards, but because left motor is used backwards,
                # power ratio must be taken into account
                self.set_motor2(pid_value * (angle-45) * -1.0/90)
                print "motor2: " + str(pid_value * (angle-45) * -1.0/90)
                # self.set_motor2(pid_value * (angle-135) * -1/90 * power_ratio)
                # print "motor2: " + str(pid_value * (angle-135) * -1/90 * power_ratio)
            elif 135 < angle <= 180:
                # Both motors are used forwards
                self.set_motor2(-pid_value)
                print "motor2: " + str(-pid_value)
                # self.set_motor2(pid_value * (angle-135) * -1/45)
                # print "motor2: " + str(pid_value * (angle-135) * -1/45)
            elif 180 < angle <= 225:
                # Both motors are used forwards
                self.set_motor2(pid_value * (angle-225) * 1.0/45)
                print "motor2: " + str(pid_value * (angle-225) * 1.0/45)
                # self.set_motor2(pid_value * -1)
                # print "motor2: " + str(pid_value * -1)
            elif 225 < angle < 315:
                # Left motor is used forwards, but because right motor is used backwards,
                # power ratio must be taken into account
                self.set_motor2(pid_value * (angle-225) * 1.0/90 * power_ratio)
                print "motor2: " + str(pid_value * (angle-225) * 1.0/90 * power_ratio)
                # self.set_motor2(pid_value * (angle-315) * 1/90)
                # print "motor2: " + str(pid_value * (angle-315) * 1/90)
            elif 315 <= angle <= 360:
                # Both motors are used forwards
                self.set_motor2(pid_value)
                print "motor2: " + str(pid_value)
                # self.set_motor2(pid_value * (angle-315)/45)
                # print "motor2: " + str(pid_value * (angle-315)/45)
            else:
                print 'should not happen'
            # elif -45 <= angle < 0:
            #    # Both motors are used forwards
            #    self.set_motor2(pid_value * (45+angle)/45)
            #    print "motor2: " + str(pid_value * (45+angle)/45)
            # elif -135 <= angle < -45:
            #    # Left motor is used forwards, but because right motor is used backwards,
            #    # power ratio must be taken into account
            #    self.set_motor2(pid_value * (angle+45) * 1/90)
            #    print "motor2: " + str(pid_value * (angle+45) * 1/90)
            # elif -180 <= angle < -135:
            #    # Both motors are used forwards
            #    self.set_motor2(pid_value * -1)
            #    print "motor2: " + str(pid_value * -1)
            sleep(software_pid_interval)

    def _pid_moving(self, start, finish):
        error = self._calculate_distance_between(start, finish)
        integral = (sum(self._prev_errors_soft[1:]) + self._prev_error_soft) * software_pid_interval
        self._prev_errors_soft = self._prev_errors_soft[1:]
        self._prev_errors_soft.append(error)

        derivative = (error - self._prev_error_soft) / pid_interval
        if derivative == 0:
            derivative = self._prev_derivative_soft*0.9
        else:
            self._prev_derivative_soft = derivative

        self._prev_error_soft = error

        print "Error: " + str(error)
        print "Derivative: " + str(derivative)
        print "Integral: " + str(integral)
        return software_pid_error*error + software_pid_integral*0 + software_pid_derivative*derivative

    @staticmethod
    def _calculate_distance_between(start, end):
        vector = end[0] - start[0], end[1] - start[1]
        distance = sqrt(pow(vector[0], 2) + pow(vector[1], 2))
        return distance

    # Gebruiken we niet!
    @staticmethod
    def _calculate_angle(start_point, destination_point, direction_point):
        try:
            vector_a = destination_point[0] - direction_point[0], destination_point[1] - direction_point[1]
            vector_b = destination_point[0] - start_point[0], destination_point[1] - start_point[1]
            vector_c = direction_point[0] - start_point[0], direction_point[1] - start_point[1]

            length_a = sqrt(pow(vector_a[0], 2) + pow(vector_a[1], 2))
            length_b = sqrt(pow(vector_b[0], 2) + pow(vector_b[1], 2))
            length_c = sqrt(pow(vector_c[0], 2) + pow(vector_c[1], 2))

            # Angle between the current direction and the direction to the goal point in degrees.
            angle = degrees(acos((pow(length_b, 2) + pow(length_c, 2) - pow(length_a, 2)) / float(2 * length_b * length_c)))

            cross = vector_b[0] * vector_c[1] - vector_b[1] * vector_c[0]       # Cross product

            if cross < 0:
                angle = 360-angle
            return angle
        except:
            return 1

    @staticmethod
    def _calculate_vertical_angle(start_point, destination_point):
        vector_a = -(destination_point[1] - start_point[1]), destination_point[0] - start_point[0]
        angle = degrees(atan2(vector_a[1], vector_a[0]))
        if angle < 0:
            angle += 360
        return angle

    def _handle_tablets(self):
        distance = self._calculate_distance_between(self.get_position(), self.get_goal_position())
        if distance < distance_threshold:
            if self._last_tablet == True:
                self.land()
                return "zeppelin landed"
            if self._prev_request is None:
                self._prev_request = time()
                self._senderPi_tablets.sent_tablet(self._goal_tablet, self.qr_processor.pub_key)
                self.add_to_console("QR-code requested")
                sleep(1)
            if time() - self._prev_request > 5:
                self._prev_request = None
            self.add_to_console("Take picture for QR-code")
            qr_string = self.qr_processor.decrypt_pil(self._camera.take_picture_pil())
            if not qr_string is None:
                self.add_to_console("QR-code found:" + str(qr_string))
            else:
                self.add_to_console("No QR-code found")
            if not (qr_string is None):
                if str(qr_string.split(":")[0]) == "tablet":
                     #move to tablet
                    tablet_number = int(qr_string.split(":")[1])
                    x = self._tablets[tablet_number-1][0]
                    y = self._tablets[tablet_number-1][1]
                    goal_tablet = tablet_number
                    self.set_goal_position((x, y))
                if str(qr_string.split(":")[0]) == "position":
                    #move to position
                    x = int(qr_string.split(":")[1].split(",")[0])
                    y = int(qr_string.split(":")[1].split(",")[1])
                    self.set_goal_position((x, y))
                    goal_tablet = 0
                    self._last_tablet = True

# -------------------------------------------- Imageprocessing ---------------------------------------------------------
    def _update_position_thread(self):
        while self._stay_on_position_flag:
            pos, direc, angle = self._positioner.find_location(self._camera.take_picture(), False)

            if not (pos is None or direc is None or angle is None):
                self._update_position(pos, direc, angle)
                self._handle_tablets()

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
        #Uncomment for connection with campusnet rabbitMQ
       # Thread(target=ssh_connector.initialise_ssh_connection).start()
        #ReceiverPi.receive(self)
        sleep(0.1)
        self._senderPi_position = SenderPi.SenderPi()
        self._senderPi_height = SenderPi.SenderPi()
        self._SenderPi_Console = SenderPi.SenderPi()
        self._senderPi_direction = SenderPi.SenderPi()
        self._senderPi_goal_position = SenderPi.SenderPi()
        self._senderPi_tablets = SenderPi.SenderPi()

    def land(self):
        """
        Lands the zeppelin and quits heightcontrol
        """
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "The zeppelin started the landing procedure")
        self.set_goal_height(ground_height)
        while self.get_height() > (ground_height+2):
            sleep(1)
        self.set_height_control(False)

    def _update_position(self, (x, y), (q, z), angle):
        """
        Updates the current position, direction and sends it to the server
        """
        self._current_position = (x, y)
        self._current_direction = (q, z)
        self._current_angle = angle
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
        return self._current_position

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
        self._senderPi_goal_position.sent_goal_position(x, y)
        self.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Goal position is set to: " + str((x, y)))

    def set_navigation_mode(self, flag):
        if flag:
            self._stay_on_position_flag = True
            Thread(target=self._update_position_thread).start()
            Thread(target=self._navigation_thread_motor1).start()
            Thread(target=self._navigation_thread_motor2).start()
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
    core.set_goal_height(1000)
    #while True:
        #software_pid_integral = float(raw_input("integral"))
        #software_pid_derivative = float(raw_input("derivative"))
        #software_pid_error = float(raw_input("error"))
        #new_interval = float(raw_input("interval"))
        #software_pid_interval = new_interval
        #core._motors._pid_interval = new_interval
    # core._current_position = (400, 400)
    # for i in Lijst_hoeken:
    #     core._current_angle = i
    #     sleep(15)

# ---------------------------------------------------------------------------------------------------------------------