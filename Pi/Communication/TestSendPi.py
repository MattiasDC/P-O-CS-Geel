from SenderPi import *
from ReceiverGUI import *
from SenderGUI import *
from ReceiverPi import *
from threading import Thread
from time import sleep
import Simulator

sender = SenderPi()

sender.sent_position(1,2)
sleep(1)
sender.sent_height(3)
sleep(1)
sender.sent_private("test")