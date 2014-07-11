#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GLib
from gi.repository import GObject

from Network.Client import Client
from Juego import Juego

TERMINATOR = "\r\n\r\n"

"""
_dict = {
    'nick': "",
    'tanque': "",
    'server': ""
    }
"""


class GameWidget(Gtk.DrawingArea):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.game_thread = False
        self.client_thread = False
        self.client = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        '''
        try:
            import socket
            socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address = (_dict['server'], 5000)
            socket.connect(address)
            socket.close()
        except:
            return False
        '''
        self.client = Client(_dict['server'])
        self.client.conectarse()
        self.client_thread = threading.Thread(target=self.client.conectarse,
            name='client')
        self.client_thread.setDaemon(True)
        self.client_thread.start()

        time.sleep(0.5)

        _buffer = 'CONNECT*%s' % (TERMINATOR)
        self.client.enviar(_buffer)
        mensajes = self.client.recibir()

        for mensaje in mensajes:
            if mensaje.startswith('CONNECT*'):
                mapa, vidas = mensaje.replace('CONNECT*', "").split()
                dirpath = os.path.dirname(os.path.dirname(_dict['tanque']))
                _dict['mapa'] = os.path.join(dirpath, "Mapas", mapa)
                _dict['vidas'] = int(vidas)
                GLib.timeout_add(500, self.__run_game, _dict.copy())
                return False
            if mensaje.startswith('CLOSE*'):
                print "FIXME: El Servidor no admite mas Jugadores", self.__run_client
        return False

    def __run_game(self, _dict):
        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(_dict, self.client)
        self.juego.config()
        self.game_thread = threading.Thread(target=self.juego.run, name='game')
        self.game_thread.setDaemon(True)
        self.game_thread.start()
        return False

    def setup_init(self, _dict):
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
        self.emit('salir')
