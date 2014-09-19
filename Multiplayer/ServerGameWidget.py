#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client
from Juego import Juego


class GameWidget(Gtk.DrawingArea):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.server_thread = False
        self.client = False
        self.server = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        """
        El Cliente Host, se encarga de configurar el Server con:
            mapa, vidas, enemigos,
                tanque y nick (propios)
        """

        self.client = Client(str(_dict['server']))
        self.client.conectarse()

        mapa = os.path.basename(str(_dict['mapa']))
        tanque = os.path.basename(str(_dict['tanque']))
        _buffer = "Config,%s,%s,%s,%s,%s" % (mapa, str(_dict['enemigos']),
            str(_dict['vidas']), tanque, str(_dict['nick']))

        self.client.enviar(_buffer)
        retorno = self.client.recibir()

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
        """
        Comienza a correr el Server.
        """
        self.server = Server((str(_dict['server']), 5000), RequestHandler)
        self.server.allow_reuse_address = True
        self.server.socket.setblocking(0)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        time.sleep(0.5)
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
        if "space" in eventos:
            eventos.remove("space")

    def salir(self):
        if self.juego:
            self.juego.salir()
        #self.server.shutdown()
        self.emit('salir')
