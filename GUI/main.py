import kivy
kivy.require('1.7.2')

from kivy.config import Config
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 800)

from uix.grid_view import GridViewApp

if __name__ == '__main__':
    GridViewApp().run()