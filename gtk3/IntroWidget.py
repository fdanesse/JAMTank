#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   IntroWidget.py por:
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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject

"""
Contiene Opciones:
    Jugar Solo                  emit("switch", "solo")
    Crear Juego en Red          emit("switch", "red")
    Unirse a Juego Existente    emit("switch", "join")
    Creditos                    emit("switch", "creditos")
    Salir                       emit("switch", "salir")
"""


class IntroWidget(Gtk.Table):

    __gsignals__ = {
        "switch": (GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Table.__init__(self, rows=7, columns=3, homogeneous=True)

        self.imagen = False
        self.temp_path = "/dev/shm/jamtank_intro_img.png"

        boton = Gtk.Button("Jugar Solo")
        boton.connect("clicked", self.__emit_switch, "solo")
        self.attach(boton, 1, 2, 1, 2)
        boton.set_sensitive(False)

        boton = Gtk.Button("Crear en Red")
        boton.connect("clicked", self.__emit_switch, "red")
        self.attach(boton, 1, 2, 2, 3)

        boton = Gtk.Button("Unirse en Red")
        boton.connect("clicked", self.__emit_switch, "join")
        self.attach(boton, 1, 2, 3, 4)

        boton = Gtk.Button("Creditos")
        boton.connect("clicked", self.__emit_switch, "creditos")
        self.attach(boton, 1, 2, 4, 5)
        boton.set_sensitive(False)

        boton = Gtk.Button("Salir")
        boton.connect("clicked", self.__emit_switch, "salir")
        self.attach(boton, 1, 2, 5, 6)

        self.show_all()

    def __do_draw(self, widget, context):
        rect = self.get_allocation()
        src = self.imagen
        dst = GdkPixbuf.Pixbuf.new_from_file_at_size(
            self.temp_path, rect.width, rect.height)

        GdkPixbuf.Pixbuf.scale(src, dst, 0, 0, 100, 100, 0, 0, 1.5, 1.5,
            GdkPixbuf.InterpType.BILINEAR)

        x = rect.width / 2 - dst.get_width() / 2
        y = rect.height / 2 - dst.get_height() / 2

        Gdk.cairo_set_source_pixbuf(context, dst, x, y)
        context.paint()

    def __emit_switch(self, widget, valor):
        self.emit("switch", valor)

    def load(self, path):
        """
        Carga una imagen para pintar el fondo.
        """
        if path:
            if os.path.exists(path):
                self.imagen = GdkPixbuf.Pixbuf.new_from_file(path)
                self.imagen.savev(self.temp_path, "png", [], [])
                self.set_size_request(-1, -1)
        self.connect("draw", self.__do_draw)
