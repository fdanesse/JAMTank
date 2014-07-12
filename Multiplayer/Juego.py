#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame

from gi.repository import GObject
from gi.repository import Gtk

from Jugador import Jugador

RESOLUCION_INICIAL = (800, 600)
BASE_PATH = os.path.dirname(__file__)
TERMINATOR = "\r\n\r\n"

GObject.threads_init()

GAME = {
    'mapa': "",
    #'vidas': 0,
    }

'''
MODEL = {
    'nick': '',
    'tanque': '',
    'sprite': False,  #'pos': (0, 0, 0), 'energia': 100,
    'vidas': 0,
    'puntos': 0,
    'bala': ()
    }
'''

JUGADORES = {}
PR = False


def get_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        return str(s.getsockname()[0]).strip()
    except:
        return ""


class Juego(GObject.Object):

    __gsignals__ = {
    "update": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self, _dict, client):

        GObject.Object.__init__(self)

        # _dict = {
        #   'enemigos': 10,             **** Sólo lo recibe en caso de ser HOST
        #   'tanque': '. . . /JAMTank/Tanques/tanque_3.png',
        #   'mapa': '. . . /JAMTank/Mapas/fondo2.png',
        #   'nick': 'un_nombre',
        #   'vidas': 50,
        #   'server': '192.168.1.9'}

        GAME['mapa'] = str(_dict['mapa'])
        #GAME['vidas'] = int(_dict['vidas'])

        ip = get_ip()
        JUGADORES[ip] = {
            'nick': '',
            'tanque': '',
            'sprite': False,
            'vidas': 0,
            'puntos': 0,
            'bala': ()
            }
        JUGADORES[ip]['nick'] = str(_dict['nick'])
        JUGADORES[ip]['tanque'] = str(_dict['tanque'])
        JUGADORES[ip]['vidas'] = int(_dict['vidas'])

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
        if PR:
            print "CLIENT Recibe:", mensajes

        for mensaje in mensajes:
            m = mensaje.strip()
            if m.startswith('PLAYER*'):
                self.__process_player(m)

    def __process_player(self, m):
        ip, nick, path, ang, x, y, energia, vidas, puntos, bala = (
            '', '', '', 0, 0, 0, 0, 0, 0, ())
        datos = m.split('||')
        for dato in datos:
            if dato.startswith('PLAYER*'):
                ip = str(dato.replace('PLAYER*', '').strip())
            elif dato.startswith('nick*'):
                nick = str(dato.replace('nick*', '').strip())
            elif dato.startswith('tanque*'):
                path, ang, x, y, energia = dato.replace(
                    'tanque*', '').strip().split()
                ang = int(ang)
                x = int(x)
                y = int(y)
                energia = int(energia)
            elif dato.startswith('vidas*'):
                vidas = int(dato.replace('vidas*', '').strip())
            elif dato.startswith('puntos*'):
                puntos = int(dato.replace('puntos*', '').strip())
            elif dato.startswith('bala*'):
                # FIXME: Procesar Bala
                pass

        self.__update_player(ip, nick, path, ang, x, y, energia,
            vidas, puntos, bala)

    def __update_player(self, ip, nick, path, ang, x, y, energia, vidas,
        puntos, bala):

        if not ip in JUGADORES.keys():
            JUGADORES[ip] = {
                'nick': '',
                'tanque': '',
                'sprite': False,
                'vidas': 0,
                'puntos': 0,
                'bala': ()
                }
            JUGADORES[ip]['nick'] = nick
            dirpath = os.path.dirname(os.path.dirname(GAME['mapa']))
            JUGADORES[ip]['tanque'] = os.path.join(dirpath, 'Tanques', path)
            JUGADORES[ip]['vidas'] = vidas

            jugador = Jugador(JUGADORES[ip]['tanque'], RESOLUCION_INICIAL)
            self.jugadores.add(jugador)
            JUGADORES[ip]['sprite'] = jugador
            JUGADORES[ip]['sprite'].update_data(angulo=ang, centerx=x,
                centery=y, energia=energia, bala=bala)
        else:
            JUGADORES[ip]['sprite'].update_data(angulo=ang, centerx=x,
                centery=y, energia=energia, bala=bala)

    def salir(self):
        # FIXME: Enviar Desconectarse y Finalizar al Servidor
        self.estado = False
        pygame.quit()
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False

    def run(self):
        self.estado = "En Juego"
        self.ventana.blit(self.escenario, (0, 0))
        pygame.display.update()
        pygame.time.wait(3)

        while self.estado == "En Juego":
            try:
                self.reloj.tick(35)
                while Gtk.events_pending():
                    Gtk.main_iteration()
                self.jugadores.clear(self.ventana, self.escenario)
                self.balas.clear(self.ventana, self.escenario)
                self.explosiones.clear(self.ventana, self.escenario)

                self.jugador.update()
                a, x, y = self.jugador.get_datos()

                if self.client:
                    self.__client_send_data(a, x, y)  # enviar
                    mensajes = self.client.recibir()  # recibir
                    self.__process_data(mensajes)  # procesar y actualizar

                # FIXME: actualizar mis balas
                # FIXME: Redibujar balas
                # FIXME: Verificar colisiones de balas agenas
                # FIXME: Redibujar explosiones

                pygame.event.pump()
                pygame.event.clear()

                self.jugadores.draw(self.ventana)
                self.balas.draw(self.ventana)
                self.explosiones.draw(self.ventana)

                self.ventana_real.blit(pygame.transform.scale(self.ventana,
                    self.resolucionreal), (0, 0))

                pygame.display.update()
                pygame.time.wait(1)
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
            JOYBUTTONDOWN, ACTIVEEVENT, USEREVENT, KEYDOWN, KEYUP])
        pygame.event.set_allowed([QUIT, VIDEORESIZE, VIDEOEXPOSE])

        pygame.display.set_mode(
            (0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)

        pygame.display.set_caption("JAMtank")

        imagen = pygame.image.load(GAME['mapa'])
        self.escenario = pygame.transform.scale(imagen,
            RESOLUCION_INICIAL).convert_alpha()

        self.ventana = pygame.Surface((RESOLUCION_INICIAL[0],
            RESOLUCION_INICIAL[1]))
        self.ventana_real = pygame.display.get_surface()

        #pygame.mouse.set_visible(False)
        ip = get_ip()
        self.jugador = Jugador(JUGADORES[ip]['tanque'], RESOLUCION_INICIAL)
        self.jugadores.add(self.jugador)
        JUGADORES[ip]['sprite'] = self.jugador


#if __name__ == "__main__":
#    juego = Juego()
#    juego.config()
#    juego.run()
