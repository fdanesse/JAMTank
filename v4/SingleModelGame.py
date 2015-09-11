#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SingleModelGame.py por:
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
import gobject
import gtk
import time
from gtkWidgets.SelectWidgets import DialogoSalir
from SingleplayerGame.Juego import Juego

BASE_PATH = os.path.realpath(os.path.dirname(__file__))
DICT = {
    0: {
        "mapa": "f1.png",
        "tanque": "t1.png",
        "enemigos": ["t2.png", "t2.png"]}
    }

class SingleModelGame(gobject.GObject):

    __gsignals__ = {
    #"error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    #"players": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
    #    (gobject.TYPE_PYOBJECT, )),
    #"play-run": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    "end-game": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, topwin):

        gobject.GObject.__init__(self)

        self._topwin = topwin
        self.juego = False
        self.eventos = []

    def process_key_press(self, event):
        nombre = gtk.gdk.keyval_name(event.keyval)
        if self.juego:
            teclas = ["w", "s", "d", "a", "space", "Escape"]
            if nombre in teclas and not nombre in self.eventos:
                if nombre == "w" and "s" in self.eventos:
                    self.eventos.remove("s")
                elif nombre == "s" and "w" in self.eventos:
                    self.eventos.remove("w")
                elif nombre == "d" and "a" in self.eventos:
                    self.eventos.remove("a")
                elif nombre == "a" and "d" in self.eventos:
                    self.eventos.remove("d")
                self.eventos.append(nombre)
            if "Escape" in self.eventos:
                dialog = DialogoSalir(parent=self._topwin,
                text="¿Abandonas el Juego?")
                self.juego._jugador.pausar()
                ret = dialog.run()
                dialog.destroy()
                if ret == gtk.RESPONSE_ACCEPT:
                    self.eventos = ["Escape"]
                elif ret == gtk.RESPONSE_CANCEL:
                    self.eventos = []
                    self.juego._jugador.reactivar()
            try:
                self.juego.update_events(self.eventos)
            except:
                print "Error:", self.process_key_press
        else:
            if nombre == "Escape":
                #self.emit("error")
                pass

    def process_key_release(self, event):
        if self.juego:
            nombre = gtk.gdk.keyval_name(event.keyval)
            teclas = ["w", "s", "d", "a", "space", "Escape"]
            if nombre in teclas and nombre in self.eventos:
                self.eventos.remove(nombre)
            try:
                self.juego.update_events(self.eventos)
            except:
                print "Error:", self.process_key_release
        else:
            self.eventos = []

    def rungame(self, xid, res):
        self.juego = Juego()
        self.juego.connect("exit", self.__exit_game)
        self.juego.config(res=res, xid=xid)
        mapa = os.path.join(BASE_PATH, "Mapas", DICT[0]["mapa"])
        tanque = os.path.join(BASE_PATH, "Tanques", DICT[0]["tanque"])
        self.juego.load(mapa, tanque)
        self.juego.run()

    def __exit_game(self, game, _dict):
        if self.juego:
            self.juego.disconnect_by_func(self.__exit_game)
            del(self.juego)
            self.juego = False
            time.sleep(0.5)
        self.emit("end-game", _dict)
