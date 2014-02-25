import pika
from values import *

class Receiver_Pi(object):
    _connected = False
    _connection = None
    _channel = None

    def __init__(self):
        self.open_connection()

    def open_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host))
        self._channel = connection.channel()
        self._channel.exchange_declare(exchange='exchange',
                         type='topic')
        self.connected = True

    def close_connection(self):
        self._connection.close()
        self._connected = False

    def receive_hcommand(self):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.hcommand.*')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def receive_motor1_command(self):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.lcommand.motor1')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def receive_motor2_command(self):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.lcommand.motor3')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def receive_motor3_command(self):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.lcommand.motor3')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def _callback(ch, method, properties, body):
        return body
