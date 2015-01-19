#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   ClientGameWidget.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import time

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject
from gi.repository import GLib

from Network.Client import Client
from Juego import Juego
from Widgets import Derecha
from DialogoEndGame import DialogoEndGame

from Globales import MAKELOG
from Globales import APPEND_LOG

if MAKELOG:
    from Globales import reset_log
    reset_log()


class GameWidget(Gtk.Paned):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Paned.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.drawing = DrawingWidget()
        self.derecha = Derecha()

        self.pack1(self.drawing, resize=True, shrink=False)
        self.pack2(self.derecha, resize=False, shrink=False)

        self.show_all()

        self.drawing.connect("update", self.__update_players)
        self.drawing.connect('salir', self.__re_emit_salir)

        # FIXME: Necesario
        self.set_sensitive(False)

    def __update_players(self, widget, _dict):
        self.derecha.update(_dict)

    def __re_emit_salir(self, widget):
        self.emit('salir')

    def setup_init(self, _dict):
        from Globales import get_ip
        ip = get_ip()
        server = str(_dict['server'])
        tanque = str(_dict['tanque'])
        self.derecha.set_data(ip, server, tanque)
        self.drawing.setup_init(_dict)

    def update_events(self, eventos):
        self.drawing.update_events(eventos)

    def salir(self):
        self.drawing.salir()


class DrawingWidget(Gtk.DrawingArea):

    __gsignals__ = {
    "update": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.client = False
        self.juego = False

        self.show_all()
        self.set_size_request(640, 480)

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

    def __end_game(self, juego, _dict):
        """
        El juego recibe salir desde el server.
        """
        dialog = DialogoEndGame(parent=self.get_toplevel(), _dict=_dict)
        self.emit('salir')
        dialog.run()
        dialog.destroy()

    def __run_game(self, _dict):
        """
        Comienza a correr el Juego.
        """
        try:
            # FIXME: Agregar Dialogo con explicacion sobre teclas
            xid = self.get_property('window').get_xid()
            os.putenv('SDL_WINDOWID', str(xid))
            self.juego = Juego(dict(_dict), self.client)
            self.juego.connect("end", self.__end_game)
            self.juego.connect("update", self.__update_players)
            self.juego.config()
            time.sleep(0.5)
            self.juego.run()
        except:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Juego no pudo Iniciar.")
            dialog.run()
            self.salir()

    def __update_players(self, juego, _dict):
        self.emit("update", _dict)

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
        dialog = Dialogo(parent=self.get_toplevel(),
            text="Saliendo del Juego . . .")
        dialog.run()
        dialog.destroy()
        self.emit('salir')


class Dialogo(Gtk.Dialog):

    def __init__(self, parent=None, text=""):

        Gtk.Dialog.__init__(self,
            parent=parent,
            flags=Gtk.DialogFlags.MODAL)

        self.set_decorated(False)
        self.set_border_width(20)

        label = Gtk.Label(text)
        label.show()

        self.vbox.pack_start(label, True, True, 5)

        self.connect("realize", self.__do_realize)

    def __do_realize(self, widget):
        GLib.timeout_add(3000, self.__destroy)

    def __destroy(self):
        self.destroy()
        return False
