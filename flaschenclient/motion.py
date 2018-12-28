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

from .limits import Limits


class Motion(object):
    def __init__(self, limits=Limits()):
        self._rotation_speed = 0
        self._rotation_acceleration = 0

        self._x_velocity = 0
        self._x_acceleration = 0

        self._y_velocity = 0
        self._y_acceleration = 0

        self._zoom_velocity = 0
        self._zoom_acceleration = 0

        self._x_gravity = 0
        self._y_gravity = 0

        self._limits = limits
        self._action_at_limit = None

    def _handle_limit_reached_all(self):

        if self.action_at_limit is None:
            return True

        if self._action_at_limit == "stop_all":
            self._rotation_speed = 0
            self._rotation_acceleration = 0
            self._x_velocity = 0
            self._x_acceleration = 0
            self._y_velocity = 0
            self._y_acceleration = 0
            self._zoom_velocity = 0
            self._zoom_acceleration = 0

        elif self._action_at_limit == "inverse_all":
            self._rotation_speed = -self._rotation_speed
            self._rotation_acceleration = -self._rotation_acceleration
            self._x_velocity = -self._x_velocity
            self._x_acceleration = -self._x_acceleration
            self._y_velocity = -self._y_velocity
            self._y_acceleration = -self._y_acceleration
            self._zoom_velocity = -self._zoom_velocity
            self._zoom_acceleration = -self._zoom_acceleration

        elif self._action_at_limit == "reset_vel_inverse_all":
            self._rotation_speed = 0
            self._rotation_acceleration = -self._rotation_acceleration
            self._x_velocity = 0
            self._x_acceleration = -self._x_acceleration
            self._y_velocity = 0
            self._y_acceleration = -self._y_acceleration
            self._zoom_velocity = 0
            self._zoom_acceleration = -self._zoom_acceleration
        else:
            return False
        return True

    def _handle_limit_reached(self, vel, acc):

        if self.action_at_limit == "stop_single":
            vel = 0
            acc = 0
        elif self.action_at_limit == "inverse_single":
            vel = -vel
            acc = -acc
        elif self.action_at_limit == "reset_vel_inverse_single":
            vel = 0
            acc = -acc

        return vel, acc

    def any_limit_reached(self):
        return self._limits.any_limit_reached()

    def rotate(self, rotation):
        rotation += self._rotation_speed
        rotation = self._limits.check("rot", rotation)

        if self._limits.rot.min_max_reached:
            if not self._handle_limit_reached_all():
                self._rotation_speed, self._rotation_acceleration = self._handle_limit_reached(self._rotation_speed,
                                                                                               self._rotation_acceleration)

        self._rotation_speed += self._rotation_acceleration
        return rotation

    def translate(self, x_offset, y_offset):
        if self._limits.width.min_max_reached or self._limits.height.min_max_reached:
            zoom_vel = 0
        else:
            zoom_vel = int(self._zoom_velocity/2)

        x_offset += self._x_velocity - zoom_vel
        y_offset += self._y_velocity - zoom_vel

        x_offset = self._limits.check("x", x_offset)
        y_offset = self._limits.check("y", y_offset)

        if self._limits.x.min_max_reached:
            if not self._handle_limit_reached_all():
                self._x_velocity, self._x_acceleration = self._handle_limit_reached(self._x_velocity,
                                                                                    self._x_acceleration)

        if self._limits.y.min_max_reached:
            if not self._handle_limit_reached_all():
                self._y_velocity, self._y_acceleration = self._handle_limit_reached(self._y_velocity,
                                                                                    self._y_acceleration)

        self._x_velocity += self._x_acceleration + self._x_gravity
        self._y_velocity += self._y_acceleration + self._y_gravity

        return x_offset, y_offset

    def zoom(self, width, height):
        width_new = width + self._zoom_velocity
        height_new = height + self._zoom_velocity

        self._limits.check("width", width_new)
        self._limits.check("height", height_new)

        # size limit is special -> use last value before min limit and last value before max limit for convenience
        if self._limits.width.min_max_reached or self._limits.height.min_max_reached:
            width_new = width
            height_new = height

            if not self._handle_limit_reached_all():
                self._zoom_velocity, self._zoom_acceleration = self._handle_limit_reached(self._zoom_velocity,
                                                                                          self._zoom_acceleration)
        self._zoom_velocity += self._zoom_acceleration
        return width_new, height_new

    @property
    def rot_vel(self):
        return self._rotation_speed

    @rot_vel.setter
    def rot_vel(self, value):
        self._rotation_speed = value

    @property
    def rot_acc(self):
        return self._rotation_acceleration

    @rot_acc.setter
    def rot_acc(self, value):
        self._rotation_acceleration = value

    @property
    def x_vel(self):
        return self._x_velocity

    @x_vel.setter
    def x_vel(self, value):
        self._x_velocity = value

    @property
    def x_acc(self):
        return self._x_acceleration

    @x_acc.setter
    def x_acc(self, value):
        self._x_acceleration = value

    @property
    def y_vel(self):
        return self._y_velocity

    @y_vel.setter
    def y_vel(self, value):
        self._y_velocity = value

    @property
    def y_acc(self):
        return self._y_acceleration

    @y_acc.setter
    def y_acc(self, value):
        self._y_acceleration = value

    @property
    def z_vel(self):
        return self._zoom_velocity

    @z_vel.setter
    def z_vel(self, value):
        self._zoom_velocity = value

    @property
    def z_acc(self):
        return self._zoom_acceleration

    @z_acc.setter
    def z_acc(self, value):
        self._zoom_acceleration = value

    @property
    def x_gravity(self):
        return self._x_gravity

    @x_gravity.setter
    def x_gravity(self, value):
        self._x_gravity = value

    @property
    def y_gravity(self):
        return self._y_gravity

    @y_gravity.setter
    def y_gravity(self, value):
        self._y_gravity = value

    @property
    def action_at_limit(self):
        return self._action_at_limit

    @action_at_limit.setter
    def action_at_limit(self, value):
        self._action_at_limit = value
