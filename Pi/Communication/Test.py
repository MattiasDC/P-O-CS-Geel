from SenderPi import *
from ReceiverGUI import *
from SenderGUI import *
from ReceiverPi import *
from threading import Thread
from time import sleep

sender = SenderPi(None)
receiver = ReceiverGUI()

def receive_thread():
    receiver.receive()

Thread(target=receive_thread).start()

sleep(0.1)

sender.sent_position(1,2)








