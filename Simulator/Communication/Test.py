from SenderGUI import *
from ReceiverGUI import *
from threading import Thread
from time import sleep
import Simulator

_sim = Simulator.VirtualZeppelin()
_sim.initialise(curr_pos=(100, 50))
_sim.set_goal_height(130)

sender = SenderGUI()
receiver = ReceiverGUI().receive(_sim)


def receive_thread():
    receiver.receive()


Thread(target=receive_thread).start()
sleep(0.1)
