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

        self.lista = Lista()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER)
        scroll.add_with_viewport(self.lista)

        self.add(scroll)
        self.show_all()

        self.set_size_request(150, -1)

    def update(self, _dict):
        self.lista.update(_dict)

class Lista(Gtk.TreeView):

    def __init__(self):

        Gtk.TreeView.__init__(self, Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_INT))

        self.players = {}

        self.set_property("rules-hint", True)
        self.set_headers_visible(False)

        self.__setear_columnas()
        self.show_all()

    def __setear_columnas(self):
        self.append_column(self.__construir_columa('Ip', 0, False))
        self.append_column(self.__construir_columa('Nick', 1, True))
        self.append_column(self.__construir_columa('Puntos', 2, True))

    def __construir_columa(self, text, index, visible):
        render = Gtk.CellRendererText()
        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            return False

        ip, nick, puntos = elementos[0]
        self.get_model().append([ip, nick, puntos])
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def agregar_items(self, elementos):
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def update(self, _dict):
        ips = _dict.keys()
        items = []
        for ip in ips:
            if not ip in self.players.keys():
                self.players[ip] = _dict[ip]
                item = (ip, self.players[ip]['nick'], self.players[ip]['puntos'])
                items.append(item)
            else:
                self.players[ip] = _dict[ip]

        if items:
            self.agregar_items(items)

        model = self.get_model()
        item = model.get_iter_first()
        _iter = None
        while item:
            _iter = item
            ip = model.get_value(_iter, 0)
            model.set_value(_iter, 1, self.players[ip]['nick'])
            model.set_value(_iter, 2, self.players[ip]['puntos'])
            item = model.iter_next(item)
        model.set_sort_column_id(2, Gtk.SortType.DESCENDING)
