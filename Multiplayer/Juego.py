#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from gi.repository import GObject

import pygame

#from Enemigo import Enemigo

RESOLUCION_INICIAL = (800, 600)
BASE_PATH = os.path.dirname(__file__)
TERMINATOR = "\r\n\r\n"

GObject.threads_init()

'''
    self.game_dict = {
        'server': '',
        'nick': '',
        'mapa': "",
        'tanque': "",
        'enemigos': 1,
        'vidas': 10,
        'players':
            {ip: {
                'nick': '',
                'tanque': {
                    'path': '',
                    'pos': (0, 0, 0),
                    'energia': 100,
                    },
                'vidas': 0,
                'puntos': 0,
                'bala': ()
                },
            },
        }
'''

class Juego(GObject.Object):

    __gsignals__ = {
    "update": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self, _dict, client):

        GObject.Object.__init__(self)

        self.game_dict = _dict
        self.client = client

        self.resolucionreal = RESOLUCION_INICIAL
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = False
        self.jugador = False

        self.jugadores = pygame.sprite.RenderUpdates()
        self.balas = pygame.sprite.RenderUpdates()
        self.explosiones = pygame.sprite.RenderUpdates()

    def __client_send_data(self, a, x, y):
        _buffer = 'TP*%s %s %s%s' % (a, x, y, TERMINATOR)
        self.client.enviar(_buffer)

    def __process_data(self, mensajes):
        for mensaje in mensajes:
            m = mensaje.strip()
            if m.startswith('PLAYER*'):
                datos = m.split('**')
                ip, nick, path, ang, x, y, energia, vidas, puntos = (0, 0, 0, 0, 0, 0, 0, 0, 0)
                for dato in datos:
                    if dato.startswith('PLAYER*'):
                        ip = dato.replace('PLAYER*', '').strip()
                    elif dato.startswith('nick*'):
                        nick = dato.replace('nick*', '').strip()
                    elif dato.startswith('tanque*'):
                        path, ang, x, y, energia = dato.replace('tanque*', '').strip().split()
                    elif dato.startswith('vidas*'):
                        vidas = dato.replace('vidas*', '').strip()
                    elif dato.startswith('puntos*'):
                        puntos = dato.replace('puntos*', '').strip()
                    elif dato.startswith('bala*'):
                        # FIXME: Procesar Bala
                        pass

                #print ip, nick, path, ang, x, y, energia, vidas, puntos
                self.jugador.set_posicion(angulo=int(ang), centerx=int(x), centery=int(y))

    def run(self):
        self.estado = "En Juego"
        self.ventana.blit(self.escenario, (0, 0))
        pygame.display.update()

        while self.estado == "En Juego":
            try:
                self.reloj.tick(35)

                self.jugadores.clear(self.ventana, self.escenario)
                self.balas.clear(self.ventana, self.escenario)
                self.explosiones.clear(self.ventana, self.escenario)

                self.jugador.update()
                a, x, y = self.jugador.get_datos()
                self.__client_send_data(a, x, y)  # enviar
                mensajes = self.client.recibir()  # recibir
                self.__process_data(mensajes)  # procesar y actualizar

                # actualizar todos los jugadores
                #self.jugador.set_posicion(angulo=a, centerx=x, centery=y)
                # FIXME: actualizar mis balas
                # FIXME: Redibujar balas
                # FIXME: Redibujar explosiones
                # FIXME: Verificar colisiones de balas agenas

                pygame.event.pump()
                pygame.event.clear()

                self.jugadores.draw(self.ventana)
                self.balas.draw(self.ventana)
                self.explosiones.draw(self.ventana)

                self.ventana_real.blit(pygame.transform.scale(self.ventana,
                    self.resolucionreal), (0,0))

                pygame.display.update()

            except:
                self.estado = False

    def escalar(self, resolucion):
        self.resolucionreal = resolucion

    def update_events(self, eventos):
        self.jugador.update_events(eventos)

    def config(self):
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

        pygame.event.set_blocked([MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN,
            JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP,
            JOYBUTTONDOWN, ACTIVEEVENT, USEREVENT])
        pygame.event.set_allowed([QUIT, VIDEORESIZE, VIDEOEXPOSE])

        pygame.display.set_mode(
            (0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)

        pygame.display.set_caption("JAMtank")

        imagen = pygame.image.load(self.game_dict['mapa'])
        self.escenario = pygame.transform.scale(imagen,
            RESOLUCION_INICIAL).convert_alpha()

        self.ventana = pygame.Surface((RESOLUCION_INICIAL[0],
            RESOLUCION_INICIAL[1]))
        self.ventana_real = pygame.display.get_surface()

        #pygame.mouse.set_visible(False)
        imagen_tanque = self.game_dict['tanque']
        from Jugador import Jugador
        self.jugador = Jugador(imagen_tanque, RESOLUCION_INICIAL)
        self.jugadores.add(self.jugador)

        '''
        for enemigo in range(1, self.game_dict['enemigos']+1):
            enemigo = Enemigo(
                imagen_tanque, RESOLUCION_INICIAL)
            self.jugadores.add(enemigo)
        '''


#if __name__ == "__main__":
#    juego = Juego()
#    juego.config()
#    juego.run()
