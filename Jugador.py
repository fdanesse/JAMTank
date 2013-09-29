#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *

from pygame.sprite import Sprite

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
        
        self.set_posicion(x = self.x, y = self.y)
        
    def update(self, teclas):
        print teclas
        
    def set_posicion(self, x=0, y=0):
        self.rect.centerx = x
        self.rect.centery = y
        