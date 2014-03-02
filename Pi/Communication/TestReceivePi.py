from SenderPi import *
from ReceiverGUI import *
from SenderGUI import *
from ReceiverPi import *
from threading import Thread
from time import sleep

receiver = ReceiverPi(None)

def receive_thread():
    receiver.receive()

Thread(target=receive_thread).start()