#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from math import sin
from math import cos
from math import radians

import pygame
from pygame.locals import *

from pygame.sprite import Sprite

VELOCIDAD = 10
INDICE_ROTACION = 5

class Jugador(Sprite):

    def __init__(self, imagen_tanque, resolucion):

        pygame.sprite.Sprite.__init__(self)
        
        self.imagen_original = None
        self.image = None
        self.rect = None
        
        imagen = pygame.image.load(imagen_tanque)
        imagen_escalada = pygame.transform.scale(imagen, (50,50))
        self.imagen_original = imagen_escalada.convert_alpha()
            
        self.image = self.imagen_original.copy()
        self.rect = self.image.get_rect()
        
        self.ancho_monitor, self.alto_monitor = resolucion
        self.x = self.ancho_monitor / 2 - self.rect.w / 2
        self.y = self.alto_monitor / 2 - self.rect.h / 2
        
        self.angulo = 0
        self.dx, self.dy = self.get_vector(self.angulo) # distancia en x,y
        
        self.set_posicion(x = self.x, y = self.y)
        
    def update(self, teclas):
        
        # girar en movimiento
        if teclas[pygame.K_UP] and teclas[pygame.K_RIGHT]:
            self.arriba()
            self.derecha()
        elif teclas[pygame.K_UP] and teclas[pygame.K_LEFT]:
            self.arriba()
            self.izquierda()
        elif teclas[pygame.K_DOWN] and teclas[pygame.K_RIGHT]:
            self.abajo()
            self.izquierda()
        elif teclas[pygame.K_DOWN] and teclas[pygame.K_LEFT]:
            self.abajo()
            self.derecha()

        # moverse sin girar
        elif teclas[pygame.K_UP] and not teclas[pygame.K_DOWN]:
            self.arriba()
        elif teclas[pygame.K_DOWN] and not teclas[pygame.K_UP]:
            self.abajo()

        # girar sin moverse
        elif teclas[pygame.K_RIGHT] and not teclas[pygame.K_LEFT]:
            self.derecha()
        elif teclas[pygame.K_LEFT] and not teclas[pygame.K_RIGHT]:
            self.izquierda()
            
    def derecha(self):
        self.angulo += int(0.7 * INDICE_ROTACION)
        self.image = pygame.transform.rotate(self.imagen_original, -self.angulo)
                
    def izquierda(self):
        self.angulo -= int(0.7 * INDICE_ROTACION)
        self.image = pygame.transform.rotate(self.imagen_original, -self.angulo)

    def arriba(self):
        self.dx, self.dy = self.get_vector(self.angulo)
        self.actualizar_posicion()
                
    def abajo(self):
        x, y = self.get_vector(self.angulo)
        self.dx = x * -1
        self.dy = y * -1
        self.actualizar_posicion()
        
    def set_posicion(self, angulo=0, x=0, y=0):
        
        self.angulo = angulo
        self.rect.centerx = x
        self.rect.centery = y
        self.image = pygame.transform.rotate(self.imagen_original, -self.angulo)
        
    def get_vector(self, angulo):
        """
        Recibe un ángulo que da orientación al tanque.
        Devuelve el incremento de puntos x,y en su desplazamiento.
        """
        
        x = int(cos(radians(angulo)) * VELOCIDAD)
        y = int(sin(radians(angulo)) * VELOCIDAD)
        
        return x,y
        
    def actualizar_posicion(self):
        """
        Cambia la posicion del rectangulo.
        Solo se ejecuta si el tanque se mueve hacia adelante o hacia atras.
        No se ejecuta cuando está girando en un mismo lugar.
        """
        
        x = self.x + self.dx
        y = self.y + self.dy

        if x > 0 and x < self.ancho_monitor and y > 0 and y < self.alto_monitor:
            self.x += self.dx
            self.y += self.dy
            self.rect.x = int(self.x) - self.rect.w / 2
            self.rect.y = int(self.y) - self.rect.h / 2
            