#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GLib

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client

TERMINATOR = "\r\n\r\n"


class GameWidget(Gtk.DrawingArea):

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.game_thread = False
        self.server_thread = False
        self.client_thread = False
        self.client = False
        self.server = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        # CLIENT
        self.client = Client(_dict['server'])
        self.client_thread = threading.Thread(target=self.client.conectarse,
            name='client')
        self.client_thread.start()

        time.sleep(0.5)

        #_buffer = 'CONNECT*%s' % (TERMINATOR)
        #self.client.enviar(_buffer)
        #retorno = self.client.recibir()

        mapa = os.path.basename(_dict['mapa'])
        _buffer = 'M*%s%s' % (mapa, TERMINATOR)
        _buffer = '%sE*%s%s' % (_buffer, _dict['enemigos'], TERMINATOR)
        _buffer = '%sV*%s%s' % (_buffer, _dict['vidas'], TERMINATOR)

        tanque = os.path.basename(_dict['tanque'])
        _buffer = '%sN*%s%s' % (_buffer, _dict['nick'], TERMINATOR)
        _buffer = '%sT*%s%s' % (_buffer, tanque, TERMINATOR)

        self.client.enviar(_buffer)
        retorno = self.client.recibir()

        #print "ServerGameWidget:", retorno
        GLib.timeout_add(500, self.__run_game, _dict)
        return False

    def __run_game(self, _dict):
        from Juego import Juego

        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(_dict, self.client)
        self.juego.config()
        self.game_thread = threading.Thread(target=self.juego.run, name='game')
        self.game_thread.start()
        return False

    def setup_init(self, _dict):
        # SERVER
        self.server = Server((_dict['server'], 5000), RequestHandler)
        self.server.allow_reuse_address = True
        self.server.socket.setblocking(0)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()

        GLib.timeout_add(500, self.__run_client, _dict)
        return False

    def do_draw(self, context):
        rect = self.get_allocation()
        if self.juego:
            self.juego.escalar((rect.width, rect.height))
