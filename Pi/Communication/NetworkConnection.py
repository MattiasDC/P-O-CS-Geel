from twisted.web import xmlrpc, server
import xmlrpclib
from twisted.internet import reactor
from datetime import datetime
from threading import Thread
from values import *
import os

class PIServer(object):

    _listening_port = None                      # Listening port
    _core = None                                # Pointer to the core

    def __init__(self, handler, core):
        # No arguments check
        self._handler = handler
        self._core = core
        self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Server initialised successfully")

    def start_server(self):
        """
        Starts the server, sets up the connection
        """
        self._listening_port = reactor.listenTCP(port, server.Site(self._handler))
        Thread(target=reactor.run, args=(False, )).start()
        self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Server has started successfully")

    def stop_server(self):
        if self._listening_port is not None:
            reactor.stop()
            self._listening_port.stopListening()
            self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " +
                                      "Server has stopped successfully")

# ----------------------------------------------------------------------------------------------------------------------


class CoreHandler(xmlrpc.XMLRPC):
    _core = None        # Pointer to the core

    def __init__(self, core):
        xmlrpc.XMLRPC.__init__(self, allowNone=True)
        self._core = core
        self._core.add_to_console("[ " + str(datetime.now().time())[:11] + " ] " + "Handler initialised successfully")

# ----------------------------------------------------- Getters --------------------------------------------------------

    def xmlrpc_get_height(self):
        return self._core.get_height()

    def xmlrpc_get_goal_height(self):
        return self._core.get_goal_height()

    def xmlrpc_get_motor_z_pwm(self):
        return self._core.get_motor_z_pwm()

    def xmlrpc_get_motors_xy_status(self):
        return self._core.get_fixed_motor_status()

    def xmlrpc_get_console_output(self):
        return self._core.get_console_output()

    def xmlrpc_get_motor1_status(self):
        return self._core.get_motor1_status()

    def xmlrpc_get_motor2_status(self):
        return self._core.get_motor2_status()

    def xmlrpc_get_current_command(self):
        return self._core.get_current_command()

# ----------------------------------------------------- Commands -------------------------------------------------------

    def xmlrpc_quit_core(self):
        self._core.quit_core()

    def xmlrpc_quit_server(self):
        self._core.quit_server()

# -------------------------------------------------------- Setters -----------------------------------------------------

    def xmlrpc_set_goal_height(self, height):
        self._core.set_goal_height(height)