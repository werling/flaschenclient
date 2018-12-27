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

import socket
import io
import _thread
from PIL import Image

from .motion import Motion
from .sequence import Sequence
from .imagewrapper import ImageWrapper
from .limits import Limits


class FlaschenClient(object):
    """ A Framebuffer display interface that sends a get_frame via UDP."""

    def __init__(self, host, port, display_width=0, display_height=0, multi_threading=True, protocol="UDP"):
        """
        Args:
            host: The flaschen taschen server hostname or ip address.
            port: The flaschen taschen server port number.
            display_width: The width of the display in pixels.
            display_height: The height of the display in pixels.
            multi_threading: Use multiple threads for sending images. If False all images will be send sequentially.
        """
        self._protocol = protocol
        self._host = host
        self._port = port
        self._stop = False
        self._nr_threads = 0
        self._connected = False
        self._display_width = display_width
        self._display_height = display_height
        self._multi_threading = multi_threading

        self._sock = self._connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sock.close()

    def send(self, image, width=0, height=0, x_offset=0, y_offset=0, rotation=0, layer=0,
             blur_in_frames=0, blur_out_frames=0,
             timeout=0, ms_between_frames=100, auto_stop=True, clear_after_exit=True, clear_prot_area=True,
             x_vel=0, x_acc=0, y_vel=0, y_acc=0, rot_vel=0, rot_acc=0, zoom_vel=0, zoom_acc=0, x_gravity=0, y_gravity=0,
             action_at_limit=None,
             x_min=None, x_max=None, y_min=None, y_max=None, rot_min=None, rot_max=None,
             width_min=None, width_max=None, height_min=None, height_max=None):
        """
        Send image to display.
        Args:
            image: PIL image to send
            width: The width of the image in pixels. If value is 0, then image.width is used. If value differs from
                image.width, then image will be resized.
            height: The height of the image in pixels. If value is 0, then image.height is used. If value differs from
                image.height, then image will be resized.
            x_offset: Offset of image on display in x-direction in pixels.
            y_offset: Offset of image  on display in y-direction in pixels.
            rotation: Rotation of image in degree.
            layer: The layer of the flaschen taschen display.
            blur_in_frames: Nr of frames the image gets unblurred at the beginning of the animation
            blur_out_frames: Nr of images the image gets blurred at the end of the animation

            timeout: Duration of showing the image or animation.
            ms_between_frames: Time between two frames in ms
            auto_stop: Stops looping if image is not visible anymore. E.g. width < 1 or image is outside display frame.
            clear_after_exit: Clears layer after exiting loop.
            clear_prot_area: Checks after each frame if there are areas from the previous frame which not got cleared
                and clears them. E.g. if the image shrinks over time. Could be processor-intensive.

            x_vel: Velocity of image in pixels per frame in x-direction
            x_acc: Acceleration of image in pixels per frame in x-direction
            y_vel: Velocity of image in pixels per frame in y-direction
            y_acc: Acceleration of image in pixels per frame in y-direction
            rot_vel: Angular velocity of image in degree per frame
            rot_acc: Angular acceleration in degree per frame.
            zoom_vel: Zoom in or out speed. Image width and height get added by 2 of this value in pixels.
            zoom_acc: Zoom in or out acceleration.
            x_gravity: Gravity which act on motion in x-direction in pixels.
            y_gravity: Gravity which act on motion in y-direction in pixels.
            action_at_limit: stop_all: Stops all motion at once
                             stop_single: Stops only the motion which triggered the limit
                             inverse_all: Inverses all motion
                             inverse_single: Inverses only motion which triggered the limit
                             reset_vel_inverse_all: Resets velocity and reversing motion.
                             None: Nothing happens after limit is reached

            x_min: Minimum x position of image
            x_max: Maximum x position of image
            y_min: Minimum y position of image
            y_max: Maximum y position of image
            rot_min: Minimum rotation
            rot_max: Maximum rotation
            width_min: Minimum width
            width_max: Maximum width
            height_min: Minimum height
            height_max: Maximum Height
        """
        limits = Limits()
        limits.x = (x_min, x_max)
        limits.y = (y_min, y_max)
        limits.width = (width_min, width_max)
        limits.height = (height_min, height_max)
        limits.rot = (rot_min, rot_max)

        motion = Motion(limits)
        motion.rot_vel = int(rot_vel)
        motion.rot_acc = int(rot_acc)
        motion.x_vel = int(x_vel)
        motion.x_acc = int(x_acc)
        motion.y_vel = int(y_vel)
        motion.y_acc = int(y_acc)
        motion.z_vel = int(zoom_vel * 2)
        motion.z_acc = int(zoom_acc * 2)
        motion.x_gravity = int(x_gravity)
        motion.y_gravity = int(y_gravity)
        motion.action_at_limit = action_at_limit

        img_wrap = ImageWrapper(image, motion)
        img_wrap.width = image.width if width == 0 else int(width)
        img_wrap.height = image.height if height == 0 else int(height)
        img_wrap.x_offset = int(x_offset)
        img_wrap.y_offset = int(y_offset)
        img_wrap.rotation = int(rotation)
        img_wrap.layer = int(layer)
        img_wrap.blur_in_frames = int(blur_in_frames)
        img_wrap.blur_out_frames = int(blur_out_frames)

        sequence = Sequence()
        sequence.timeout = timeout
        sequence.ms_between_frames = ms_between_frames
        sequence.auto_stop = auto_stop
        sequence.clear_after_exit = clear_after_exit
        sequence.clear_prot_area = clear_prot_area

        self._stop = False
        self._nr_threads += 1

        if self._multi_threading:
            _thread.start_new_thread(self._send_loop, (img_wrap, sequence))
        else:
            self._send_loop(img_wrap, sequence)

    def stop(self):
        self._stop = True

    def clear(self, layer):
        width = 1024
        height = 1024
        img = Image.new('RGB', (width, height), color='black')
        img = self._crop_image_to_display_size(img)[0]
        image_bytes = io.BytesIO()
        img.save(image_bytes, 'png')
        self._socket_send(image_bytes, img.width, img.height, layer)

    def clear_all(self):
        for i in range(0, 15):
            self.clear(i)

    def is_running(self):
        return bool(self._nr_threads > 0)

    def is_connected(self):
        return self._connected

    def _connect(self):
        sock = None
        try:
            if self._protocol == "TCP":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif self._protocol == "UDP":
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                raise Exception("Protocol not supported.")
            sock.connect((self._host, self._port))
        except ConnectionRefusedError:
            print(self._protocol + " Connection refused")
        return sock

    def _send_loop(self, img_wrap, sequence):
        sequence.start()
        prev_image = None
        sock = None

        if self._protocol == "TCP":
            sock = self._connect()

        while True:
            # Main Loop of animation

            # get image or frame of gif
            tmp_image = img_wrap.get_frame()

            # transform image according to given motion
            tmp_image = img_wrap.transform(tmp_image)

            # clear protruding area from last frame
            tmp_x_offset = img_wrap.x_offset
            tmp_y_offset = img_wrap.y_offset
            if sequence.clear_prot_area:
                tmp_image, tmp_x_offset, tmp_y_offset = img_wrap.clear_protruding_area(tmp_image, prev_image)
                prev_image = ImageWrapper(None, copy=img_wrap)

            # crop image to size of display to save some connection
            tmp_image, tmp_x_offset, tmp_y_offset = self._crop_image_to_display_size(tmp_image,
                                                                                     tmp_x_offset, tmp_y_offset)

            # convert to png for allowing bigger image sizes
            image_bytes = io.BytesIO()
            tmp_image = tmp_image.convert('RGB')  # to get sure no alpha channel is used
            tmp_image.save(image_bytes, 'png')

            # keep frame per second rate
            sequence.pause()

            # send image to tcp or udp socket
            success = self._socket_send(image_bytes, img_wrap.layer, tmp_x_offset, tmp_y_offset)

            # main loop stops if:
            # - protocol is tcp and an error occurred
            # - stop is set to true
            # - timeout is reached
            # - auto_stop is true and frame is not visible anymore (e.g. outside the display, too small, etc...)
            if sequence.timeout_reached() or self._stop:
                img_wrap.start_deinit()

            if not success:
                break

            if img_wrap.deinit_finished:
                break

            if sequence.auto_stop:
                if not self._image_is_visible(img_wrap):
                    break

            # calc new transforming parameters
            img_wrap.animate()

        if sequence.clear_after_exit:
            self.clear(img_wrap.layer)

        if self._protocol == "TCP" and sock is not None:
            sock.close()

        self._nr_threads -= 1

    def _crop_image_to_display_size(self, image, x_offset=0, y_offset=0):
        if self._display_width != 0 and self._display_height != 0:
            # get upper left corner of image part inside display
            x1 = min(0, x_offset)
            y1 = min(0, y_offset)

            # get lower right corner of image part inside display
            x2 = min(self._display_width, image.width)
            y2 = min(self._display_height, image.height)

            image = image.crop((0 - x1, 0 - y1, x2 - x1, y2 - y1))

            x_offset = max(0, x_offset)
            y_offset = max(0, y_offset)
        return image, x_offset, y_offset

    def _image_is_visible(self, img_info):
        if img_info.width <= 1 or img_info.height <= 1 or \
                img_info.width > self._display_width*10 or img_info.height > self._display_height*10 or\
                img_info.x_offset > self._display_width or img_info.x_offset < -img_info.width or \
                img_info.y_offset > self._display_height or img_info.y_offset < -img_info.height:
            return False
        return True

    def _socket_send(self, image_bytes, layer, x_offset=0, y_offset=0, sock=None):
        try:
            footer = ("{}\n {}\n {}\n".format(x_offset, y_offset, layer)).encode()

            if sock is None:
                self._sock.send(image_bytes.getvalue() + footer)
            else:
                sock.send(image_bytes.getvalue() + footer)

            self._connected = True
            return True
        except ConnectionRefusedError:
            # if display refused connection -> keep program running (only udp)
            self._connected = False
            print("UDP Server refused connection.")
            return True
        except BrokenPipeError:
            #  Error occurs with TCP -> exits loop and stops program
            self._connected = False
            print("TCP Pipe is broken.")
            return False
        except ConnectionResetError:
            #  Error occurs with TCP -> exits loop and stops program
            self._connected = False
            print("TCP Connection reset by peer")
            return False
