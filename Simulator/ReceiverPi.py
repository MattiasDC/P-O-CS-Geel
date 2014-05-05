import pika
from values import *
from threading import Thread
from time import sleep

#The core (or simulator) which the callback function must use
_core = None
#The receiver-object for receiving messages
_receiver = None


#Determines the behavior when a message is received (calls the appropriate function in the core/simulator)
#No check on exceptions
def callback(ch, method, properties, body):
    global _core
    if (team + '.hcommand.move') in str(method.routing_key):
        #move-command received
        #position in format <x>,<y>, so parse first the correct values for the correct vales

        body = str(body)
        pos = body.find(',')
        x = body[0:pos]
        y = body[pos+1:len(body)]
        #Set the new goal-position in the core-class
        _core.set_goal_position(int(x), int(y))
        for i in range(0, len(_core._tablets-1)):
            if x==_core.tablets[i][0] and y== _core.tablets[i][1]:
                _core.set_goal_tablet = i+1
                return 'go to tablet'
        _core._our_zeppelin._last_tablet = True
    if (team + '.hcommand.elevate') in str(method.routing_key):
        #Height-command received
        #Set the new goal-height in the core-class
        print 'message received'
        _core.set_goal_height(int(body))
    if (team + '.lcommand') in str(method.routing_key):
        #Low-level command received
        if 'motor1' in str(method.routing_key):
            #Set motor1 at the pwm-value determined by the message
            _core.set_motor1(int(body))
        if 'motor2' in str(method.routing_key):
            #Set motor2 at the pwm-value determined by the message
            _core.set_motor2(int(body))
        if 'motor3' in str(method.routing_key):
            #Set motor3 at the pwm-value determined by the message
            _core.set_motor3(int(body/10.0))


#Run this function (in the core) to start receiving messages
#Starts a new thread (because receiving involves an infinite loop)
def receive(core):
    global _core
    _core = core
    global _receiver
    _receiver = ReceiverPi()
    t = Thread(target=receive_thread)
    sleep(0.1)
    t.start()


#The receiving thread (starts the receive method of the ReceiverPi-class)
def receive_thread():
    global _receiver
    _receiver.receive()

#!!!!!Always put a sleep after making a receiver, otherwise first message can be lost!!!!!
class ReceiverPi(object):
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
       self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, port=5672, credentials=pika.PlainCredentials('geel', 'geel')))
       self._channel = self._connection.channel()
       self._channel.exchange_declare(exchange='exchange',
                         type='topic')
       self._connected = True

    #Close the connection (also sets the connected-flag to true)
    #Must be called when program stops
    def close_connection(self):
        self._connection.close()
        self._connected = False

    #Wait for a new high-level command (infinite loop, so must be run in a separate thread)
    #Difference between commands made in the callback-function
    def receive(self):
        if self._connected:
            result = self._channel.queue_declare(exclusive=True)
            queue_name = result.method.queue
            #Listen to the high-level commands (only of our team)
            self._channel.queue_bind(exchange=exchange,
                           queue=queue_name,
                           routing_key= team + '.hcommand.*')
            #Listen to the low-level commands (only of our team)
            self._channel.queue_bind(exchange=exchange,
                           queue=queue_name,
                           routing_key= team + '.lcommand.*')
            self._channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)
            self._channel.start_consuming()
        else:
            return 'Not connected'







