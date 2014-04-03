class Shape(object):
    """abstract class for shapes"""
    def __init__(self, color, center, shape):
        self._color = color
        self._center = center
        self._shape = shape

    @property
    def color(self):
        """
        The colour of this shape.
        """
        return self._color

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center):
        self._center = center

    @property
    def shape(self):
        """
        The shape of this shape as string.
        """
        return self._shape

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
    def __init__(self, color, center=None):
        super(Rectangle, self).__init__(color, center, 'Rectangle')


class Star(Shape):
    def __init__(self, color, center=None):
        super(Star, self).__init__(color, center, 'Star')


class Heart(Shape):
    def __init__(self, color, center=None):
        super(Heart, self).__init__(color, center, 'Heart')


class Ellipse(Shape):
    def __init__(self, color, center=None):
        super(Ellipse, self).__init__(color, center, 'Ellipse')