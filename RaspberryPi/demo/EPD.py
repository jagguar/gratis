# Copyright 2013 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.


import Image
import re
import os


class EPDError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class EPD(object):

    """EPD E-Ink interface

to use:
  from EPD import EPD

  epd = EPD([path='/path/to/epd'], [auto=boolean])

  image = Image.new('1', epd.size, 0)
  # draw on image
  epd.clear()         # clear the panel
  epd.display(image)  # tranfer image data
  epd.update()        # refresh the panel image - not deeed if auto=true
"""


    PANEL_RE = re.compile('^([A-Za-z]+)\s+(\d+\.\d+)\s+(\d+)x(\d+)\s*$', flags=0)

    def __init__(self, *args, **kwargs):
        self._epd_path = '/dev/epd'
        self._width = 200
        self._height = 96
        self._panel = 'EPD 2.0'
        self._auto = False

        if len(args) > 0:
            self._epd_path = args[0]
        elif 'epd' in kwargs:
            self._epd_path = kwargs['epd']

        if ('auto' in kwargs) and kwargs['auto']:
            self._auto = True

        with open(os.path.join(self._epd_path, 'version')) as f:
            self._version = f.readline().rstrip('\n')

        with open(os.path.join(self._epd_path, 'panel')) as f:
            line = f.readline().rstrip('\n')
            m = self.PANEL_RE.match(line)
            if None == m:
                raise EPDError('invalid panel string')
            self._panel = m.group(1) + ' ' + m.group(2)
            self._width = int(m.group(3))
            self._height = int(m.group(4))

        if self._width < 1 or self._height < 1:
            raise EPDError('invalid panel geometry')


    @property
    def size(self):
        return (self._width, self._height)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def panel(self):
        return self._panel

    @property
    def version(self):
        return self._version

    @property
    def auto(self):
        return self._auto

    @auto.setter
    def auto(self, flag):
        if flag:
            self._auto = True
        else:
            self._auto = False


    def display(self, image):
        if image.mode != "1":
            raise EPDError('only single bit images are supported')

        if image.size != self.size:
            raise EPDError('image size mismatch')

        with open(os.path.join(self._epd_path, 'display'), 'r+b') as f:
            for c in image.tostring():
                b = ((ord(c) * 0x80200802L) & 0x0884422110L) * 0x0101010101L >> 32
                f.write(chr(b & 0xff))

        if self.auto:
            self.update()


    def update(self):
        self._command('U')

    def clear(self):
        self._command('C')

    def _command(self, c):
        with open(os.path.join(self._epd_path, 'command'), 'wb') as f:
            f.write(c)
