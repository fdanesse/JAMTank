#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
from math import sin
from math import cos
from math import radians

#from Sonido import Motor
from pygame.sprite import Sprite

VELOCIDAD = 10
INDICE_ROTACION = 5


class Jugador(Sprite):

    def __init__(self, imagen_path, resolucion):

        Sprite.__init__(self)

        # FIXME: Motores desactivados, verificar y corregir
        path = os.path.dirname(os.path.dirname(imagen_path))
        #motor1 = os.path.join(path, "Audio", "motor1.mp3")
        motor2 = os.path.join(path, "Audio", "motor2.ogg")
        #self.motor = Motor(motor1)
        #self.motor.connect("endfile", self.__change_motor, motor2)
        disparo = pygame.mixer.Sound(motor2)
        disparo.play(-1)

        self.eventos = []
        self.energia = 100
        self.imagen_original = None
        self.image = None
        self.rect = None

        imagen = pygame.image.load(imagen_path)
        imagen_escalada = pygame.transform.scale(imagen, (50, 50))
        self.imagen_original = imagen_escalada.convert_alpha()

        self.image = self.imagen_original.copy()
        self.rect = self.image.get_rect()

        self.ancho_monitor, self.alto_monitor = resolucion
        self.centerx = self.ancho_monitor / 2
        self.centery = self.alto_monitor / 2

        self.angulo = 0
        # distancia en x,y
        self.dx, self.dy = self.__get_vector(self.angulo)

        self.temp_image = None
        self.temp_angulo = 0
        self.temp_x = self.ancho_monitor / 2
        self.temp_y = self.alto_monitor / 2

    #def __change_motor(self, player, sound):
    #    del(player)
    #    self.motor = Motor(sound)
    #    self.motor.connect("endfile", self.__change_motor, sound)

    def __derecha(self):
        self.temp_angulo += int(0.7 * INDICE_ROTACION)
        # FIXME: Solo util sin la red
        #self.temp_image = pygame.transform.rotate(
        #    self.imagen_original, -self.temp_angulo)

    def __izquierda(self):
        self.temp_angulo -= int(0.7 * INDICE_ROTACION)
        # FIXME: Solo util sin la red
        #self.temp_image = pygame.transform.rotate(
        #    self.imagen_original, -self.temp_angulo)

    def __arriba(self):
        self.dx, self.dy = self.__get_vector(self.temp_angulo)
        self.__actualizar_posicion()

    def __abajo(self):
        x, y = self.__get_vector(self.temp_angulo)
        self.dx = x * -1
        self.dy = y * -1
        self.__actualizar_posicion()

    def __get_vector(self, angulo):
        """
        Recibe un ángulo que da orientación al tanque.
        Devuelve el incremento de puntos x,y en su desplazamiento.
        """
        radianes = radians(angulo)
        x = int(cos(radianes) * VELOCIDAD)
        y = int(sin(radianes) * VELOCIDAD)
        return x, y

    def __actualizar_posicion(self):
        """
        Cambia la posicion del rectangulo.
        Solo se ejecuta si el tanque se mueve hacia adelante o hacia atras.
        No se ejecuta cuando está girando en un mismo lugar.
        """
        x = self.centerx + self.dx
        y = self.centery + self.dy

        if x > 0 and x < self.ancho_monitor and \
            y > 0 and y < self.alto_monitor:

            self.temp_x += self.dx
            self.temp_y += self.dy
            self.temp_x = int(self.temp_x)
            self.temp_y = int(self.temp_y)

    def __set_posicion(self, angulo=0, centerx=0, centery=0):
        """
        Actualiza los datos según lo recibido desde el server.
        """
        self.temp_angulo = angulo
        self.temp_x = centerx
        self.temp_y = centery

        self.angulo = angulo
        self.centerx = centerx
        self.centery = centery

        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

        self.image = pygame.transform.rotate(
            self.imagen_original, -self.angulo)

    def __get_tanques_rects(self, group):
        recs = []
        for jugador in group.sprites():
            if jugador != self:
                recs.append(jugador.rect)
        return recs

    def __check_collision(self, lista):
        rect = pygame.Rect(self.rect.x, self.rect.y,
            self.rect.width + 10, self.rect.height + 10)
        for rectangulo in lista:
            if rect.colliderect(rectangulo):
                return True
        return False

    def get_datos(self):
        # FIXME: Activar y Corregir:
        #rects = self.__get_tanques_rects(self.groups()[0])
        #if rects:
        #    if self.__check_collision(rects):
        #        return (self.angulo, self.centerx, self.centery)
        #    else:
        #        return (self.temp_angulo, self.temp_x, self.temp_y)
        #else:
        #    return (self.temp_angulo, self.temp_x, self.temp_y)
        return (self.temp_angulo, self.temp_x, self.temp_y)

    def update_data(self, angulo=0, centerx=0, centery=0,
        energia=100):
        self.energia = energia
        self.__set_posicion(angulo=angulo, centerx=centerx, centery=centery)

    def update_events(self, eventos):
        self.eventos = eventos

    def update(self):
        if not self.eventos:
            return

        # girar en movimiento
        if "Up" in self.eventos and "Right" in self.eventos:
            self.__arriba()
            self.__derecha()
        elif "Up" in self.eventos and "Left" in self.eventos:
            self.__arriba()
            self.__izquierda()
        elif "Down" in self.eventos and "Right" in self.eventos:
            self.__abajo()
            self.__izquierda()
        elif "Down" in self.eventos and "Left" in self.eventos:
            self.__abajo()
            self.__derecha()

        # moverse sin girar
        elif "Up" in self.eventos:
            self.__arriba()
        elif "Down" in self.eventos:
            self.__abajo()

        # girar sin moverse
        elif "Right" in self.eventos:
            self.__derecha()
        elif "Left" in self.eventos:
            self.__izquierda()
