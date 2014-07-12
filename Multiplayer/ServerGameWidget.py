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

TERMINATOR = "\r\n\r\n"

"""
_dict = {
    'server': get_ip(),
    'nick': '',
    'mapa': "",
    'tanque': "",
    'enemigos': 10,
    'vidas': 50,
    }
"""


class GameWidget(Gtk.DrawingArea):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        #self.game_thread = False
        self.server_thread = False
        #self.client_thread = False
        self.client = False
        self.server = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        self.client = Client(str(_dict['server']))
        self.client.conectarse()
        #self.client_thread = threading.Thread(target=self.client.conectarse,
        #    name='client')
        #self.client_thread.setDaemon(True)
        #self.client_thread.start()

        mapa = os.path.basename(str(_dict['mapa']))
        _buffer = 'M*%s%s' % (mapa, TERMINATOR)
        _buffer = '%sE*%s%s' % (_buffer, str(_dict['enemigos']), TERMINATOR)
        _buffer = '%sV*%s%s' % (_buffer, str(_dict['vidas']), TERMINATOR)

        tanque = os.path.basename(str(_dict['tanque']))
        _buffer = '%sN*%s%s' % (_buffer, str(_dict['nick']), TERMINATOR)
        _buffer = '%sT*%s%s' % (_buffer, tanque, TERMINATOR)

        self.client.enviar(_buffer)
        retorno = self.client.recibir()

        time.sleep(0.5)
        self.__run_game(_dict.copy())

    def __run_game(self, _dict):
        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(_dict.copy(), self.client)
        self.juego.config()
        time.sleep(0.5)
        self.juego.run()
        #self.game_thread = threading.Thread(
        #   target=self.juego.run, name='game')
        #self.game_thread.setDaemon(True)
        #self.game_thread.start()

    def setup_init(self, _dict):
        self.server = Server((str(_dict['server']), 5000), RequestHandler)
        self.server.allow_reuse_address = True
        self.server.socket.setblocking(0)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()

        time.sleep(0.5)
        self.__run_client(_dict.copy())
        return False

    def do_draw(self, context):
        rect = self.get_allocation()
        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def update_events(self, eventos):
        if "Escape" in eventos:
            self.salir()
        else:
            if self.juego:
                self.juego.update_events(eventos)

    def salir(self):
        if self.juego:
            self.juego.salir()
        self.server.shutdown()
        self.emit('salir')
