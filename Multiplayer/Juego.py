#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame

from gi.repository import GObject
from gi.repository import Gtk

from Jugador import Jugador
from Bala import Bala

RESOLUCION_INICIAL = (800, 600)
BASE_PATH = os.path.dirname(__file__)

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
    'bala': '',
    'bala-sprite', ''
    }
'''

JUGADORES = {}


def get_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 80))
        return str(s.getsockname()[0]).strip()
    except:
        return "localhost"


class Juego(GObject.Object):

    __gsignals__ = {
    "update": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self, _dict, client):

        GObject.Object.__init__(self)

        # _dict = {
        #   'tanque': '. . . /JAMTank/Tanques    anque_3.png',
        #   'mapa': '. . . /JAMTank/Mapas/fondo2.png',
        #   'nick': 'un_nombre',
        #   'vidas': 50,
        #   'server': '192.168.1.9'}

        GAME['mapa'] = str(_dict['mapa'])

        self.ip = get_ip()
        JUGADORES[self.ip] = {
            'nick': '',
            'tanque': '',
            'vidas': 0,
            'puntos': 0,
            }
        JUGADORES[self.ip]['nick'] = str(_dict['nick'])
        JUGADORES[self.ip]['tanque'] = str(_dict['tanque'])
        JUGADORES[self.ip]['vidas'] = int(_dict['vidas'])

        self.client = client

        self.resolucionreal = RESOLUCION_INICIAL
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = False
        self.jugador = False
        self.bala = False
        self.disparo = False

        self.jugadores = pygame.sprite.RenderUpdates()
        self.balas = pygame.sprite.RenderUpdates()
        #self.explosiones = pygame.sprite.RenderUpdates()

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
                #self.explosiones.clear(self.ventana, self.escenario)

                self.jugador.update()
                a, x, y = self.jugador.get_datos()

                datos = "UPDATE,%s,%s,%s" % (a, x, y)
                if self.disparo:
                    datos = "%s,%s,%s,%s" % (datos, a, x, y)
                    self.disparo = False
                elif self.bala:
                    self.bala.update()
                    a, x, y = self.bala.get_datos()
                    datos = "%s,%s,%s,%s" % (datos, a, x, y)
                else:
                    datos = "%s,-,-,-" % datos

                self.client.enviar(datos)

                mensajes = self.client.recibir()
                ip, nick, tanque, a, x, y, aa, xx, yy = mensajes.split(",")
                a = int(a)
                x = int(x)
                y = int(y)
                if aa != '-' and xx != '-' and yy != '-':
                    aa = int(aa)
                    xx = int(xx)
                    yy = int(yy)
                    if not self.bala:
                        image_path = os.path.join(os.path.dirname(
                            os.path.dirname(GAME['mapa'])),
                            'Iconos', 'bala.png')
                        self.bala = Bala(aa, xx, yy, image_path,
                            RESOLUCION_INICIAL)
                        self.balas.add(self.bala)
                    else:
                        valor = self.bala.set_posicion(centerx=xx, centery=yy)
                        if not valor:
                            del(self.bala)
                            self.bala = False

                self.jugador.update_data(a,x,y)

                pygame.event.pump()
                pygame.event.clear()

                self.jugadores.draw(self.ventana)
                self.balas.draw(self.ventana)
                #self.explosiones.draw(self.ventana)

                self.ventana_real.blit(pygame.transform.scale(self.ventana,
                    self.resolucionreal), (0, 0))

                pygame.display.update()
                pygame.time.wait(1)

            except:
                self.estado = False

    def escalar(self, resolucion):
        self.resolucionreal = resolucion

    def update_events(self, eventos):
        if "space" in eventos and not self.bala:
            self.disparo = True
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

        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)
        #sonido_juego.play(-1)

        self.jugador = Jugador(JUGADORES[self.ip]['tanque'],
            RESOLUCION_INICIAL)
        self.jugadores.add(self.jugador)
        x, y = RESOLUCION_INICIAL
        self.jugador.update_data(centerx=x/2, centery=y/2)
        #JUGADORES[self.ip]['sprite'] = self.jugador


#if __name__ == "__main__":
#    juego = Juego()
#    juego.config()
#    juego.run()
