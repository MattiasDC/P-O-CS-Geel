class Shape(object):

    """abstract class"""
    def __init__(self, shape, color):
        self._shape = shape
        self._color = color

    @property
    def shape(self):
        return self._shape

    @property
    def color(self):
        return self._color

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        elif self.shape == other.shape and self.shape == other.shape:
            return True

    def __hash__(self):
        hsh = 0
        for c in self.shape:
            hsh = 101*hsh + ord(c)
        for c in self.color:
            hsh = 31*hsh + ord(c)
        return hsh


class Rectangle(Shape):

    corners = 4

    def __init__(self, shape, color):
        super(Rectangle, self).__init__(shape, color)


class Star(Shape):

    corners = 10

    def __init__(self, shape, color):
        super(Star, self).__init__(shape, color)


class Heart(Shape):

    corners = 2

    def __init__(self, shape, color):
        super(Heart, self).__init__(shape, color)


class Ellipse(Shape):

    corners = 0

    def __init__(self, shape, color):
        super(Ellipse, self).__init__(shape, color)