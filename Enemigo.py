#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from math import sin
from math import cos
from math import radians

import pygame

from pygame.sprite import Sprite

VELOCIDAD = 10
INDICE_ROTACION = 5

random.seed()


class Enemigo(Sprite):

    def __init__(self, imagen_tanque, resolucion):

        pygame.sprite.Sprite.__init__(self)

        self.contador = 0
        self.eventos = []
        self.imagen_original = None
        self.image = None
        self.rect = None

        imagen = pygame.image.load(imagen_tanque)
        imagen_escalada = pygame.transform.scale(imagen, (50, 50))
        self.imagen_original = imagen_escalada.convert_alpha()

        self.image = self.imagen_original.copy()
        self.rect = self.image.get_rect()

        self.ancho_monitor, self.alto_monitor = resolucion
        self.centerx = self.ancho_monitor / 2
        self.centery = self.alto_monitor / 2

        self.angulo = 0
        # distancia en x,y
        self.dx, self.dy = self.get_vector(self.angulo)

        self.set_posicion(
            centerx=self.centerx,
            centery=self.centery)

    def update(self):

        self.contador += 1

        if self.contador == 15:
            self.contador = 0

            teclas = ["Up", "Down", "Right", "Left", "space"]
            nombre = random.choice(teclas)

            if nombre in teclas and nombre in self.eventos:
                self.eventos.remove(nombre)

            else:
                self.eventos.append(nombre)

        if not self.eventos:
            return

        # girar en movimiento
        if "Up" in self.eventos and "Right" in self.eventos:
            self.arriba()
            self.derecha()

        elif "Up" in self.eventos and "Left" in self.eventos:
            self.arriba()
            self.izquierda()

        elif "Down" in self.eventos and "Right" in self.eventos:
            self.abajo()
            self.izquierda()

        elif "Down" in self.eventos and "Left" in self.eventos:
            self.abajo()
            self.derecha()

        # moverse sin girar
        elif "Up" in self.eventos:
            self.arriba()

        elif "Down" in self.eventos:
            self.abajo()

        # girar sin moverse
        elif "Right" in self.eventos:
            self.derecha()

        elif "Left" in self.eventos:
            self.izquierda()

    def derecha(self):
        self.angulo += int(0.7 * INDICE_ROTACION)
        self.image = pygame.transform.rotate(
            self.imagen_original, -self.angulo)

    def izquierda(self):
        self.angulo -= int(0.7 * INDICE_ROTACION)
        self.image = pygame.transform.rotate(
            self.imagen_original, -self.angulo)

    def arriba(self):
        self.dx, self.dy = self.get_vector(self.angulo)
        self.actualizar_posicion()

    def abajo(self):
        x, y = self.get_vector(self.angulo)
        self.dx = x * -1
        self.dy = y * -1
        self.actualizar_posicion()

    def set_posicion(self, angulo=0, centerx=0, centery=0):

        self.angulo = angulo
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.image = pygame.transform.rotate(
            self.imagen_original, -self.angulo)

    def get_vector(self, angulo):
        """
        Recibe un ángulo que da orientación al tanque.
        Devuelve el incremento de puntos x,y en su desplazamiento.
        """

        radianes = radians(angulo)
        x = int(cos(radianes) * VELOCIDAD)
        y = int(sin(radianes) * VELOCIDAD)

        return x, y

    def actualizar_posicion(self):
        """
        Cambia la posicion del rectangulo.
        Solo se ejecuta si el tanque se mueve
        hacia adelante o hacia atras.
        No se ejecuta cuando está girando en un mismo lugar.
        """

        x = self.centerx + self.dx
        y = self.centery + self.dy

        if x > 0 and x < self.ancho_monitor and \
            y > 0 and y < self.alto_monitor:

            self.centerx += self.dx
            self.centery += self.dy
            self.rect.centerx = int(self.centerx)
            self.rect.centery = int(self.centery)
