#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
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
from gi.repository import GLib

BASE_PATH = os.path.dirname(__file__)


class Derecha(Gtk.EventBox):

    def __init__(self):

        Gtk.EventBox.__init__(self)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER)
        scroll.add_with_viewport(Lista())

        self.add(scroll)
        self.show_all()

        self.set_size_request(150, -1)


class Lista(Gtk.TreeView):

    def __init__(self):

        Gtk.TreeView.__init__(self, Gtk.ListStore(
            GdkPixbuf.Pixbuf,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING))

        self.set_property("rules-hint", True)
        #self.set_headers_clickable(True)
        self.set_headers_visible(False)

        self.__setear_columnas()
        self.show_all()

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('', 0, True))
        self.append_column(self.__construir_columa('Nombre', 1, True))
        self.append_column(self.__construir_columa('', 2, False))

    def __construir_columa(self, text, index, visible):
        render = Gtk.CellRendererText()
        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __construir_columa_icono(self, text, index, visible):
        render = Gtk.CellRendererPixbuf()
        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def limpiar(self):
        self.get_model().clear()

    def agregar_items(self, elementos):
        self.get_toplevel().set_sensitive(False)
        self.permitir_select = False
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            return False

        texto, path = elementos[0]
        icono = None

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, 24, -1)
        self.get_model().append([pixbuf, texto, path])
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False
