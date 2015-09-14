#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Juego.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import pygame
import gobject
import gtk
import time
import platform
from Jugador import Jugador
from Enemigo import Enemigo
from Bala import Bala
from Explosion import Explosion
from Sound import Sound

MODEL = {
    "disparos": 0,
    "aciertos": 0,
    "puntos": 0,
    "energia": 100,
    "vidas": 1,
    }
RES = (800, 600)
BASE_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


class Juego(gobject.GObject):

    __gsignals__ = {
    "update": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "exit": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gobject.GObject.__init__(self)

        self._audio = False
        self._res = False
        self._escenario = False
        self._win = False
        self._real_win = False
        self._estado = False

        self._jugador = False
        self._disparo = False
        self._disparos_activos = True
        self._contador = 0
        self._data_game_players = {}

        self._jugadores = pygame.sprite.RenderUpdates()
        self._balas = pygame.sprite.RenderUpdates()
        self._mybalas = pygame.sprite.RenderUpdates()
        self._explosiones = pygame.sprite.RenderUpdates()

        self._while = False

        print "Nuevo Juego Creado:", platform.platform()

    def __reactivar_disparos(self):
        self._disparos_activos = True
        return False

    def __disparar(self, jugador):
        self._audio.disparo()
        _id = self._jugador._id
        path = os.path.join(BASE_PATH, "Balas", "bala.png")
        _dict = jugador.get_disparo()
        b = Bala(_dict, path, RES, _id)
        self._balas.add(b)
        self._data_game_players[_id]["disparos"] += 1

    def __check_disparos(self):
        if self._disparo:
            self._disparo = False
            self.__disparar(self._jugador)
            gobject.timeout_add(1000, self.__reactivar_disparos)

    def __explosion(self, explosiones):
        if explosiones:
            path = os.path.join(BASE_PATH, "Explosion")
            self._audio.explosion()
            for e in explosiones:
                x, y = e
                self._explosiones.add(Explosion(x, y, path))

    def __check_collisions(self):
        explosiones = []
        for bala in self._balas.sprites():
            x, y = bala.rect.centerx, bala.rect.centery
            for jugador in self._jugadores.sprites():
                jid = jugador._id
                bid = bala._id
                if jid != bid:
                    # Colisiones jugadores <> balas
                    if jugador.rect.collidepoint((x, y)):
                        self._data_game_players[jid]["energia"] -= 10
                        self._data_game_players[bid]["aciertos"] += 1
                        self._data_game_players[bid]["puntos"] += 1
                        if self._data_game_players[jid]["energia"] <= 0:
                            self._data_game_players[jid]["vidas"] -= 1
                            self._data_game_players[bid]["puntos"] += 10
                            if self._data_game_players[jid]["vidas"] <= 0:
                                jugador.pausar()
                        for g in bala.groups():
                            g.remove(bala)
                        bala.kill()
                        explosiones.append((x, y))
        self.__explosion(explosiones)

    def __check_vidas(self):
        _id = self._jugador._id
        estados = []
        for j in self._jugadores.sprites():
            if j._id != _id:
                estados.append(bool(self._data_game_players[j._id]["vidas"]))
        if self._data_game_players[_id]["vidas"] <= 0 or (not True in estados):
            self._estado = False

    def __run(self):
        while gtk.events_pending():
            gtk.main_iteration()
        self._balas.clear(self._win, self._escenario)
        self._jugadores.clear(self._win, self._escenario)
        self._explosiones.clear(self._win, self._escenario)

        self._jugadores.update()
        self._balas.update()
        self._explosiones.update()

        self.__check_disparos()
        self.__check_collisions()

        self._jugadores.draw(self._win)
        self._balas.draw(self._win)
        self._explosiones.draw(self._win)

        self._real_win.blit(pygame.transform.scale(
            self._win, self._res), (0, 0))

        pygame.display.update()
        pygame.event.pump()
        pygame.event.clear()

        if self._contador == 10:
            self.emit("update", self._data_game_players)
            self._contador = 0
        self._contador += 1

        self.__check_vidas()

        if self._estado:
            return True
        else:
            pygame.quit()
            self.emit("exit", self._data_game_players)
            return False

    def run(self, reset=True):
        if self._while:
            gobject.source_remove(self._while)
            self._while = False
            self._estado = False
        if reset:
            print "Comenzando a Correr el juego..."
            self._win.blit(self._escenario, (0, 0))
            pygame.display.update()
            time.sleep(0.03)
            self._estado = True
            self._while = gobject.timeout_add(3, self.__run)

    def update_events(self, eventos):
        if "Escape" in eventos:
            self._estado = False
            return False
        if "space" in eventos:
            if self._jugador._estado == "activo":
                if not self._disparo and self._disparos_activos:
                    self._disparo = True
                    self._disparos_activos = False
        else:
            if self._jugador:
                self._jugador.update_events(eventos)

    def load(self, mapa, tank, enemigos):
        print "Cargando mapa:", mapa
        imagen = pygame.image.load(mapa)
        self._escenario = pygame.transform.scale(imagen, RES).convert_alpha()
        _id = 0
        self._jugador = Jugador(RES, tank, _id)
        self._jugadores.add(self._jugador)
        self._data_game_players[_id] = dict(MODEL)
        _id = 1
        for enem in enemigos:
            self._jugadores.add(Enemigo(RES, enem, _id))
            self._data_game_players[_id] = dict(MODEL)
            _id += 1

    def config(self, res=(800, 600), xid=False):
        print "Configurando Juego:"
        print "\tres:", res
        print "\txid", xid
        self._res = res
        if xid:
            os.putenv("SDL_WINDOWID", str(xid))
        pygame.init()
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
        self._audio = Sound()
