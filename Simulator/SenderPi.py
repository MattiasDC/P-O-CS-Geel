import pika
from values import *

#!!!!!Messages sent to an exchange with no receiver attached, will be lost!!!!!
#!!!!Be careful with threads: calling a send-function more than once simultaneously results in an error!!!!
#!!!! => make a new sender for each thread!!!!

#To use this class, just make an object and call the appropriate method
class SenderPi(object):
    #Flag to determine if the sender is connected to a server
    _connected = False
    #The connection used by the sender
    _connection = None
    #The channel of the connection used by the sender
    _channel = None
    #The color of the team that uses this Sender
    _color = None

    #Initialise the sender (open the connection and set the related core)
    def __init__(self, color):
        self._color = color
        self.open_connection()

    #Open a connection to the server (also sets the connected-flag to true)
    def open_connection(self):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost', port=5673, credentials=pika.PlainCredentials('geel', 'geel')))
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
            routing_key = self._color + '.info.location'
            message = str(int(x)) + ',' + str(int(y))
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
            routing_key = self._color + '.info.height'
            message = str(int(z))
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a goal position (determined by the parameters) to the sever
    def sent_goal_position(self, x, y):
        if not self._connected:
            #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the message in format <x>,<y> to the exchange with the correct routing key
            routing_key = self._color + '.private.goal_position'
            message = str(int(x)) + ',' + str(int(y))
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a goal height (determined by the parameters) to the sever
    def sent_goal_height(self, z):
        if not self._connected:
            #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the message in format <z> to the exchange with the correct routing key
            routing_key = self._color + '.private.goal_height'
            message = str(int(z))
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent console information to the sever
    def sent_console_information(self, info):
        if not self._connected:
            #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the console-information to the exchange with the correct routing key
            routing_key = self._color + '.private.console'
            message = str(info)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'