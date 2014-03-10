from ReceiverGUI import receive
import SenderGUI
from time import sleep
import GUIDummy

_dummy = GUIDummy.GUIDummy()
_sender = SenderGUI.SenderGUI()

receive(_dummy)

while (True):
    c = raw_input('Command')
    if c == 'p':
        x = raw_input('x')
        y = raw_input('y')
        _sender.move_command(x,y)
    if c == 'h':
        h = raw_input('h')
        _sender.height_command(h)



