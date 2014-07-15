#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading

from gi.repository import Gtk
from gi.repository import GdkX11
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

        #self.game_thread = False
        #self.client_thread = False
        self.client = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        self.client = Client(str(_dict['server']))
        self.client.conectarse()
        #self.client_thread = threading.Thread(target=self.client.conectarse,
        #    name='client')
        #self.client_thread.setDaemon(True)
        #self.client_thread.start()

        _buffer = 'CONNECT*%s' % (TERMINATOR)
        self.client.enviar(_buffer)
        mensajes = self.client.recibir()
        for mensaje in mensajes:
            if mensaje.startswith('CONNECT*'):
                mapa, vidas = mensaje.replace('CONNECT*', "").split()
                dirpath = os.path.dirname(os.path.dirname(
                    str(_dict['tanque'])))
                _dict['mapa'] = os.path.join(dirpath, "Mapas", mapa)
                _dict['vidas'] = int(vidas)

                tanque = os.path.basename(str(_dict['tanque']))
                _buffer = ''
                _buffer = '%sN*%s%s' % (_buffer,
                    str(_dict['nick']), TERMINATOR)
                _buffer = '%sT*%s%s' % (_buffer, tanque, TERMINATOR)
                self.client.enviar(_buffer)
                retorno = self.client.recibir()

                time.sleep(0.5)
                self.__run_game(dict(_dict))
                return False
            if mensaje.startswith('CLOSE*'):
                # FIXME: Si llega hasta acá, no se puede lanzar el juego
                print "FIXME: El Servidor no admite mas Jugadores"
                return False
        # FIXME: Si llega hasta acá, no se puede lanzar el juego
        print "Este mensaje no corresponde en esta instancia de cliente"
        print mensajes
        return False

    def __run_game(self, _dict):
        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(dict(_dict), self.client)
        self.juego.config()
        time.sleep(0.5)
        self.juego.run()
        #self.game_thread = threading.Thread(
        #    target=self.juego.run, name='game')
        #self.game_thread.setDaemon(True)
        #self.game_thread.start()

    def setup_init(self, _dict):
        self.__run_client(dict(_dict))
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
