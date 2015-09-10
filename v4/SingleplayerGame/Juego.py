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
from Bala import Bala
from Explosion import Explosion
from Sound import Sound

RES = (800, 600)
BASE_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
LAT = 100


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

        self._jugadores = pygame.sprite.RenderUpdates()
        self._balas = pygame.sprite.RenderUpdates()
        self._mybalas = pygame.sprite.RenderUpdates()
        self._explosiones = pygame.sprite.RenderUpdates()

        self._while = False

        print "Nuevo Juego Creado:", platform.platform()

    def __reactivar_disparos(self):
        self._disparos_activos = True
        return False

    def __check_disparos_and_balas(self):
        """
        Actualizar posiciones de balas
        Disparos se convierte en balas rumbo al server
        """
        mybalas = []
        for bala in self._balas.sprites():
            if bala.ip == self._ip:
                mybalas.append(bala.get_datos())
        self._data_game_players[self._ip]["b"] = mybalas

        if self._disparo:
            self._disparo = False
            self._data_game_players[self._ip]["b"].append(
                self._jugador.get_disparo())
            gobject.timeout_add(1000, self.__reactivar_disparos)

    def __enviar_datos(self):
        if self._client:
            # Datos de posicion del jugador local
            _dict = {"ingame": self._jugador.get_datos()}

            if not self._promedio:
                # Calcula latencia y la envia luego de las primeras LAT pasadas
                promedio = self.__check_latency()
                if promedio:
                    print "Cliente Enviando Latencia local:", promedio
                    _dict["l"] = promedio

            # Datos de Balas locales
            _dict["ingame"]["b"] = self._data_game_players[
                self._ip].get("b", [])

            # Datos de Colisiones
            col = self._data_game_players[self._ip].get("c", [])
            if col:
                _dict["ingame"]["c"] = col

            if self._pausa:
                # Si hay que corregir segun latencia general en el server
                time.sleep(self._pausa)

            self._client.enviar(_dict)

    def __recibir_datos(self):
        self._default_retorno = self._client.recibir(
            dict(self._default_retorno))
        return self._default_retorno

    def __save_players_data(self, new):
        """
        Persistencia de datos de jugadores y balas.
        """
        ips = self._data_game_players.keys()
        for key in new.keys():
            if not key in ips:
                tanque = os.path.join(BASE_PATH, "Tanques", new[key]["t"])
                jugador = Jugador(RES, key, tanque, new[key]["n"])
                self._jugadores.add(jugador)
            self._data_game_players[key] = new[key]
        self._jugadores.update(new)

        for key in self._data_game_players.keys():
            if "p" in self._data_game_players[key].keys():
                if not self._data_game_players[key]["p"]:
                    del(self._data_game_players[key]["p"])

    def __save_balas_data(self, _dict):
        path = os.path.join(BASE_PATH, "Balas", "bala.png")

        b = 0
        for ip in _dict.keys():
            b += len(_dict[ip].get("b", []))
        if b > len(self._balas.sprites()):
            self._audio.disparo()

        for ip in _dict.keys():
            # balas en server
            balas = _dict[ip].get("b", [])
            # sprites de balas actuales
            actuales = []
            for sprite in self._balas.sprites():
                if sprite.ip == ip:
                    actuales.append(sprite)

            while len(actuales) < len(balas):
                # Agregar las que faltan
                _id = 0
                if actuales:
                    _id = actuales.index(actuales[-1]) + 1
                b = Bala(balas[_id], path, RES, ip)
                self._balas.add(b)
                actuales.append(b)

            while len(actuales) > len(balas):
                # Quitar las que sobran
                a = actuales[0]
                for g in a.groups():
                    g.remove(a)
                a.kill()
                actuales.remove(a)

            # Actualizar posiciones
            for sprite in actuales:
                _id = actuales.index(sprite)
                datos = balas[_id]
                sprite.set_posicion(centerx=datos["x"], centery=datos["y"])

    def __save_colisiones_data(self, _dict):
        path = os.path.join(BASE_PATH, "Explosion")
        exp = []
        for ip in _dict.keys():
            exp.extend(_dict[ip].get("e", []))
        if exp:
            self._audio.explosion()
        for e in exp:
            self._explosiones.add(Explosion(e["x"], e["y"], path))
        # Las explosiones no deben guardarse
        for ip in self._data_game_players.keys():
            if "e" in self._data_game_players[ip].keys():
                del(self._data_game_players[ip]["e"])

    def __check_collisions(self):
        """
        Colisiones tienen (ip de tanque tocado x, y), se envian estos datos
        y se quitan las balas de los datos a enviar, pero no se eliminan sus
        sprites hasta confirmación desde el server
        """
        for jugador in self._jugadores.sprites():
            if jugador._ip != self._ip:
                remover = []
                for bala in self._data_game_players[self._ip].get("b", []):
                    x, y = bala["x"], bala["y"]
                    if jugador.rect.collidepoint((x, y)):
                        if not "c" in self._data_game_players[self._ip].keys():
                            self._data_game_players[self._ip]["c"] = []
                        self._data_game_players[self._ip]["c"].append(
                            {"ip": jugador._ip, "x": x, "y": y})
                        remover.append(
                            self._data_game_players[self._ip]["b"].index(bala))
                if remover:
                    for _id in reversed(remover):
                        bala = self._data_game_players[self._ip]["b"][_id]
                        self._data_game_players[self._ip]["b"].remove(bala)

    def __update_data(self, _dict):
        if _dict.get("off", False):
            # Recibe salir desde el server
            self._estado = False
            del(_dict["off"])

        if not _dict.get("ingame"):
            print "Error al leer ingame en el juego", _dict
            return False

        self.__save_players_data(dict(_dict.get("ingame", {})))
        self.__save_balas_data(dict(_dict.get("ingame", {})))
        self.__save_colisiones_data(dict(_dict.get("ingame", {})))

        if "l" in _dict.keys():
            self.__set_latency(_dict)
        self.__latency_recalc()

    def __run(self):
        while gtk.events_pending():
            gtk.main_iteration()
        self._balas.clear(self._win, self._escenario)
        self._jugadores.clear(self._win, self._escenario)
        self._explosiones.clear(self._win, self._escenario)

        if self._jugador:
            self._jugador.process_events()
        #self._balas.update(self._ip)
        #self._explosiones.update()
        #self.__check_disparos_and_balas()
        #self.__check_collisions()
        #self.__enviar_datos()
        #self.__update_data(self.__recibir_datos())

        self._jugadores.draw(self._win)
        self._balas.draw(self._win)
        self._explosiones.draw(self._win)

        self._real_win.blit(pygame.transform.scale(
            self._win, self._res), (0, 0))

        pygame.display.update()
        pygame.event.pump()
        pygame.event.clear()

        if self._contador == 10:
            #self.emit("update", dict(self._data_game_players))
            self._contador = 0
        self._contador += 1

        if self._estado:
            return True
        else:
            pygame.quit()
            #self.emit("exit", self._data_game_players)
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
        if not self._promedio:
            # Las primeras LAT pasadas son solo para calcular latencia.
            return False
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

    def load(self, mapa, tank):
        print "Cargando mapa:", mapa
        imagen = pygame.image.load(mapa)
        self._escenario = pygame.transform.scale(imagen, RES).convert_alpha()
        #self._jugador = Jugador(RES, tank)
        #self._jugadores.add(self._jugador)
        #self._data_game_players[self._ip] = {}

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
