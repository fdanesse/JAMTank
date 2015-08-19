#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
import random
import gobject
import gtk
from Jugador import Jugador

RES = (800, 600)


class Juego(gobject.GObject):

    __gsignals__ = {
    #"update": (gobject.SIGNAL_RUN_LAST,
    #    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    #"end": (gobject.SIGNAL_RUN_LAST,
    #    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "exit": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gobject.GObject.__init__(self)

        self._res = RES
        self._escenario = False
        self._win = False
        self._real_win = False
        self._clock = False
        self._estado = False
        self._client = False
        self._time = 35

        self._jugador = False
        self._data_game_players = {}

        self._jugadores = pygame.sprite.RenderUpdates()
        self._balas = pygame.sprite.RenderUpdates()
        self._explosiones = pygame.sprite.RenderUpdates()

        self._default_retorno = {"ingame": {"players": {}}}

        print "Nuevo Juego Creado"

    def __enviar_datos(self):
        if self._client:
            if self._jugador:
                _dict = {"ingame": self._jugador.get_datos()}
            else:
                _dict = {
                    "ingame": {
                        "ang": 0,
                        "x": 0,
                        "y": 0}
                    }
            self._client.enviar(_dict)

    def __recibir_datos(self):
        if self._client:
            _dict = self._client.recibir(dict(self._default_retorno))
        return _dict

    def __update(self, _dict):
        if _dict.get("off", False):
            self._estado = False
        else:
            new = dict(_dict["ingame"])
            # FIXME: Realizar aca el Chequeo de Colisiones
            for key in new.keys():
                self._data_game_players[key] = new[key]
            #self._jugadores.update(new)

    def run(self):
        print "Comenzando a Correr el juego..."
        self._estado = "En Juego"
        self._win.blit(self._escenario, (0, 0))
        pygame.display.update()
        pygame.time.wait(3)
        #gobject.timeout_add(1500, self.__emit_update)
        while self._estado == "En Juego":
            #try:
            self._clock.tick(self._time)
            while gtk.events_pending():
                gtk.main_iteration()
            self._jugadores.clear(self._win, self._escenario)
            self._balas.clear(self._win, self._escenario)
            self._explosiones.clear(self._win, self._escenario)

            #if self.jugador:
            #    El jugador actualiza su posicion y disparos segun eventos
            #    self.jugador.status_update()
            #    los nuevos datos deben enviarse al server

            self.__enviar_datos()
            _dict = self.__recibir_datos()
            self.__update(_dict)

            #Con los datos recibidos se actualizan todos los objetos

            self._explosiones.update()

            self._jugadores.draw(self._win)
            self._balas.draw(self._win)
            self._explosiones.draw(self._win)

            self._real_win.blit(pygame.transform.scale(
                self._win, self._res), (0, 0))

            pygame.display.update()
            pygame.event.pump()
            pygame.event.clear()
            #pygame.time.wait(1)
            #except:
            #    "Error en run game"
            #    self._estado = False

        pygame.quit()
        self.emit('exit', self._data_game_players)

    def update_events(self, eventos):
        if "Escape" in eventos:
            self._estado = False

    def load(self, mapa, tank, nick):
        print "Cargando mapa:", mapa
        imagen = pygame.image.load(mapa)
        self._escenario = pygame.transform.scale(imagen, RES).convert_alpha()
        #path = os.path.dirname(BASE_PATH)
        #sound = os.path.join(path, "Audio", "Juego.ogg")
        #self.sound_juego = pygame.mixer.Sound(sound)
        #self.sound_juego.play(-1)
        #disparo = os.path.join(path, "Audio", "disparo.ogg")
        #self.sound_disparo = pygame.mixer.Sound(disparo)
        #explosion = os.path.join(path, "Audio", "explosion.ogg")
        #self.sound_explosion = pygame.mixer.Sound(explosion)
        #print "Cargando Jugador:", nick, tank
        #self._jugador = Jugador(self._res, self._client.ip, tank, nick)
        #self._jugadores.add(self._jugador)

    def config(self, time=35, res=(800, 600), client=False, xid=False):
        print "Configurando Juego:"
        print "\ttime:", time
        print "\tres:", res
        print "\tclient", client
        print "\txid", xid
        self._time = time
        self._res = res
        self._client = client
        if xid:
            os.putenv("SDL_WINDOWID", str(xid))
        pygame.init()
        self._clock = pygame.time.Clock()
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
        #pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)
        pygame.display.set_mode(self._res, pygame.DOUBLEBUF, 0)
        pygame.display.set_caption("JAMtank")
        self._win = pygame.Surface(RES)
        self._real_win = pygame.display.get_surface()
        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)


#if __name__ == "__main__":
#    mapa = os.path.join(os.path.dirname(BASE_PATH), "Mapas", "f2.png")
#    juego = Juego()
#    juego.config(time=35, res=(800, 600), client=False, xid=False)
#    juego.load(mapa)
#    juego.run()
