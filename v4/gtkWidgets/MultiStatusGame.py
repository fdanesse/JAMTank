#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   MultiStatusGame.py por:
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
from WidgetsGenerales import FrameVolumen
from WidgetsGenerales import FrameProgress
from Globales import set_font

BASE = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


class MultiDialogoEndGame(gtk.Dialog):

    def __init__(self, parent=None, _dict={}):

        gtk.Dialog.__init__(self, parent=parent,
        buttons=("Salir", gtk.RESPONSE_CANCEL))

        self.set_decorated(False)
        self.set_border_width(15)

        self._ranking = Ranking()
        self.vbox.pack_start(self._ranking, True, True, 5)

        self._ranking._lista.update(_dict)
        self.vbox.show_all()
        self.set_sensitive(False)
        gobject.timeout_add(4000, self.__sensitive)

    def __sensitive(self):
        self.set_sensitive(True)
        return False


class MultiStatusGame(gtk.Window):

    __gsignals__ = {
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, gobject.TYPE_STRING))}

    def __init__(self, top, screen_wh, ip, vidas):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        self._ip = ip
        w, h = screen_wh
        self.set_size_request(w / 4, h)
        self.set_resizable(False)
        self.move(w / 4 * 3, 0)
        self.set_deletable(False)
        self.set_transient_for(top)

        self._ranking = Ranking()
        self._volumenes = FrameVolumen()
        self._framejugador = FrameJugador(vidas)
        image = gtk.Image()
        path = os.path.join(BASE, "Iconos", "teclas.svg")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, w / 4 / 3 * 2, -1)
        image.set_from_pixbuf(pixbuf)

        vbox = gtk.VBox()
        vbox.pack_start(self._ranking, False, False, 0)
        vbox.pack_start(image, True, True, 0)
        vbox.pack_end(self._framejugador, False, False, 0)
        vbox.pack_end(self._volumenes, False, False, 0)
        self.add(vbox)
        self.show_all()

        self._volumenes.connect("volumen", self.__emit_volumen)

    def __emit_volumen(self, widget, valor, text):
        self.emit("volumen", valor, text)

    def update(self, juego, _dict):
        self._ranking._lista.update(_dict)
        self._framejugador.update(_dict.get(self._ip))


class Ranking(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" Ranking ")
        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)
        self._lista = Lista()
        event.add(self._lista)
        self.add(event)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")


class Lista(gtk.TreeView):

    def __init__(self):

        gtk.TreeView.__init__(self, gtk.ListStore(gobject.TYPE_STRING,
            gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_INT))

        self.set_property("rules-hint", True)
        self.set_headers_clickable(False)
        self.set_headers_visible(False)
        self.__setear_columnas()
        self.get_model().set_sort_column_id(4, gtk.SORT_DESCENDING)
        self.show_all()

    def __setear_columnas(self):
        self.append_column(self.__construir_columa("Ip", 0, False))
        self.append_column(self.__construir_columa_icono("Tanque", 1, True))
        self.append_column(self.__construir_columa("Path", 2, False))
        self.append_column(self.__construir_columa("Nombre", 3, True))
        self.append_column(self.__construir_columa("Puntos", 4, True))

    def __construir_columa(self, text, index, visible):
        render = gtk.CellRendererText()
        columna = gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property("visible", visible)
        columna.set_property("resizable", False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __construir_columa_icono(self, text, index, visible):
        render = gtk.CellRendererPixbuf()
        columna = gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property("visible", visible)
        columna.set_property("resizable", False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            return False
        ip, pixbuf, path, nick, puntos = elementos[0]
        self.get_model().append([ip, pixbuf, path, nick, puntos])
        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def __buscar(self, texto):
        model = self.get_model()
        _iter = model.get_iter_first()
        while _iter:
            contenido = model.get_value(_iter, 0)
            if texto == contenido:
                return _iter
            _iter = model.iter_next(_iter)
        return None

    def agregar_items(self, elementos):
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def update(self, _dict):
        try:
            items = []
            for ip in _dict.keys():
                _iter = self.__buscar(ip)
                if _iter:
                    model = self.get_model()
                    model.set_value(_iter, 4, _dict[ip]["s"]["p"])
                else:
                    nick = _dict[ip]["n"]
                    puntos = _dict[ip]["s"]["p"]
                    path = os.path.join(BASE, "Tanques", _dict[ip]["t"])
                    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 50, -1)
                    items.append([ip, pixbuf, path, nick, puntos])
            self.agregar_items(items)
        except:
            print "ERROR:", self.update, _dict


class FrameJugador(gtk.Frame):

    def __init__(self, vidas):

        gtk.Frame.__init__(self)

        self._max_vidas = vidas
        self.set_border_width(4)
        self.set_label(" Jugador ")

        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)

        self._preview = gtk.Image()
        self._energia = FrameProgress("Energía:")
        self._vidas = FrameProgress("Vidas:")

        vbox = gtk.VBox()
        vbox.pack_start(self._preview, False, False, 0)
        vbox.pack_start(self._energia, False, False, 0)
        vbox.pack_start(self._vidas, False, False, 0)

        event.add(vbox)
        self.add(event)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")

    def update(self, _dict):
        try:
            nick = _dict["n"]
            if self.get_label() != nick:
                self.set_label(" %s " % nick)
                path = os.path.join(BASE, "Tanques", _dict["t"])
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 80, -1)
                self._preview.set_from_pixbuf(pixbuf)
            self._energia.update(100, _dict["s"]["e"])
            self._vidas.update(self._max_vidas, _dict["s"]["v"])
        except:
            print "ERROR:", self.update, _dict
