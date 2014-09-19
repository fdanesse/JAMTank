#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
from math import sin
from math import cos
from math import radians

from pygame.sprite import Sprite

VELOCIDAD = 18


class Bala(Sprite):

    def __init__(self, angulo, x, y, image_path, resolucion):

        Sprite.__init__(self)

        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        self.angulo = angulo
        self.ancho_monitor, self.alto_monitor = resolucion
        self.dx, self.dy = self.__get_vector(angulo)
        self.temp_x = x + self.dx
        self.temp_y = y + self.dy
        self.rect.centerx = self.temp_x
        self.rect.centery = self.temp_y

        self.sound_path = os.path.dirname(os.path.dirname(image_path))
        sound_path = os.path.join(self.sound_path, "Audio", "disparo.ogg")
        disparo = pygame.mixer.Sound(sound_path)
        disparo.play()

    def __get_vector(self, angulo):
        dx = int(cos(radians(angulo)) * VELOCIDAD)
        dy = int(sin(radians(angulo)) * VELOCIDAD)
        return dx, dy

    def get_datos(self):
        return (self.angulo, self.temp_x, self.temp_y)

    def set_posicion(self, centerx=0, centery=0):
        self.rect.centerx = centerx
        self.rect.centery = centery
        if centerx > 0 and centerx < self.ancho_monitor and \
            centery > 0 and centery < self.alto_monitor:
                return True
        else:
            self.kill()
            return False

    def update(self):
        x = self.rect.centerx + self.dx
        y = self.rect.centery + self.dy
        #if x > 0 and x < self.ancho_monitor and \
        #    y > 0 and y < self.alto_monitor:
        #    self.temp_x = int(x)
        #    self.temp_y = int(y)
        #else:
        #    self.kill()
        self.temp_x = int(x)
        self.temp_y = int(y)
