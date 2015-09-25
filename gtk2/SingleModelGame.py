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
import random
random.seed()
from gtkWidgets.WidgetsGenerales import DialogoSalir
from SingleplayerGame.Juego import Juego

BASE_PATH = os.path.realpath(os.path.dirname(__file__))


def make_dict():
    TANQUES = {
        0: "t1.png",
        1: "t3.png",
        2: "t4.png",
        3: "t8.png",
        4: "t9.png",
        5: "t7.png",
        6: "t2.png",
        7: "t6.png",
        }
    NIVELES = {
        1: {"mapa": "001.png", "enemigos": [0]},
        2: {"mapa": "002.png", "enemigos": [0, 0]},
        3: {"mapa": "003.png", "enemigos": [0, 0, 1]},
        4: {"mapa": "004.png", "enemigos": [0, 0, 1, 1]},
        5: {"mapa": "005.png", "enemigos": [0, 0, 1, 1, 2]},
        6: {"mapa": "006.png", "enemigos": [0, 0, 1, 1, 2, 2]},
        7: {"mapa": "007.png", "enemigos": [0, 1, 1, 1, 2, 2]},
        8: {"mapa": "008.png", "enemigos": [0, 1, 1, 2, 2, 3]},
        9: {"mapa": "009.png", "enemigos": [1, 1, 1, 2, 2, 3]},
        10: {"mapa": "010.png", "enemigos": [7, 6, 1]},
        11: {"mapa": "011.png", "enemigos": [7, 6, 3]},
        12: {"mapa": "012.png", "enemigos": [7, 4, 3, 2]},
        13: {"mapa": "013.png", "enemigos": [5, 4, 3, 2, 1, 0]},
        14: {"mapa": "014.png", "enemigos": [5, 4, 3, 2, 1, 1]},
        15: {"mapa": "015.png", "enemigos": [6, 5, 4, 3, 0]},
        16: {"mapa": "016.png", "enemigos": [7, 5, 4, 3, 1]},
        17: {"mapa": "017.png", "enemigos": [7, 6, 5, 4, 3]},
        18: {"mapa": "018.png", "enemigos": [7, 6, 5, 4, 3, 1, 1, 0]},
        }
    DICT = {}
    for k in NIVELES.keys():
        DICT[k] = {}
        DICT[k]["mapa"] = NIVELES[k]["mapa"]
        DICT[k]["tanque"] = "t5.png"
        ene = []
        dif = 0
        for e in NIVELES[k]["enemigos"]:
            ene.append([TANQUES[e], e])
            dif += e+1
        DICT[k]["enemigos"] = ene
    return DICT


DICT = make_dict()


def get_data_game(index):
    mapa = os.path.join(BASE_PATH, "Mapas", DICT[index]["mapa"])
    tanque = os.path.join(BASE_PATH, "Tanques", DICT[index]["tanque"])
    enemigos = []
    for enemigo in DICT[index]["enemigos"]:
        enemigos.append([os.path.join(BASE_PATH, "Tanques", enemigo[0]),
            enemigo[1]])
    return (mapa, tanque, enemigos)


class SingleModelGame(gobject.GObject):

    __gsignals__ = {
    "error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    "end-game": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, topwin):

        gobject.GObject.__init__(self)

        self._topwin = topwin
        self.index = 1
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
                self.juego.pausar()
                ret = dialog.run()
                dialog.destroy()
                if ret == gtk.RESPONSE_ACCEPT:
                    self.eventos = ["Escape"]
                elif ret == gtk.RESPONSE_CANCEL:
                    self.eventos = []
                    self.juego.reactivar()
            try:
                self.juego.update_events(self.eventos)
            except:
                print "Error:", self.process_key_press
        else:
            if nombre == "Escape":
                self.emit("error")

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
        if not self.index in DICT.keys():
            self.index = 1
        mapa, tanque, enem = get_data_game(self.index)
        self.juego.load(mapa, tanque, enem)
        self.juego.run()

    def __exit_game(self, game, _dict):
        if self.juego:
            self.juego.disconnect_by_func(self.__exit_game)
            del(self.juego)
            self.juego = False
            time.sleep(0.5)
        self.emit("end-game", _dict)
