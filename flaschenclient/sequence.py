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

import time


class Sequence(object):
    def __init__(self):
        self._timeout = 0
        self._ms_between_frames = 100
        self._auto_stop = True
        self._clear_after_exit = True
        self._clear_prot_area = False
        self._stop_loop_at_limit = False

        self._starting_time = None
        self._last_frame_time = None

    def timeout_reached(self):
        if self.total_time_passed() >= self._timeout:
            return True
        return False

    def start(self):
        self._starting_time = time.time()

    def pause(self):
        if self._last_frame_time is not None:
            last_frame_time_passed = self.time_since_last_frame()
            while last_frame_time_passed * 1000 <= self._ms_between_frames:
                time.sleep(0.01)
                last_frame_time_passed = self.time_since_last_frame()
        self._last_frame_time = time.time()

    def total_time_passed(self):
        if self._starting_time is None:
            raise Exception("Sequence must first be started.")
        return time.time() - self._starting_time

    def time_since_last_frame(self):
        if self._last_frame_time is None:
            raise Exception("For measuring time call tick first.")
        return time.time() - self._last_frame_time

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def ms_between_frames(self):
        return self._ms_between_frames

    @ms_between_frames.setter
    def ms_between_frames(self, value):
        self._ms_between_frames = value

    @property
    def auto_stop(self):
        return self._auto_stop

    @auto_stop.setter
    def auto_stop(self, value):
        self._auto_stop = value

    @property
    def clear_after_exit(self):
        return self._clear_after_exit

    @clear_after_exit.setter
    def clear_after_exit(self, value):
        self._clear_after_exit = value

    @property
    def clear_prot_area(self):
        return self._clear_prot_area

    @clear_prot_area.setter
    def clear_prot_area(self, value):
        self._clear_prot_area = value

    @property
    def stop_loop_at_limit(self):
        return self._stop_loop_at_limit

    @stop_loop_at_limit.setter
    def stop_loop_at_limit(self, value):
        self._stop_loop_at_limit = value
