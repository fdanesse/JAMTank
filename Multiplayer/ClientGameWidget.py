#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import codecs

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject
from gi.repository import GLib

from Network.Client import Client
from Juego import Juego

MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")


def WRITE_LOG(_dict):
    archivo = open(LOGPATH, "w")
    archivo.write(json.dumps(
        _dict, indent=4, separators=(", ", ":"), sort_keys=True))
    archivo.close()


def APPEND_LOG(_dict):
    new = {}
    if os.path.exists(LOGPATH):
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
        connected = self.client.conectarse()

        if connected:
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
                APPEND_LOG({'client': new_dict})

            if retorno == "CLOSE":
                dialog = Dialogo(parent=self.get_toplevel(),
                    text="El Servidor no Admite más Jugadores.")
                dialog.run()
                self.salir()
            else:
                time.sleep(0.5)
                self.__run_game(new_dict)

        else:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Cliente no pudo Conectarse con el Servidor.")
            dialog.run()
            self.salir()

    def __end_game(self, juego):
        """
        El juego recibe salir desde el server pues host ha salido del juego.
        """
        self.emit('salir')

    def __run_game(self, _dict):
        """
        Comienza a correr el Juego.
        """
        try:
            xid = self.get_property('window').get_xid()
            os.putenv('SDL_WINDOWID', str(xid))
            self.juego = Juego(dict(_dict), self.client)
            self.juego.connect("end", self.__end_game)
            self.juego.config()
            time.sleep(0.5)
            self.juego.run()
        except:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Juego no pudo Iniciar.")
            dialog.run()
            self.salir()

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
            self.juego.salir("REMOVE,")
            time.sleep(0.5)
            del(self.juego)
            self.juego = False
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False
        self.emit('salir')


class Dialogo(Gtk.Dialog):

    def __init__(self, parent=None, text=""):

        Gtk.Dialog.__init__(self,
            parent=parent,
            flags=Gtk.DialogFlags.MODAL)

        #self.set_decorated(False)
        #self.modify_bg(0, get_colors("window"))
        self.set_border_width(15)

        label = Gtk.Label(text)
        label.show()

        self.vbox.pack_start(label, True, True, 5)

        self.connect("realize", self.__do_realize)

    def __do_realize(self, widget):
        GLib.timeout_add(2000, self.__destroy)

    def __destroy(self):
        self.destroy()
        return False
