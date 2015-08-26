#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame

from pygame.sprite import Sprite


class Explosion(Sprite):

    def __init__(self, x, y, dir_path):

        Sprite.__init__(self)

        self._count = 0
        self._val = 1

        self._imgs = []
        archivos = sorted(os.listdir(dir_path))
        for arch in archivos:
            path = os.path.join(dir_path, arch)
            imagen = pygame.image.load(path)
            self._imgs.append(imagen)

        self.image = self._imgs[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        self._count += self._val
        self.image = self._imgs[self._count]
        if self._count == len(self._imgs) - 1:
            self._val = -1
        else:
            if self._count < 1:
                for g in self.groups():
                    g.remove(self)
                self.kill()
                del(self)
