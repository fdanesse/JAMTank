#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading

from gi.repository import Gtk
from gi.repository import GdkX11

TERMINATOR = "\r\n\r\n"


def get_image_string(path):

    import base64

    pixbuf_file = open(path, 'rb')
    image_string = base64.b64encode(
        pixbuf_file.read())
    pixbuf_file.close()

    return image_string


class GameWidget(Gtk.DrawingArea):

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.juego = False
        self.client = False
        self.client_thread = False
        self.game_thread = False
        self.server_thread = False

        self.show_all()

    def do_draw(self, context):

        rect = self.get_allocation()

        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def setup_init(self, datos):

        tipo = datos.get('tipo', False)

        if tipo == 'single':
            from SinglePlayer.Juego import Juego

            xid = self.get_property('window').get_xid()
            os.putenv('SDL_WINDOWID', str(xid))

            self.juego = Juego(datos)
            self.juego.config()

            self.game_thread = threading.Thread(
                target=self.juego.run,
                name='game')

            self.game_thread.start()

        elif tipo == 'multi':
            # SERVER
            from Multiplayer.Server import Server
            from Multiplayer.Server import RequestHandler

            server = Server(
                ("192.168.1.9", 5000), RequestHandler)
            server.allow_reuse_address = True
            server.socket.setblocking(0)

            self.server_thread = threading.Thread(
                target=server.serve_forever,
                name='server')

            self.server_thread.setDaemon(True)
            self.server_thread.start()

            # CLIENT
            from Multiplayer.Client import Client
            self.client = Client('192.168.1.9')

            self.client_thread = threading.Thread(
                target=self.client.conectarse,
                name='client')

            #self.client_thread.setDaemon(False)
            self.client_thread.start()
            self.__game_setup(datos)

            # JUEGO
            from Multiplayer.Juego import Juego

            xid = self.get_property('window').get_xid()
            os.putenv('SDL_WINDOWID', str(xid))

            self.juego = Juego(datos)
            self.juego.config()

            self.game_thread = threading.Thread(
                target=self.juego.run,
                name='game')

            self.game_thread.start()

        elif tipo == 'join':
            print "conectarse a juego en red"

        '''
        for item in datos.items():
            print item
        '''

    def __game_setup(self, datos):
        """
        El host envia al server:
            mapa
            enemigos
            vidas
        """

        mensaje = "M*%s%s" % (
            datos['mapa'], TERMINATOR)
        mensaje = "%sE*%s%s" % (
            mensaje, datos['enemigos'], TERMINATOR)
        mensaje = "%sV*%s%s" % (
            mensaje, datos['vidas'], TERMINATOR)

        self.client.enviar(mensaje)
        self.client.recibir()
