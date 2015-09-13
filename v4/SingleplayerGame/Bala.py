#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Bala.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import pygame
from math import sin
from math import cos
from math import radians

from pygame.sprite import Sprite

VELOCIDAD = 10


class Bala(Sprite):

    def __init__(self, bdict, image_path, res, _id):

        Sprite.__init__(self)

        self._id = _id
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        self._angulo = bdict["a"]
        self._res = res
        self._dx, self._dy = self.__get_vector(self._angulo)
        self.rect.centerx = bdict["x"] + self._dx
        self.rect.centery = bdict["y"] + self._dy

    def __get_vector(self, angulo):
        dx = int(cos(radians(angulo)) * VELOCIDAD)
        dy = int(sin(radians(angulo)) * VELOCIDAD)
        return dx, dy

    def update(self):
        x = self.rect.centerx + self._dx
        y = self.rect.centery + self._dy
        if x > 0 and x < self._res[0] and y > 0 and y < self._res[1]:
            self.rect.centerx = x
            self.rect.centery = y
        else:
            for g in self.groups():
                g.remove(self)
            self.kill()
            return False
