import time
from datetime import datetime
from threading import Thread
from time import sleep
from copy import deepcopy

import RPi.GPIO as GPIO
from values import *


GPIO.setmode(GPIO.BCM)
# --------------------------------------------------------------------- Variables

_current_height = 0             # Current height
_prev_height = 0                # The previous current height
_enabled = False                # enables or disables the threading

_core_set = False               # Boolean to check if the core is already set
_core = None                    # Core corresponding to this sensor (to push console output)


def initialise(core):
    """ Sets the core of this sensor """
    # Input is not checked!!
    global _core, _core_set
    _core = core
    _core_set = True

def _get_height_list():
    measurements = []
    for i in range(samples):
        distance = _measure_height()
        if distance > 0:
            measurements.append(distance)
    return measurements


def _measure_height():
    """ Measures once the height """

    # Trigger trig_gpio for trig_duration
    GPIO.output(trig_gpio, True)
    sleep(trig_duration)
    GPIO.output(trig_gpio, False)

    # Wait for the echo signal (or timeout)
    countdown_high = inttimeout
    while (GPIO.input(echo_gpio) == 0) and (countdown_high > 0):
        countdown_high -= 1

    # If we've gotten a signal
    if countdown_high > 0:
        echo_start = time.time()

        countdown_low = inttimeout
        while (GPIO.input(echo_gpio) == 1) and (countdown_low > 0):
            countdown_low -= 1
        echo_end = time.time()

        echo_duration = echo_end - echo_start

        # Display the distance, unless there was a timeout on
        # the echo signal
        if countdown_high > 0 and countdown_low > 0:
            # echo_duration is in seconds, so multiply by speed
            # of sound.  Divide by 2 because of round trip and
            # multiply by 100 to get cm instead of m.
            result = echo_duration * v_snd * 100 / 2
            if result >= 2:
                return result

    return -1


def _measure_height_thread():
    """  Measures the distance every second and updates the distance (mean of last # _samples) """

    global _current_height, _enabled, _prev_height

    while _enabled:
        list = _get_height_list()
        if len(list) > samples / 2:
            sorted_list = deepcopy(list)
            sorted_list.sort()
            _prev_height = _current_height
            _current_height = sum(sorted_list[samples / 4:len(sorted_list) - samples / 4]) / \
                              (len(sorted_list) - samples / 2)
        sleep(interval)


def stop():
    """ Stops the distance sensor """
    global _enabled

    _enabled = False
    sleep(0.5)             # Sensor can still be expecting a return value; this makes sure the signal has been received
    GPIO.setup(trig_gpio, GPIO.IN)
    _core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Distance sensor stopped successfully")


def start():
    """
    Starts the distance sensor and measuring thread
    """
    global _enabled, _core, _core_set

    if _core_set:
            GPIO.setup(echo_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(trig_gpio, GPIO.OUT)
            GPIO.output(trig_gpio, False)

            _enabled = True
            Thread(target=_measure_height_thread).start()
            _core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] "
                                 + "Distance sensor is started successfully")

# ---------------------------------------------- GETTERS --------------------------------------------------------------

def get_status():
    global _enabled
    return _enabled

def get_height():
    """ Returns the current height  """
    return _current_height