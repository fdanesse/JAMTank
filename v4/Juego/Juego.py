#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
import random
import gobject
import gtk
import time
import platform
from Globales import get_ip
from Jugador import Jugador

RES = (800, 600)
BASE_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
OLPC = bool('olpc' in platform.platform())
LAT = 100


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

        self._res = False
        self._escenario = False
        self._win = False
        self._real_win = False
        self._client = False
        self._estado = False

        self._jugador = False
        self._data_game_players = {}

        self._jugadores = pygame.sprite.RenderUpdates()
        self._balas = pygame.sprite.RenderUpdates()
        self._explosiones = pygame.sprite.RenderUpdates()

        self._default_retorno = {"ingame": True}

        # Variables para control de latencia
        self._while = False
        self._latencias = []
        self._time = False
        self._promedio = 0.0
        self._max_lat_server = 0.0
        self._pausa = 0.0

        print "Nuevo Juego Creado:", platform.platform()

    def __enviar_datos(self):
        if self._client:
            _dict = {"ingame": self._jugador.get_datos()}

            if not self._promedio:
                # Calcula latencia y la envia luego de las primeras LAT pasadas
                promedio = self.__check_latency()
                if promedio:
                    print "Cliente Enviando Latencia local:", promedio
                    _dict["l"] = promedio

            if self._pausa:
                # Si hay que corregir segun latencia general en el server
                time.sleep(self._pausa)

            self._client.enviar(_dict)

    def __check_latency(self):
        """
        Almacena los primeros LAT tiempos entre envios y
        crea promedio de latencia local.
        """
        promedio = 0
        if len(self._latencias) <= LAT:
            if not self._time:
                self._time = float("%.3f" % time.time())
            else:
                now = float("%.3f" % time.time())
                latencia = float("%.3f" % (now - self._time))
                self._latencias.append(latencia)
                self._time = now
        else:
            promedio = float("%.3f" % (
                sum(self._latencias) / float(len(self._latencias))))
            self._promedio = promedio
            self._latencias = []
            del(self._latencias)
        return promedio

    def __set_latency(self, _dict):
        """
        Maximo de latencia en el server es la latencia a considerar.
        """
        self._max_lat_server = float("%.3f" % _dict.get("l", 0.0))
        print "Cliente Configurando Latencia General:", self._max_lat_server
        if self._pausa:
            self._pausa = self._max_lat_server - self._promedio
            print "Cliente Configurando Espera:", self._pausa

    def __latency_recalc(self):
        """
        Con todos los datos necesarios, se configura posible enlentecimiento.
        """
        if self._max_lat_server and self._promedio and not self._pausa and \
            self._promedio < self._max_lat_server:
            self._pausa = self._max_lat_server - self._promedio
            print "Cliente Configurando Espera:", self._pausa

    def __recibir_datos(self):
        self._default_retorno = self._client.recibir(
            dict(self._default_retorno))
        return self._default_retorno

    def __save_game_data(self, _dict):
        """
        Persistencia de datos de jugadores.
        """
        new = dict(_dict["ingame"])
        ips = self._data_game_players.keys()
        for key in new.keys():
            if not key in ips:
                tanque = os.path.join(BASE_PATH, "Tanques", new[key]["t"])
                jugador = Jugador(RES, key, tanque, new[key]["n"])
                self._jugadores.add(jugador)
            self._data_game_players[key] = new[key]
        self._jugadores.update(new)

    def __update(self, _dict):
        if _dict.get("off", False):
            # Recibe salir desde el server
            self._estado = False
            del(_dict["off"])

        if not _dict.get("ingame"):
            print "Error al leer ingame en el juego", _dict
            return False

        self.__save_game_data(_dict)

        if "l" in _dict.keys():
            self.__set_latency(_dict)
        self.__latency_recalc()

    def __run(self):
        while gtk.events_pending():
            gtk.main_iteration()
        self._jugadores.clear(self._win, self._escenario)

        if self._jugador:
            self._jugador.process_events()
        self.__enviar_datos()
        self.__update(self.__recibir_datos())

        self._jugadores.draw(self._win)

        self._real_win.blit(pygame.transform.scale(
            self._win, self._res), (0, 0))

        pygame.display.update()
        pygame.event.pump()
        pygame.event.clear()

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
        if not self._promedio:
            # Las primeras LAT pasadas son solo para calcular latencia.
            return False
        if "Escape" in eventos:
            self._estado = False
        else:
            if self._jugador:
                self._jugador.update_events(eventos)

    def load(self, mapa, tank, nick):
        print "Cargando mapa:", mapa
        imagen = pygame.image.load(mapa)
        self._escenario = pygame.transform.scale(imagen, RES).convert_alpha()
        ip = get_ip()
        self._jugador = Jugador(RES, ip, tank, nick)
        self._jugadores.add(self._jugador)
        self._data_game_players[ip] = {}

    def pause_player(self):
        if self._jugador:
            self._jugador.pausar()

    def reactivar_player(self):
        if self._jugador:
            self._jugador.reactivar()

    def config(self, res=(800, 600), client=False, xid=False):
        print "Configurando Juego:"
        print "\tres:", res
        print "\tclient", client
        print "\txid", xid
        self._res = res
        self._client = client
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
        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)
