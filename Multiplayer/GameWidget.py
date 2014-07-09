#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading

from gi.repository import Gtk
from gi.repository import GdkX11

from Network.Server import Server
from Network.Server import RequestHandler

TERMINATOR = "\r\n\r\n"


class GameWidget(Gtk.DrawingArea):

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        #self.juego = False
        #self.client = False
        #self.client_thread = False
        #self.game_thread = False
        self.server_thread = False

        self.show_all()

    def do_draw(self, context):
        rect = self.get_allocation()
        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def setup_init(self, _dict):
        # SERVER
        server = Server((_dict['server'], 5000), RequestHandler)
        server.allow_reuse_address = True
        server.socket.setblocking(0)

        self.server_thread = threading.Thread(target=server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()

        #self.jamtank = JAMtank(ip=self.ip_server, PUERTO=PUERTO)
        #client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #direccion_servidor = (_dict['server'], 5000)
        #client.connect(direccion_servidor)
        #client.setblocking(0)

        '''
        # CLIENT
        from Multiplayer.Client import Client
        self.client = Client('192.168.1.26')

        self.client_thread = threading.Thread(
            target=self.client.conectarse, name='client')

        self.client_thread.start()
        datos = self.__game_setup(datos)

        from Multiplayer.Juego import Juego

        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(datos, self.client)
        self.juego.config()

        self.game_thread = threading.Thread(
            target=self.juego.run, name='game')

        self.game_thread.start()
        '''
