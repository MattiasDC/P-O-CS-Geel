import pika
from values import *

#!!!!!Messages sent to an exchange with no receiver attached, will be lost!!!!!
#!!!!Be careful with threads: calling a send-function more than once simultaneously results in an error!!!!
#!!!! => make a new sender for each thread!!!!

#To use this class, just make an object and call the appropriate method
class SenderGUI(object):
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
        print host
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

    #Sent a command to move to a new positions (determined by the parameters) to the sever
    def move_command(self, x, y):
        if not self._connected:
             #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the message in format <x>,<y> to the exchange with our routing key
            routing_key = team + '.hcommand.move'
            message = str(int(x)) + ',' + str(int(y))
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a command to move to a new positions (determined by the parameters) to the sever
    def height_command(self, z):
        if not self._connected:
             #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            #Publish the message in format <z> to the exchange with our routing key
            routing_key = team + '.hcommand.elevate'
            message = str(int(z))
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a command to turn motor3 on/of, pwm-value determined by the parameter
    #Not used
    def motor1_command(self, value):
        if not self._connected:
             #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            routing_key = team + '.lcommand.motor1'
            message = str(value)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a command to turn motor3 on/of, pwm-value determined by the parameter
    #Not used
    def motor2_command(self, value):
        if not self._connected:
             #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            routing_key = team + '.lcommand.motor2'
            message = str(value)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'

    #Sent a command to turn motor3 on/of, pwm-value determined by the parameter
    #Not used
    def motor3_command(self, value):
        if not self._connected:
             #No connection to a server, so the message can not be delivered
            return 'Not connected'
        else:
            routing_key = team + '.lcommand.motor3'
            message = str(value)
            self._channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=message)
            return 'succes'





