class Shape(object):

    """abstract class for shapes"""
    def __init__(self, color):
        self._color = color

    @property
    def color(self):
        return self._color

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        elif self.color == other.color:
            return True

    def __hash__(self):
        hsh = 0
        for c in self.color:
            hsh = 101*hsh + ord(c)
        return hsh


class Rectangle(Shape):

    corners = 4
    contour = [[0, 0], [0, 8.5], [5.5, 0], [5.5, 8.5]]

    def __init__(self, color):
        super(Rectangle, self).__init__(color)


class Star(Shape):

    corners = 10

    def __init__(self, color):
        super(Star, self).__init__(color)


class Heart(Shape):

    corners = 2

    def __init__(self, color):
        super(Heart, self).__init__(color)


class Ellipse(Shape):

    corners = 0

    def __init__(self, color):
        super(Ellipse, self).__init__(color)