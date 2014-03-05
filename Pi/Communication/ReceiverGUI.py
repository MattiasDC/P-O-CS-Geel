import pika
from values import *
from threading import Thread
from time import sleep


#The GUI-object which the callback-function must use
_GUI = None
#The receiver-object for receiving messages
_receiver = None

#Determines the behavior when a message is received (calls the appropriate method of the GUI)
#No check on exceptions
def callback(ch, method, properties, body):
    print 'boodschap ontvangen'
    if 'height' in method.routing_key:
        #Height updated
        print 'hoogte'
        print body
    if 'location' in method.routing_key:
        #Location updated
        print 'positie'
        print body
    if 'private' in method.routing_key:
        #Private message received
        print 'private'
        print body


#Run this function to start receiving messages
#Starts a new thread (because receiving involves an infinite loop)
def receive(GUI):
    global _GUI
    _GUI = GUI
    global _receiver
    _receiver = ReceiverGUI()
    t = Thread(target=receive_thread)
    sleep(0.1)
    t.start()


#The receiving thread (starts the receive method of the ReceiverPi-class)
def receive_thread():
    global _receiver
    _receiver.receive()

#!!!!!Always put a sleep after making a receiver, otherwise first message can be lost!!!!!
class ReceiverGUI(object):
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
        host=host))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange='exchange',
                         type='topic')
        self._connected = True

    #Close the connection (also sets the connected-flag to true)
    #Must be called when program stops
    def close_connection(self):
        self._connection.close()
        self._connected = False

    #Receive all the messages for the GUI published to the server
    #Infinite loop, so must be run in a separate thread
    def receive(self):
        if self._connected:
            result = self._channel.queue_declare(exclusive=True)
            queue_name = result.method.queue
            #Receive all the public information (height + position)
            self._channel.queue_bind(exchange=exchange,
                           queue=queue_name,
                           routing_key='*.info.*')
            #Receive all the private information of our team
            self._channel.queue_bind(exchange=exchange,
                           queue=queue_name,
                           routing_key= team + '.private.#')
            self._channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)
            self._channel.start_consuming()
        else:
            return 'Not connected'






