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

from PIL import Image, ImageFilter
from .motion import Motion


class ImageWrapper(object):
    def __init__(self, image, motion=Motion(), copy=None):
        self._image = image
        self._motion = motion

        width = 0
        height = 0
        x_offset = 0
        y_offset = 0
        rotation = 0
        layer = 0

        if copy is not None:
            if type(copy).__name__ is not 'ImageWrapper':
                raise Exception("Copy has to be an ImageWrapper object.")
            width = copy.width
            height = copy.height
            x_offset = copy.x_offset
            y_offset = copy.y_offset
            rotation = copy.rotation
            layer = copy.layer

        self._width = width
        self._height = height
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._rotation = rotation
        self._layer = layer

        self._count_frame = 0
        self._count_frame_total = 0

        self._blur_in_frames = 0
        self._blur_out_frames = 0
        self._deinit_started = False

        self._is_gif = False
        self._gif_finished = None
        if image is not None:
            if hasattr(image, 'is_animated'):
                # only gifs have attribute is_animated
                self._is_gif = image.is_animated
                self._nr_frame = image.n_frames
                self._gif_finished = False

    def transform(self, frame):
        frame = frame.resize((self._width, self._height), Image.BILINEAR)
        frame = frame.rotate(self._rotation, Image.BILINEAR)

        if self._blur_in_frames > 0 and self._count_frame_total < self._blur_in_frames and not self._deinit_started:
            strength = int((self._blur_in_frames - self._count_frame_total) * 10 / self._blur_in_frames)
            frame = frame.filter(ImageFilter.BoxBlur(strength))

        if self.blur_out_frames > 0 and self._deinit_started:
            strength = 10 - int((self._blur_out_frames - self._count_frame_total) * 10 / self.blur_out_frames)
            frame = frame.filter(ImageFilter.BoxBlur(strength))

        return frame

    def animate(self):
        self._width, self._height = self._motion.zoom(self._width, self._height)
        self._x_offset, self._y_offset = self._motion.translate(self._x_offset, self._y_offset)
        self._rotation = self._motion.rotate(self._rotation)

        self._count_frame += 1
        self._count_frame_total += 1

    def get_frame(self):
        if self._is_gif:
            self._image.seek(self._count_frame)
            self._gif_finished = False
            if self._count_frame == self._nr_frame - 1:
                # loop is completed -> go to first frame
                self._count_frame = -1
                self._gif_finished = True

        return self._image.convert('RGBA')

    def gif_finished(self):
        return True if self._gif_finished is None else self._gif_finished

    def clear_protruding_area(self, new_img, prev_img):
        # find pixels which were included in previous frame but not in the current one
        # first find upper left corner of area
        if prev_img is None:
            return new_img, self.x_offset, self.y_offset

        x1 = min(prev_img.x_offset, self.x_offset)
        y1 = min(prev_img.y_offset, self.y_offset)

        # find lower right corner of area
        x2 = max(prev_img.x_offset + prev_img.width, self.x_offset + self.width)
        y2 = max(prev_img.y_offset + prev_img.height, self.y_offset + self.height)

        # check if found area is inside of the new_image
        if x1 >= self.x_offset and y1 >= self.y_offset and \
                x2 <= self.x_offset + self.width and y2 <= self.y_offset + self.height:
            return new_img, self.x_offset, self.y_offset

        width = x2 - x1
        height = y2 - y1

        img = Image.new('RGB', (width, height), color='black')

        x = max(0, self.x_offset - prev_img.x_offset)
        y = max(0, self.y_offset - prev_img.y_offset)

        img.paste(new_img, (x, y))

        return img, x1, y1

    def start_deinit(self):
        if not self._deinit_started:
            self._count_frame_total = 0
            self._deinit_started = True

    @property
    def deinit_finished(self):
        return self._deinit_started and self._blur_out_frames == self._count_frame_total

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value < 1:
            value = 1
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value < 1:
            value = 1
        self._height = value

    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset(self, value):
        self._x_offset = value

    @property
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset(self, value):
        self._y_offset = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        value = value % 360
        self._rotation = value

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        self._layer = value

    @property
    def blur_in_frames(self):
        return self._blur_in_frames

    @blur_in_frames.setter
    def blur_in_frames(self, value):
        self._blur_in_frames = value

    @property
    def blur_out_frames(self):
        return self._blur_out_frames

    @blur_out_frames.setter
    def blur_out_frames(self, value):
        self._blur_out_frames = value

