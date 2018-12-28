# -*- mode: python; c-basic-offset: 4; indent-tabs-mode: nil; -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://gnu.org/licenses/gpl-2.0.txt>


class Limit(object):
    def __init__(self, _min=None, _max=None):
        self._min = _min
        self._max = _max

        self._max_reached = False
        self._min_reached = False

    def check(self, value):
        if self._max is not None:
            self._max_reached = value >= self._max
            value = min(value, self._max)
        if self._min is not None:
            self._min_reached = value <= self._min
            value = max(value, self._min)
        return value

    def reset(self):
        self._max_reached = False
        self._min_reached = False

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def max_reached(self):
        return self._max_reached

    @property
    def min_reached(self):
        return self._min_reached

    @property
    def min_max_reached(self):
        return self._min_reached or self._max_reached


class Limits(object):
    def __init__(self):
        self._width = Limit()
        self._height = Limit()
        self._x = Limit()
        self._y = Limit()
        self._rot = Limit()

    def check(self, name, value):
        if name == "width":
            value = self._width.check(value)
        elif name == "height":
            value = self._height.check(value)
        elif name == "x":
            value = self._x.check(value)
        elif name == "y":
            value = self._y.check(value)
        elif name == "rot":
            value = self._rot.check(value)
        else:
            raise Exception("Limit doesn't exists.")

        return value

    def any_limit_reached(self):
        return self._width.min_max_reached or self._height.min_max_reached or \
               self._x.min_max_reached or self._y.min_max_reached or self._rot.min_max_reached

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = Limit(value[0], value[1])

    @property
    def height(self):
        return self._width

    @height.setter
    def height(self, value):
        self._height = Limit(value[0], value[1])

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = Limit(value[0], value[1])

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = Limit(value[0], value[1])

    @property
    def rot(self):
        return self._rot

    @rot.setter
    def rot(self, value):
        self._rot = Limit(value[0], value[1])
