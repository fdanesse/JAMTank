#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Enemigo.py por:
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

import gobject
import pygame
from math import sin
from math import cos
from math import degrees
from math import atan2
from math import radians
import random
random.seed()

from pygame.sprite import Sprite

VELOCIDAD = 5
INDICE_ROTACION = 5


class Enemigo(gobject.GObject, Sprite):

    __gsignals__ = {
    "disparo": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, [])}

    def __init__(self, res, tank, _id):

        gobject.GObject.__init__(self)
        Sprite.__init__(self)

        self._id = _id
        self._brain = tank[1]
        self._estado = "activo"
        self._res = res
        self._imagen_path = tank[0]
        self._eventos = []
        self._disparos_activos = True
        self._tanque_objetivo = False

        imagen = pygame.image.load(self._imagen_path)
        self._imagen_original = pygame.transform.scale(
            imagen, (40, 40)).convert_alpha()

        self.image = self._imagen_original.copy()
        self.rect = self.image.get_rect()

        self._angulo = random.randrange(0, 360, 1)
        self.centerx = random.randrange(40, self._res[0] - 40, 1)
        self.centery = random.randrange(40, self._res[1] - 40, 1)
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery
        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)
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
        ancho = range(20, self._res[0] - 20)
        alto = range(20, self._res[1] - 20)
        if x in ancho and y in alto:
            self.centerx = int(self.centerx + self._dx)
            self.centery = int(self.centery + self._dy)
            self.rect.centerx = self.centerx
            self.rect.centery = self.centery

    def __reactivar_disparos(self):
        self._disparos_activos = True
        return False

    def __pensar_decidir(self):
        self._eventos = []
        x2 = self._tanque_objetivo.rect.centerx
        y2 = self._tanque_objetivo.rect.centery
        x1, y1 = self.rect.centerx, self.rect.centery
        # http://www.vitutor.com/geo/rec/d_4.html
        angulo = int(degrees(atan2(y2 - y1, x2 - x1)))
        if angulo < 0:
            angulo = 360 + angulo
        if angulo > 360:
            angulo = 360 - angulo

        # movimientos
        eventos = [[], [], []]
        if self._brain in range(0, 4):
            # Modo persecución, con velocidad incremental
            if self._brain == 3:
                eventos = []
            else:
                eventos = eventos[0:3-self._brain]
            if angulo < self._angulo:
                eventos.append(["a", "w"])
            elif angulo > self._angulo:
                eventos.append(["d", "w"])
        elif self._brain in range(4, 8):
            # modo estático
            if self._brain == 7:
                eventos = []
            else:
                eventos = eventos[:7-self._brain]
            if angulo < self._angulo:
                eventos.append(["a"])
            elif angulo > self._angulo:
                eventos.append(["d"])
        if eventos:
            self._eventos = random.choice(eventos)

        # disparos
        disparo = random.randrange(1, 101, 1)
        if self._brain in range(0, 2) and disparo < 2:
            self._eventos.append("space")
        elif self._brain in range(2, 7) and disparo < 6:
            self._eventos.append("space")
        elif self._brain == 7 and disparo < 2:
            self._eventos.append("space")

    def update(self):
        if not self._tanque_objetivo:
            for g in self.groups():
                for t in g.sprites():
                    if t._id == 0:
                        self._tanque_objetivo = t
                        break
        if self._estado == "paused":
            return

        self.__pensar_decidir()

        if not self._eventos:
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

        if "space" in self._eventos and self._disparos_activos:
            self._disparos_activos = False
            self.emit("disparo")
            gobject.timeout_add(1000, self.__reactivar_disparos)

    def get_disparo(self):
        x, y = self.__get_vector(self._angulo)
        x += self.rect.centerx
        y += self.rect.centery
        _dict = {
            "a": int(self._angulo),
            "x": x,
            "y": y,
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
        self._angulo = random.randrange(0, 360, 1)
        self.centerx = random.randrange(40, self._res[0] - 40, 1)
        self.centery = random.randrange(40, self._res[1] - 40, 1)
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery
        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)
        self._dx, self._dy = self.__get_vector(self._angulo)
