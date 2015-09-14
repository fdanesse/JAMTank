#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Jugador.py por:
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

VELOCIDAD = 5
INDICE_ROTACION = 5


class Jugador(Sprite):

    def __init__(self, res, tank, _id):

        Sprite.__init__(self)

        self._id = _id
        self._estado = "activo"
        self._res = res
        self._imagen_path = tank
        self._eventos = []

        imagen = pygame.image.load(self._imagen_path)
        self._imagen_original = pygame.transform.scale(
            imagen, (50, 50)).convert_alpha()

        self.image = self._imagen_original.copy()
        self.rect = self.image.get_rect()

        self._angulo = 0
        self.centerx = self._res[0] / 2
        self.centery = self._res[1] / 2
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery
        self._dx, self._dy = self.__get_vector(self._angulo)

    def __derecha(self):
        self._angulo += int(0.7 * INDICE_ROTACION)
        if self._angulo > 360:
            self._angulo = 360 - self._angulo
        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)

    def __izquierda(self):
        self._angulo -= int(0.7 * INDICE_ROTACION)
        if self._angulo < 0:
            self._angulo = 360 + self._angulo
        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)

    def __adelante(self):
        self._dx, self._dy = self.__get_vector(self._angulo)
        self.__calcular_nueva_posicion()

    def __atras(self):
        x, y = self.__get_vector(self._angulo)
        self._dx = x * -1
        self._dy = y * -1
        self.__calcular_nueva_posicion()

    def __get_vector(self, angulo):
        """
        Recibe un ángulo que da orientación al tanque.
        Devuelve el incremento de puntos x,y en su desplazamiento.
        """
        radianes = radians(angulo)
        x = int(cos(radianes) * VELOCIDAD)
        y = int(sin(radianes) * VELOCIDAD)
        return x, y

    def __calcular_nueva_posicion(self):
        """
        Cambia la posicion del rectangulo.
        Solo se ejecuta si el tanque se mueve hacia adelante o hacia atras.
        No se ejecuta cuando está girando en un mismo lugar.
        """
        x = self.centerx + self._dx
        y = self.centery + self._dy
        ancho = range(25, self._res[0] - 25)
        alto = range(25, self._res[1] - 25)
        if x in ancho and y in alto:
            self.centerx = int(self.centerx + self._dx)
            self.centery = int(self.centery + self._dy)
            self.rect.centerx = self.centerx
            self.rect.centery = self.centery

    def update_events(self, eventos):
        """
        Solo Jugador Local.
        """
        if self._estado == "activo":
            self._eventos = list(eventos)
        elif self._estado == "paused":
            self._eventos = []

    def update(self):
        """
        Solo Jugador Local.
        """
        if not self._eventos or self._estado == "paused":
            return

        # girar en movimiento
        if "w" in self._eventos and "d" in self._eventos:
            self.__adelante()
            self.__derecha()
        elif "w" in self._eventos and "a" in self._eventos:
            self.__adelante()
            self.__izquierda()
        elif "s" in self._eventos and "d" in self._eventos:
            self.__atras()
            self.__izquierda()
        elif "s" in self._eventos and "a" in self._eventos:
            self.__atras()
            self.__derecha()

        # moverse sin girar
        elif "w" in self._eventos:
            self.__adelante()
        elif "s" in self._eventos:
            self.__atras()

        # girar sin moverse
        elif "d" in self._eventos:
            self.__derecha()
        elif "a" in self._eventos:
            self.__izquierda()

    def get_disparo(self):
        _dict = {
            "a": int(self._angulo),
            "x": int(self.rect.centerx),
            "y": int(self.rect.centery),
            }
        return _dict

    def pausar(self):
        self._estado = "paused"
        self.rect.centerx = -200
        self.rect.centery = -200
        self._angulo = 0
        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)

    def reactivar(self):
        self._estado = "activo"
        self.rect.centerx = self._res[0] / 2
        self.rect.centery = self._res[1] / 2
        self._angulo = 0
        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)
