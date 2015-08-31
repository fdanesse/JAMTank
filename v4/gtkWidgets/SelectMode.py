#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SelectMode.py por:
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
import gtk
import gobject
from gtkWidgets.SelectWidgets import DialogoSalir


class SelectMode(gtk.Window):

    __gsignals__ = {
    "switch": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self, top):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        self.set_resizable(False)
        self.set_position(3)
        self.set_deletable(False)
        self.set_decorated(False)
        self.set_border_width(15)
        self.set_transient_for(top)

        vbox = gtk.VBox()
        boton = gtk.Button("Jugar Solo")
        boton.connect("clicked", self.__emit_switch, "solo")
        vbox.pack_start(boton, False, False, 0)
        boton.set_sensitive(False)

        boton = gtk.Button("Crear en Red")
        boton.connect("clicked", self.__emit_switch, "red")
        vbox.pack_start(boton, False, False, 0)

        boton = gtk.Button("Unirse en Red")
        boton.connect("clicked", self.__emit_switch, "join")
        vbox.pack_start(boton, False, False, 0)

        boton = gtk.Button("Creditos")
        boton.connect("clicked", self.__emit_switch, "creditos")
        vbox.pack_start(boton, False, False, 0)
        boton.set_sensitive(False)

        boton = gtk.Button("Salir")
        boton.connect("clicked", self.__emit_switch, "salir")
        vbox.pack_start(boton, False, False, 0)

        self.add(vbox)
        self.show_all()

    def __emit_switch(self, widget, valor):
        if valor == "salir":
            self.hide()
            dialog = DialogoSalir(parent=self,
                text="¿Confirmas que Deseas Salir de JAMTank?")
            ret = dialog.run()
            dialog.destroy()
            if ret == gtk.RESPONSE_ACCEPT:
                self.emit("switch", valor)
            else:
                self.show()
        else:
            self.emit("switch", valor)
