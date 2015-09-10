#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Explosion.py por:
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

import os
import pygame

from pygame.sprite import Sprite


class Explosion(Sprite):

    def __init__(self, x, y, dir_path):

        Sprite.__init__(self)

        self._count = 0
        self._val = 1

        self._imgs = []
        archivos = sorted(os.listdir(dir_path))
        for arch in archivos:
            path = os.path.join(dir_path, arch)
            imagen = pygame.image.load(path)
            self._imgs.append(imagen)

        self.image = self._imgs[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        self._count += self._val
        self.image = self._imgs[self._count]
        if self._count == len(self._imgs) - 1:
            self._val = -1
        else:
            if self._count < 1:
                for g in self.groups():
                    g.remove(self)
                self.kill()
                del(self)
