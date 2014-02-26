import pika
from values import *

class SenderPi(object):
    #Flag to determine if the sender is connected to a server
    _connected = False
    #The connection used by the sender
    _connection = None
    #The channel of the connection used by the sender
    _channel = None

    #Initialise the sender (open the connection)
    def __init__(self):
        self.open_connection()

    #Open a connection to the server (also sets the connected-flag to true)
    def open_connection(self):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=exchange,
                             type='topic')
        self._connected = True

    #Close the connection (also sets the connected-flag to true)
    #Must be called when program stops
    def close_connection(self):
        self._connection.close()
        self._connected = False


    #Sent an updated position (determined by the parameters) to the sever
    def sent_position(self, x, y):
        if not self._connected:
            #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the message in format <x>,<y> to the exchange with our routing key
            routing_key = 'geel.info.location'
            message = str(x) + ',' + str(y)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent an updated height (determined by the parameters) to the sever
    def sent_height(self, z):
        if not self._connected:
            #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the message in format <z> to the exchange with our routing key
            routing_key = 'geel.info.height'
            message = str(z)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a private message to the server
    #Exact formatting must still be determined
    #!!!!!Only ASCII-signs in message!!!!!
    def sent_private(self, message):
        if not self._connected:
            #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            routing_key = 'geel.private'
            message = str(message)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

	