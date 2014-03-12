import kivy
kivy.require('1.8.0')

from kivy.config import Config
Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)

#from uix.properties_view import PropViewApp
#
#if __name__ == '__main__':
#    PropViewApp().run()
#
#from uix.grid_view import GridViewApp
#
#if __name__ == '__main__':
#    GridViewApp().run()
#
from uix.FloatingDutchManApp import FloatingDutchManApp

if __name__ == '__main__':
    FloatingDutchManApp().run()