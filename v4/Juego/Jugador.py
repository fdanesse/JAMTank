#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        #self._ip = ip
        self.eventos = []

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

        #self.__set_posicion(angulo=0, centerx=self._temp_x, centery=self._temp_y)

    '''
    def __derecha(self):
        self._temp_angulo += int(0.7 * INDICE_ROTACION)

    def __izquierda(self):
        self._temp_angulo -= int(0.7 * INDICE_ROTACION)

    def __adelante(self):
        self._dx, self._dy = self.__get_vector(self._temp_angulo)
        self.__actualizar_posicion()

    def __atras(self):
        x, y = self.__get_vector(self._temp_angulo)
        self._dx = x * -1
        self._dy = y * -1
        self.__actualizar_posicion()
    '''

    def __get_vector(self, angulo):
        """
        Recibe un ángulo que da orientación al tanque.
        Devuelve el incremento de puntos x,y en su desplazamiento.
        """
        radianes = radians(angulo)
        x = int(cos(radianes) * VELOCIDAD)
        y = int(sin(radianes) * VELOCIDAD)
        return x, y
    '''

    def __actualizar_posicion(self):
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
        return (int(self._temp_angulo), int(self._temp_x), int(self._temp_y))

    def update_data(self, tanque, angulo=0, centerx=0, centery=0):
        if self.imagen_path != tanque:
            self.imagen_path = tanque
            imagen = pygame.image.load(self.imagen_path)
            imagen_escalada = pygame.transform.scale(imagen, (50, 50))
            self._imagen_original = imagen_escalada.convert_alpha()
            self.image = self._imagen_original.copy()
            self.rect = self.image.get_rect()
        self.__set_posicion(angulo=angulo, centerx=centerx, centery=centery)

    def update_events(self, eventos):
        """
        Solo Jugador Local.
        """
        self.eventos = list(eventos)

    def update(self):
        """
        Solo Jugador Local.
        """
        if not self.eventos:
            return

        # girar en movimiento
        if "w" in self.eventos and "d" in self.eventos:
            self.__adelante()
            self.__derecha()
        elif "w" in self.eventos and "a" in self.eventos:
            self.__adelante()
            self.__izquierda()
        elif "s" in self.eventos and "d" in self.eventos:
            self.__atras()
            self.__izquierda()
        elif "s" in self.eventos and "a" in self.eventos:
            self.__atras()
            self.__derecha()

        # moverse sin girar
        elif "w" in self.eventos:
            self.__adelante()
        elif "s" in self.eventos:
            self.__atras()

        # girar sin moverse
        elif "d" in self.eventos:
            self.__derecha()
        elif "a" in self.eventos:
            self.__izquierda()
    '''
