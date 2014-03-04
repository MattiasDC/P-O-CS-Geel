import numpy as np
from math import sqrt

class Shape(object):

    """abstract class for shapes"""
    def __init__(self, color, center):
        self._color = color
        self._center = center

    def distance_to_other(self, shape):
       return sqrt(abs(self.center[0] - shape.center[0])**2 + abs(self.center[1] - shape.center[1])**2)

    @property
    def color(self):
        return self._color

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center):
        self._center = center

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        elif self.color == other.color and self.center == other.center:
            return True
        return False

    def __hash__(self):
        hsh = 0
        for c in self.color:
            hsh = 101*hsh + ord(c)
        hsh = 31*hsh + self.center[0]
        hsh = 31*hsh + self.center[1]
        return hsh


class Rectangle(Shape):

    corners = 4
    contour = np.asarray([[[236, 1485]], [[253, 1483]], [[471, 1563]], [[470, 1584]], [[418, 1714]], [[405, 1717]],
                          [[181, 1637]], [[180, 1621]]])

    def __init__(self, color, center=None):
        super(Rectangle, self).__init__(color, center)


class Star(Shape):

    corners = 10
    contour = np.asarray([[[1184, 1583]], [[1183, 1670]], [[1262, 1704]], [[1181, 1735]], [[1175, 1820]],
                          [[1123, 1749]], [[1038, 1767]], [[1091, 1696]], [[1047, 1625]], [[1127, 1649]]])

    def __init__(self, color, center=None):
        super(Star, self).__init__(color, center)


class Heart(Shape):

    corners = 2
    contour = np.asarray([[[306, 827]], [[347, 826]], [[373, 839]], [[391, 856]], [[395, 849]], [[425, 837]],
                          [[461, 840]], [[478, 849]], [[494, 869]], [[499, 892]], [[495, 917]], [[478, 952]],
                          [[441, 991]], [[398, 1018]], [[378, 1026]], [[354, 1013]], [[299, 955]], [[277, 910]],
                          [[273, 863]], [[282, 844]]])

    def __init__(self, color, center=None):
        super(Heart, self).__init__(color, center)


class Ellipse(Shape):

    corners = 0
    contour = np.asarray([[[752, 1170]], [[801, 1168]], [[828, 1180]], [[854, 1200]], [[876, 1235]], [[881, 1282]],
                          [[870, 1316]], [[840, 1350]], [[805, 1367]], [[764, 1367]], [[730, 1355]], [[702, 1329]],
                          [[685, 1300]], [[680, 1267]], [[686, 1229]], [[715, 1190]]])

    def __init__(self, color, center=None):
        super(Ellipse, self).__init__(color, center)