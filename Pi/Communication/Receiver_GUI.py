import pika
from values import *

class Receiver_GUI(object):
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

    def receive_position(self, team):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key=team + '*.info.location')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def receive_height(self, team):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key=team + '*.info.height')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def receive_private(self, team):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.private.#')
        self._channel.basic_consume(self._callback,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    def _callback(ch, method, properties, body):
        return body




