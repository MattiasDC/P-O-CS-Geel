import pika
from values import *

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
        self.connected = True

    #Close the connection (also sets the connected-flag to true)
    #Must be called when program stops
    def close_connection(self):
        self._connection.close()
        self._connected = False

    #Receive all the positions of the team determined by the parameter
    #Infinite loop, so must be run in a separate thread
    def receive(self):
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


#Determines the behavior when a message is received
#Still to be determined
def callback(ch, method, properties, body):
    print 'boodschap ontvangen'
    print body




