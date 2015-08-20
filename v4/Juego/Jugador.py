#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
from math import sin
from math import cos
from math import radians

from pygame.sprite import Sprite

VELOCIDAD = 10
INDICE_ROTACION = 5


class Jugador(Sprite):

    def __init__(self, res, ip, tank, nick):

        Sprite.__init__(self)

        self._res = res
        self._imagen_path = tank
        self._nick = nick
        self._ip = ip
        self._eventos = []

        imagen = pygame.image.load(self._imagen_path)
        self._imagen_original = pygame.transform.scale(
            imagen, (50, 50)).convert_alpha()

        self.image = self._imagen_original.copy()
        self.rect = self.image.get_rect()

        self._angulo = 0
        self.centerx = self._res[0] / 2
        self.centery = self._res[1] / 2
        self._dx, self._dy = self.__get_vector(self._angulo)

        self._temp_angulo = 0
        self._temp_x = self._res[0] / 2
        self._temp_y = self._res[1] / 2

    def __derecha(self):
        self._temp_angulo += int(0.7 * INDICE_ROTACION)
        if self._temp_angulo > 360:
            self._temp_angulo = 360 - self._temp_angulo

    def __izquierda(self):
        self._temp_angulo -= int(0.7 * INDICE_ROTACION)
        if self._temp_angulo < 0:
            self._temp_angulo = 360 + self._temp_angulo

    def __adelante(self):
        self._dx, self._dy = self.__get_vector(self._temp_angulo)
        self.__calcular_nueva_posicion()

    def __atras(self):
        x, y = self.__get_vector(self._temp_angulo)
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
            self._temp_x += self._dx
            self._temp_y += self._dy
            self._temp_x = int(self._temp_x)
            self._temp_y = int(self._temp_y)

    def __set_posicion(self, angulo=0, centerx=0, centery=0):
        """
        Actualiza los datos según lo recibido desde el server.
        """
        self._temp_angulo = angulo
        self._temp_x = centerx
        self._temp_y = centery

        self._angulo = angulo
        self.centerx = centerx
        self.centery = centery

        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

        self.image = pygame.transform.rotate(
            self._imagen_original, -self._angulo)

    def get_datos(self):
        """
        Solo Jugador Local.
        """
        _dict = {
            "a": int(self._temp_angulo),
            "x": int(self._temp_x),
            "y": int(self._temp_y),
            "n": self._nick,
            "t": os.path.basename(self._imagen_path)  # tanque
            }
        return _dict

    def update(self, _dict):
        mydict = _dict.get(self._ip, False)
        if mydict:
            self.__set_posicion(
                angulo=mydict.get("a", 0),
                centerx=mydict.get("x", 0),
                centery=mydict.get("y", 0))
        else:
            self.kill()

    def update_events(self, eventos):
        """
        Solo Jugador Local.
        """
        self._eventos = list(eventos)

    def process_events(self):
        """
        Solo Jugador Local.
        """
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
