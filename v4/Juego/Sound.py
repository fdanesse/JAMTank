#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
import gobject

BASE_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


class Sound(gobject.GObject):

    def __init__(self):

        gobject.GObject.__init__(self)

        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)
        #path = os.path.dirname(BASE_PATH)
        #sound = os.path.join(path, "Audio", "Juego.ogg")
        #self.sound_juego = pygame.mixer.Sound(sound)
        #self.sound_juego.play(-1)

        disparo = os.path.join(BASE_PATH, "Audio", "disparo.ogg")
        self._disparo = pygame.mixer.Sound(disparo)

        explosion = os.path.join(BASE_PATH, "Audio", "explosion.ogg")
        self._explosion = pygame.mixer.Sound(explosion)

    def disparo(self):
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self._disparo)

    def explosion(self):
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self._explosion)

