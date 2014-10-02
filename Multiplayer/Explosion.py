#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame

from pygame.sprite import Sprite


class Explosion(Sprite):

    def __init__(self, x, y, dir_path):

        Sprite.__init__(self)

        self.contador = 0
        self.valor = 1

        self.imagenes = []
        archivos = sorted(os.listdir(dir_path))
        for arch in archivos:
            path = os.path.join(dir_path, arch)
            imagen = pygame.image.load(path)
            self.imagenes.append(imagen)

        self.image = self.imagenes[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        #self.sonido_explosion = sonido_explosion
        #self.sonido_explosion.play()

    def update(self):
        self.contador += self.valor
        self.image = self.imagenes[self.contador]
        if self.contador == len(self.imagenes)-1:
            self.valor = -1
        else:
            if self.contador < 1:
                self.kill()
                del(self)
