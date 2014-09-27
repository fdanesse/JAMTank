#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading
import json
import codecs

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject

from Network.Server import Server
from Network.Server import RequestHandler
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


def APPEND_LOG(_dict):
    archivo = codecs.open(LOGPATH, "r", "utf-8")
    new = json.JSONDecoder("utf-8").decode(archivo.read())
    archivo.close()
    for key in _dict.keys():
        new[key] = _dict[key]
    WRITE_LOG(new)


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
        server = str(_dict['server'])
        mapa = os.path.basename(str(_dict['mapa']))
        tanque = os.path.basename(str(_dict['tanque']))
        enemigos = str(_dict['enemigos'])
        vidas = str(_dict['vidas'])
        nick = str(_dict['nick'])

        self.client = Client(server)
        connected = self.client.conectarse()

        if connected:
            _buffer = "Config,%s,%s,%s,%s,%s" % (mapa, enemigos,
                vidas, tanque, nick)

            self.client.enviar(_buffer)
            retorno = self.client.recibir()

            if retorno == "OK":
                tanque = str(_dict['tanque'])
                mapa = str(_dict['mapa'])

                new_dict = {
                    'tanque': tanque,
                    'nick': nick,
                    'mapa': mapa,
                    }

                if MAKELOG:
                    APPEND_LOG({'client': new_dict})
                time.sleep(0.5)
                self.__run_game(new_dict)
            else:
                print "FIXME: Algo salió mal al configurar el Server."

        else:
            print "EL Cliente no pudo conectarse al socket"
            self.salir()

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

        if MAKELOG:
            WRITE_LOG({'server': _dict})
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
        # FIXME: El server debe avisar desconexion a todos los clientes
        self.server.shutdown()
        self.emit('salir')
