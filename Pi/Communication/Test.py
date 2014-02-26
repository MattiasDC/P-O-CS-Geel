from SenderPi import *
from ReceiverGUI import *
from threading import Thread
from time import sleep

sender = SenderPi()
receiver = ReceiverGUI()

def receive_thread():
    receiver.receive()

Thread(target=receive_thread).start()

print'hier1'
sleep(1)

sender.sent_position(10,5)








