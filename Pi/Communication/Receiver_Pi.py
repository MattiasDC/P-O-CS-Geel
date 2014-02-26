import pika
from values import *

class Receiver_Pi(object):
    #Flag to determine if the sender is connected to a receiver
    _connected = False
    #The connection used by the receiver
    _connection = None
    #The channel of the connection used by the receiver
    _channel = None

    #Initialise the receiver(open the connection)
    def __init__(self):
        self.open_connection()

    #Open a connection to the server (also sets the connected-flag to true)
    def open_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host))
        self._channel = connection.channel()
        self._channel.exchange_declare(exchange='exchange',
                         type='topic')
        self.connected = True

    #Close the connection (also sets the connected-flag to true)
    #Must be called when program stops
    def close_connection(self):
        self._connection.close()
        self._connected = False

    #Wait for a new high-level command (infinite loop, so must be run in a separate thread)
    #Difference between commands made in the callback-function
    def receive_hcommand(self):
        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        #Listen to the high-level commands
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.hcommand.*')
        #Listen to the low-level commands
        self._channel.queue_bind(exchange=exchange,
                       queue=queue_name,
                       routing_key='geel.lcommand.*')
        self._channel.basic_consume(self._callback_hcommand,
                      queue=queue_name,
                      no_ack=True)
        self._channel.start_consuming()

    #Determines the behavior when a message is receiver
    #Still to be determined
    def _callback_hcommand(ch, method, properties, body):
        print body

