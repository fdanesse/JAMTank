#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from math import sin
from math import cos
from math import radians

from pygame.sprite import Sprite

VELOCIDAD = 18


class Bala(Sprite):

    def __init__(self, bdict, image_path, res, ip):

        Sprite.__init__(self)

        self.ip = ip
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        self._angulo = bdict["a"]
        self._res = res
        self._dx, self._dy = self.__get_vector(self._angulo)
        self._temp_x = bdict["x"] + self._dx
        self._temp_y = bdict["y"] + self._dy
        self.rect.centerx = self._temp_x
        self.rect.centery = self._temp_y

    def __get_vector(self, angulo):
        dx = int(cos(radians(angulo)) * VELOCIDAD)
        dy = int(sin(radians(angulo)) * VELOCIDAD)
        return dx, dy

    def get_datos(self):
        return {"a": self._angulo, "x": self._temp_x, "y": self._temp_y}

    def set_posicion(self, centerx=0, centery=0):
        self.rect.centerx = centerx
        self.rect.centery = centery
        if centerx > 0 and centerx < self._res[0] and \
            centery > 0 and centery < self._res[1]:
                return True
        else:
            for g in self.groups():
                g.remove(self)
            self.kill()
            return False

    def update(self, myip):
        """
        Solo bala de jugador local.
        """
        if myip == self.ip:
            x = self.rect.centerx + self._dx
            y = self.rect.centery + self._dy
            self._temp_x = int(x)
            self._temp_y = int(y)
