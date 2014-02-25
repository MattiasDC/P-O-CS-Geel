import pika
from values import *


class Sender_GUI(object):
    _connected = False
    _connection = None
    _channel = None

    def __init__(self):
        self.open_connection()

    def open_connection(self):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=exchange,
                             type='topic')
        self._connected = True

    def close_connection(self):
        self._connection.close()
        self._connected = False

    def move_command(self, x, y):
        if not self._connected:
            return 'Not connected'
        else:
            routing_key = 'geel.hcommand.move'
            message = x + ',' + y
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    def height_command(self, z):
        if not self._connected:
            return 'Not connected'
        else:
            routing_key = 'geel.hcommand.elevate'
            message = z
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    def motor1_command(self, value):
        if not self._connected:
            return 'Not connected'
        else:
            routing_key = 'geel.lcommand.motor1'
            message = value
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    def motor2_command(self, value):
        if not self._connected:
            return 'Not connected'
        else:
            routing_key = 'geel.lcommand.motor2'
            message = value
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    def motor3_command(self, value):
        if not self._connected:
            return 'Not connected'
        else:
            routing_key = 'geel.lcommand.motor2'
            message = value
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'





