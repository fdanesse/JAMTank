#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading

from gi.repository import Gtk
from gi.repository import GdkX11

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client

TERMINATOR = "\r\n\r\n"


class GameWidget(Gtk.DrawingArea):

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        #self.game_thread = False
        self.server_thread = False
        self.client_thread = False
        self.client = False
        self.juego = False

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

        time.sleep(0.5)

        # CLIENT
        self.client = Client(_dict['server'])
        self.client_thread = threading.Thread(target=self.client.conectarse,
            name='client')
        self.client_thread.start()

        time.sleep(0.5)

        #_buffer = 'CONNECT*%s' % (TERMINATOR)
        #self.client.enviar(_buffer)
        #retorno = self.client.recibir()

        _buffer = 'M*%s%s' % (_dict['mapa'], TERMINATOR)
        _buffer = '%sE*%s%s' % (_buffer, _dict['enemigos'], TERMINATOR)
        _buffer = '%sV*%s%s' % (_buffer, _dict['vidas'], TERMINATOR)
        '''
        'nick': '',
        'mapa': "",
        'tanque': "",
        'enemigos': 10,
        'vidas': 50,
        '''
        _buffer = '%sN*%s%s' % (_buffer, _dict['nick'], TERMINATOR)
        _buffer = '%sT*%s%s' % (_buffer, _dict['tanque'], TERMINATOR)

        self.client.enviar(_buffer)
        retorno = self.client.recibir()

        print "ServerGameWidget:", retorno
        '''
        datos = self.__game_setup(datos)

        from Multiplayer.Juego import Juego

        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(datos, self.client)
        self.juego.config()

        self.game_thread = threading.Thread(target=self.juego.run, name='game')

        self.game_thread.start()
        '''
