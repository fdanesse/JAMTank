#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject

from Network.Client import Client
from Juego import Juego

MAKELOG = True

LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")
if os.path.exists(LOGPATH):
    os.remove(LOGPATH)


def WRITE_LOG(_dict):
    archivo = open(LOGPATH, "w")
    archivo.write(json.dumps(
        _dict, indent=4, separators=(", ", ":"), sort_keys=True))
    archivo.close()


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
        server = str(_dict['server'])
        tanque = os.path.basename(str(_dict['tanque']))
        nick = str(_dict['nick'])
        dirpath = os.path.dirname(os.path.dirname(str(_dict['tanque'])))

        self.client = Client(server)
        self.client.conectarse()

        _buffer = "JOIN,%s,%s" % (tanque, nick)

        self.client.enviar(_buffer)
        retorno = self.client.recibir()

        mapa = os.path.join(dirpath, "Mapas", retorno)
        tanque = str(_dict['tanque'])

        new_dict = {
            'tanque': tanque,
            'nick': nick,
            'mapa': mapa,
            }

        if MAKELOG:
            WRITE_LOG({'client': new_dict})

        if retorno == "CLOSE":
            print "FIXME: No se admiten más Jugadores"
        else:
            time.sleep(0.5)
            self.__run_game(new_dict)

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
