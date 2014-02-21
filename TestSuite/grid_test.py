from os import remove

import Grid
from Shapes import *



#-----------------------------------------------------------------------------
# get_point tests
#-----------------------------------------------------------------------------
def test_get_point():
    """
    Test the get point method of the Grid class.
    """
    grid = Grid([[("red", "heart"), ("green", "oval")],
                 [("blue", "square"), ("white", "star")]])

    assert isinstance(grid.get_point(x=0, y=0), Heart)
    assert grid.get_point(x=0, y=0).color == "red"
    assert isinstance(grid.get_point(x=1, y=0), Ellipse)
    assert grid.get_point(x=1, y=0).color == "green"
    assert isinstance(grid.get_point(x=0, y=1), Rectangle)
    assert grid.get_point(x=0, y=1).color == "blue"
    assert isinstance(grid.get_point(x=1, y=1), Star)
    assert grid.get_point(x=1, y=1).color == "white"


#-----------------------------------------------------------------------------
# From empty tests
#-----------------------------------------------------------------------------
def test_from_empty16():
    grid = Grid.from_empty(1, 6)

    assert grid.n_columns == 1
    assert grid.n_rows == 6

    for i in range(6):
        assert grid.get_point(x=0, y=i) is None


def test_from_empty61():
    grid = Grid.from_empty(6, 1)

    assert grid.n_columns == 6
    assert grid.n_rows == 1

    for i in range(6):
        assert grid.get_point(x=i, y=0) is None


def test_from_empty55():
    grid = Grid.from_empty(5, 5)

    assert grid.n_columns == 5
    assert grid.n_rows == 5

    for i in range(5):
        for j in range(5):
            assert grid.get_point(x=i, y=j) is None


#-----------------------------------------------------------------------------
# write file tests
#-----------------------------------------------------------------------------
def test_write_file():
    grid = Grid([[("red", "heart"), ("green", "oval")],
                 [("blue", "square"), ("white", "star")]])

    grid.write_to_file("./write_test.txt")

    with open('./write_test.txt', 'r') as test:
        test_str = test.read()
    remove('./write_test.txt')

    assert test_str == "red$heart,green$ellipse;\nblue$rectangle,white$star;\n"


#-----------------------------------------------------------------------------
# read file tests
#-----------------------------------------------------------------------------
def test_read_file1():
    grid = Grid.from_file("./test1.txt")

    assert isinstance(grid.get_point(x=0, y=0), Heart)
    assert grid.get_point(x=0, y=0).color == "red"
    assert isinstance(grid.get_point(x=1, y=0), Ellipse)
    assert grid.get_point(x=1, y=0).color == "green"
    assert isinstance(grid.get_point(x=0, y=1), Rectangle)
    assert grid.get_point(x=0, y=1).color == "blue"
    assert isinstance(grid.get_point(x=1, y=1), Star)
    assert grid.get_point(x=1, y=1).color == "white"


def test_read_file2():
    grid = Grid.from_file("./test2.txt")

    assert isinstance(grid.get_point(x=0, y=0), Heart)
    assert grid.get_point(x=0, y=0).color == "red"
    assert isinstance(grid.get_point(x=1, y=0), Ellipse)
    assert grid.get_point(x=1, y=0).color == "green"
    assert isinstance(grid.get_point(x=0, y=1), Rectangle)
    assert grid.get_point(x=0, y=1).color == "blue"
    assert isinstance(grid.get_point(x=1, y=1), Star)
    assert grid.get_point(x=1, y=1).color == "white"

    assert isinstance(grid.get_point(x=0, y=2), Ellipse)
    assert grid.get_point(x=0, y=2).color == "green"
    assert isinstance(grid.get_point(x=1, y=2), Heart)
    assert grid.get_point(x=1, y=2).color == "red"
    assert isinstance(grid.get_point(x=0, y=3), Star)
    assert grid.get_point(x=0, y=3).color == "white"
    assert isinstance(grid.get_point(x=1, y=3), Rectangle)
    assert grid.get_point(x=1, y=3).color == "blue"


#-----------------------------------------------------------------------------
# is_valid_positions tests
#-----------------------------------------------------------------------------
def test_is_valid_position():
    grid = Grid.from_empty(10, 10)

    assert grid.is_valid_position(0, 0)
    assert grid.is_valid_position(5, 5)
    assert grid.is_valid_position(9, 9)

    assert not grid.is_valid_position(-1, 8)
    assert not grid.is_valid_position(10, 8)

    assert not grid.is_valid_position(8, -1)
    assert not grid.is_valid_position(8, 10)