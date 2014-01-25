#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from gi.repository import GObject

import pygame

#from Enemigo import Enemigo

RESOLUCION_INICIAL = (800, 600)
BASE_PATH = os.path.dirname(__file__)

GObject.threads_init()


class Juego(GObject.Object):
    """
    Juego de Batalla entre Tanques.
    """

    __gsignals__ = {
        "update": (GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE, [])}

    def __init__(self, datos):

        GObject.Object.__init__(self)

        self.game_dict = datos
        self.resolucionreal = RESOLUCION_INICIAL
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = False
        self.jugador = False
        self.jugadores = pygame.sprite.RenderUpdates()

    def escalar(self, resolucion):

        self.resolucionreal = resolucion

    def config(self):
        """
        Configuración inicial del Juego.
        """

        pygame.init()
        self.reloj = pygame.time.Clock()

        from pygame.locals import MOUSEMOTION
        from pygame.locals import MOUSEBUTTONUP
        from pygame.locals import MOUSEBUTTONDOWN
        from pygame.locals import JOYAXISMOTION
        from pygame.locals import JOYBALLMOTION
        from pygame.locals import JOYHATMOTION
        from pygame.locals import JOYBUTTONUP
        from pygame.locals import JOYBUTTONDOWN
        from pygame.locals import VIDEORESIZE
        from pygame.locals import VIDEOEXPOSE
        from pygame.locals import USEREVENT
        from pygame.locals import QUIT
        from pygame.locals import ACTIVEEVENT
        from pygame.locals import KEYDOWN
        from pygame.locals import KEYUP

        pygame.event.set_blocked(
            [MOUSEMOTION, MOUSEBUTTONUP,
            MOUSEBUTTONDOWN, JOYAXISMOTION,
            JOYBALLMOTION, JOYHATMOTION,
            JOYBUTTONUP, JOYBUTTONDOWN,
            ACTIVEEVENT, USEREVENT])

        pygame.event.set_allowed(
            [QUIT, VIDEORESIZE, VIDEOEXPOSE])

        pygame.display.set_mode(
            (0, 0),
            pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)

        pygame.display.set_caption("JAMtank")

        imagen = pygame.image.load(
            self.game_dict['mapa'])

        self.escenario = pygame.transform.scale(
            imagen, RESOLUCION_INICIAL).convert_alpha()

        self.ventana = pygame.Surface(
            (RESOLUCION_INICIAL[0], RESOLUCION_INICIAL[1]))

        self.ventana_real = pygame.display.get_surface()

        pygame.mouse.set_visible(False)

        imagen_tanque = self.game_dict['tanque']

        from Jugador import Jugador

        self.jugador = Jugador(
            imagen_tanque, RESOLUCION_INICIAL)
        self.jugadores.add(self.jugador)

        '''
        for enemigo in range(1, self.game_dict['enemigos']+1):
            enemigo = Enemigo(
                imagen_tanque, RESOLUCION_INICIAL)
            self.jugadores.add(enemigo)
        '''

    def run(self):
        """
        El Juego comienza a Correr.
        """

        self.estado = "En Juego"

        self.ventana.blit(self.escenario, (0, 0))

        pygame.display.update()

        while self.estado == "En Juego":
            try:
                self.reloj.tick(35)

                self.jugadores.clear(
                    self.ventana, self.escenario)
                #self.balas.clear(
                #    self.ventana, self.escenario)
                #self.explosiones.clear(
                #    self.ventana, self.escenario)

                # FIXME:
                #   Obtener datos de tanques y balas
                #   Enviarlas al servidor
                #   Recibir los datos del servidor

                self.jugadores.update()
                # FIXME: Redibujar balas
                # FIXME: Redibujar explosiones

                pygame.event.pump()
                pygame.event.clear()

                self.jugadores.draw(self.ventana)

                self.ventana_real.blit(pygame.transform.scale(
                    self.ventana, self.resolucionreal), (0,0))

                pygame.display.update()

            except:
                self.estado = False

    def update_events(self, eventos):

        self.jugador.update_events(eventos)


if __name__ == "__main__":
    juego = Juego()
    juego.config()
    juego.run()
