#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject

from Network.Client import Client
from Juego import Juego


class GameWidget(Gtk.DrawingArea):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.client = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        """
        El Cliente remoto intenta conectarse al server pasandole:
                tanque y nick (propios)
        """
        self.client = Client(str(_dict['server']))
        self.client.conectarse()

        tanque = os.path.basename(str(_dict['tanque']))
        _buffer = "JOIN,%s,%s" % (tanque, str(_dict['nick']))

        self.client.enviar(_buffer)
        retorno = self.client.recibir()

        if retorno == "CLOSE":
            print "No se admiten más Jugadores"
        else:
            dirpath = os.path.dirname(os.path.dirname(str(_dict['tanque'])))
            _dict['mapa'] = os.path.join(dirpath, "Mapas", retorno)
            time.sleep(0.5)
            self.__run_game(dict(_dict))

    def __run_game(self, _dict):
        """
        Comienza a correr el Juego.
        """
        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))
        self.juego = Juego(dict(_dict), self.client)
        self.juego.config()
        time.sleep(0.5)
        self.juego.run()

    def setup_init(self, _dict):
        self.__run_client(dict(_dict))
        return False

    def do_draw(self, context):
        """
        Reescalado en gtk, reescala en pygame.
        """
        rect = self.get_allocation()
        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def update_events(self, eventos):
        """
        Eventos gtk, se pasan a pygame
        """
        if "Escape" in eventos:
            self.salir()
        else:
            if self.juego:
                self.juego.update_events(eventos)

    def salir(self):
        if self.juego:
            self.juego.salir()
        self.emit('salir')
