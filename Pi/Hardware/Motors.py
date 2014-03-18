import math
from datetime import datetime
from time import sleep
import RPi.GPIO as GPIO
from values import *


GPIO.setmode(GPIO.BCM)


class MotorControl(object):
    _motor1 = None      # motor1 = right motor
    _motor2 = None      # motor2 = left motor
    _pwm_motor = None   # motor4 = below

    _core = None

    def __init__(self, core):
        # Arguments not checked
        self._core = core
        self._motor1 = FixedMotor(24, 4, self._core)
        self._motor2 = FixedMotor(17, 23, self._core)
        self._pwm_motor = PWMMotor(10, 11, self._core)

    def stop(self):
        """
        Stops the MotorControl, releases all pins and stops moving
        """
        self._pwm_motor.quit()
        self.stop_moving()
        GPIO.setup(24, GPIO.IN)
        GPIO.setup(4, GPIO.IN)
        GPIO.setup(23, GPIO.IN)
        GPIO.setup(17, GPIO.IN)
        GPIO.setup(10, GPIO.IN)
        GPIO.setup(11, GPIO.IN)
        self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " +
                                  "Motor control successfully stopped all motors")

    def stop_moving(self):
        """
        Stops the current movement of the navigation motors
        """
        self._motor1.stop_moving()
        self._motor2.stop_moving()
        self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " +
                                  "Direction motors have stopped moving")

    def motor1_pwm(self, pwm):
        """
        Let the first motor turn at percentage determined by the PWM-argument
        """

        #If the pwm-value is outside the range [-100,100], adjust it
        if pwm > 100:
            pwm = 100
        if pwm < -100:
            pwm = -100

        #The total duration of one duty cycle
        total_time = 1/software_frequency
        #The duration of the motor-movement in one duty cycle
        up_time = abs(total_time*pwm/100)

        if (pwm >= 0 and pwm <= 100):
            #Let the motor turn for the up_time
            self._motor1.move_counterclockwise()
            sleep(up_time)
             #Stop the motor and sleep for the remaining of the duty_cycle
            self._motor1.stop_moving()
            sleep (total_time-up_time)
        if (pwm < 0 and pwm >= 100):
            #Let the motor turn for the up_time
            self._motor1.move_clockwise()
            sleep(up_time)
             #Stop the motor and sleep for the remaining of the duty_cycle
            self._motor1.stop_moving()
            sleep (total_time-up_time)

    def motor2_pwm(self, pwm):
        """
        Let the first motor turn at percentage determined by the PWM-argument
        """

        #If the pwm-value is outside the range [-100,100], adjust it
        if pwm>100:
            pwm = 100
        if pwm <-100:
            pwm = -100

        #The total duration of one duty cycle
        total_time = 1/software_frequency
        #The duration of the motor-movement in one duty cycle
        up_time = abs(total_time*pwm/100)

        if (pwm >= 0 and pwm <= 100):
            #Let the motor turn for the up_time
            self._motor2.move_counterclockwise()
            sleep(up_time)
            #Stop the motor and sleep for the remaining of the duty_cycle
            self._motor2.stop_moving()
            sleep (total_time-up_time)
        if (pwm < 0 and pwm >= 100):
            #Let the motor turn for the up_time
            self._motor2.move_clockwise()
            sleep(up_time)
            #Stop the motor and sleep for the remaining of the duty_cycle
            self._motor2.stop_moving()
            sleep (total_time-up_time)

    def set_pwm(self, pwm):
        #Controls the PWM-motor
        self._pwm_motor.set_pwm(pwm)

    def get_fixed_motors_status(self):
        """
        Returns the current movement of the navigation motors
        """
        status1 = str(self._motor1.get_status())
        status2 = str(self._motor2.get_status())
        if (status1 == "Error" or status2 == "Error"):
            self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Error")
            return None
        return [status1, status2]

    def get_pwm(self):
        """
        Returns the PWM of the height motor
        """
        return self._pwm_motor.get_pwm()

    def get_motor1_status(self):
        """
        Returns the status of motor1
        """
        return self._motor1.get_status()

    def get_motor2_status(self):
        """
        Returns the status of motor2
        """
        return self._motor2.get_status()

# ----------------------------------------------------------------------------------------------------------------------


class FixedMotor(object):
    _pin1 = None
    _Pin2 = None

    _core = None            # Pointer to the core

    def __init__(self, p1, p2, core):
        # No check on arguments
        self._core = core
        self._pin1 = p1
        self._pin2 = p2

        GPIO.setup(self._pin1, GPIO.OUT)
        GPIO.setup(self._pin2, GPIO.OUT)

    def move_counterclockwise(self):
        """
        Moving the motor backwards
        """
        GPIO.output(self._pin1, 0)
        GPIO.output(self._pin2, 1)
        print "move counterclockwise"

    def move_clockwise(self):
        """
        Moving the motor forwards
        """
        GPIO.output(self._pin1, 1)
        GPIO.output(self._pin2, 0)
        print "moved clockwise"

    def stop_moving(self):
        """
        Stops moving
        """
        GPIO.output(self._pin1, 0)
        GPIO.output(self._pin2, 0)

    def get_status(self):
        """
        Returns the current status of the motor
        """
        if GPIO.input(self._pin1) and not GPIO.input(self._pin2):
            return "Clockwise"
        if not GPIO.input(self._pin1) and GPIO.input(self._pin2):
            return "Counterclockwise"
        if GPIO.input(self._pin1) and GPIO.input(self._pin2):
            return "Error"
        return "Not moving"

# ----------------------------------------------------------------------------------------------------------------------


class PWMMotor(object):

    _pin1 = None                    # Direction pin1
    _Pin2 = None                    # Direction pin2
    _PWM = None                     # PWM handler

    _core = None                    # Pointer to the core
    _current_duty_cycle = 0         # Current duty cycle

    _direction = True

    def __init__(self, p1, p2, core):
        # No check on arguments
        self._core = core
        self._pin1 = p1
        self._pin2 = p2
        GPIO.setup(self._pin1, GPIO.OUT)
        GPIO.setup(self._pin2, GPIO.OUT)
        GPIO.setup(PWM_pin, GPIO.OUT)

        self._PWM = GPIO.PWM(PWM_pin, frequency)
        self.set_direction("up")
        self._PWM.start(0)

    def _set_current_duty_cycle(self, new_cycle):
        """
        Adjudges the cycle (0-100) to the real cycle with minimal PWM correction
        """
        try:
            if new_cycle == 0:
                self._current_duty_cycle = 0
                # Direction is not changed!
            else:
                # Maps the value between 0-100
                new_cycle = math.copysign(min(100, abs(new_cycle)), new_cycle)
                new_cycle = math.copysign(max(0, abs(new_cycle)), new_cycle)
                if new_cycle < 0:
                    self.set_direction("down")
                else:
                    self.set_direction("up")

                #Adjust the pwm-value according to the minimal cycle
                self._current_duty_cycle = int(minimal_cycle + (abs(new_cycle)*percentage_correction)/10)

        except (ValueError, TypeError) as e:
            self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Error on new_cycle " +
                                      str(new_cycle) + " " + str(e))

    def quit(self):
        """
        Shuts down the PWM channel
        """
        self._PWM.ChangeDutyCycle(0)
        self._PWM.stop()
        self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "PWM motor has successfully stopped")

    def set_direction(self, direction="up"):
        """
        Changes the direction of the motor
        """
        # Check on argument not needed
        if direction == "up" or direction == "Up" or direction == "UP" or direction is True:
            GPIO.output(self._pin1, 0)
            GPIO.output(self._pin2, 1)
            self._direction = True
        else:
            GPIO.output(self._pin1, 1)
            GPIO.output(self._pin2, 0)
            self._direction = False

    def set_pwm(self, pwm):
        """
        Changes the current PWM to the given argument (0-100)
        """
        # Check on argument already done in _set_current_duty_cycle
        self._set_current_duty_cycle(pwm)
        self._PWM.ChangeDutyCycle(self._current_duty_cycle)

    def get_pwm(self):
        """
        Returns the current PWM (negative if it is moving down)
        """
        if self._direction:
            return self._current_duty_cycle
        else:
            return -self._current_duty_cycle

# ----------------------------------------------------------------------------------------------------------------------
