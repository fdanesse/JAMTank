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

        self.set_border_width(5)

        self._dict = {}
        self.lista = Lista()
        self.energia = Progreso()
        self.vidas = Progreso()
        self.preview = PreviewTank()
        self.server = Gtk.Label("111.111.111.111")
        self.client = Gtk.Label("111.111.111.111")

        vbox = Gtk.VBox()

        frame = Gtk.Frame()
        frame.set_label(" Servidor ")
        frame.set_label_align(0.5, 0.5)
        frame.add(self.server)
        vbox.pack_start(frame, False, True, 0)

        frame = Gtk.Frame()
        frame.set_label(" Cliente ")
        frame.set_label_align(0.5, 0.5)
        frame.add(self.client)
        vbox.pack_start(frame, False, True, 0)

        frame = Gtk.Frame()
        frame.set_label(" Jugadores ")
        frame.set_label_align(0.5, 0.5)
        frame.add(self.lista)
        vbox.pack_start(frame, True, True, 0)

        frame = Gtk.Frame()
        frame.set_label(" Vidas ")
        frame.set_label_align(0.5, 0.5)
        frame.add(self.vidas)
        vbox.pack_end(frame, False, True, 0)

        frame = Gtk.Frame()
        frame.set_label(" Energía ")
        frame.set_label_align(0.5, 0.5)
        frame.add(self.energia)
        vbox.pack_end(frame, False, True, 0)

        frame = Gtk.Frame()
        frame.set_label(" Tanque ")
        frame.set_label_align(0.5, 0.5)
        frame.add(self.preview)
        vbox.pack_end(frame, False, True, 0)

        self.add(vbox)
        self.show_all()

        self.set_size_request(150, -1)

    def update(self, _dict):
        if not self._dict:
            self._dict['vidas'] = _dict[self.client.get_text()]['vidas']
            self._dict['energia'] = _dict[self.client.get_text()]['energia']
        self.lista.update(_dict)
        maximo_e = self._dict['energia']
        val_e = _dict[self.client.get_text()]['energia']
        maximo_v = self._dict['vidas']
        val_v = _dict[self.client.get_text()]['vidas']
        self.energia.set_progress(100 * val_e / maximo_e)
        self.vidas.set_progress(100 * val_v / maximo_v)

    def set_data(self, ip, server, tanque):
        self.server.set_text(server)
        self.client.set_text(ip)
        self.preview.set_imagen(tanque)


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


class Progreso(Gtk.EventBox):
    """
    Barra de progreso para mostrar energia.
    """

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.escala = ProgressBar(
            Gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))

        self.valor = 0

        self.add(self.escala)
        self.show_all()

        self.set_size_request(-1, 30)
        self.set_progress(0)

    def set_progress(self, valor=0):
        if self.valor != valor:
            self.valor = valor
            self.escala.ajuste.set_value(valor)
            self.escala.queue_draw()


class ProgressBar(Gtk.Scale):

    def __init__(self, ajuste):

        Gtk.Scale.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.ajuste = ajuste
        self.set_digits(0)
        self.set_draw_value(False)

        self.borde = 10

        self.show_all()

    def do_draw(self, contexto):
        rect = self.get_allocation()
        w, h = (rect.width, rect.height)

        # Relleno de la barra
        ww = w - self.borde * 2
        hh = h - self.borde * 2
        Gdk.cairo_set_source_color(contexto, Gdk.Color(0, 0, 0))
        rect = Gdk.Rectangle()
        rect.x, rect.y, rect.width, rect.height = (
            self.borde, self.borde, ww, hh)
        Gdk.cairo_rectangle(contexto, rect)
        contexto.fill()

        # Relleno de la barra segun progreso
        Gdk.cairo_set_source_color(contexto, Gdk.Color(23000, 41000, 12000))
        rect = Gdk.Rectangle()

        ximage = int(self.ajuste.get_value() * ww / 100)
        rect.x, rect.y, rect.width, rect.height = (self.borde, self.borde,
            ximage, hh)

        Gdk.cairo_rectangle(contexto, rect)
        contexto.fill()

        return True


class PreviewTank(Gtk.DrawingArea):

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.temp_path = "/dev/shm/prev.png"
        self.imagen = False
        self.connect('draw', self.__do_draw)
        self.show_all()

        self.set_size_request(-1, 80)

    def set_imagen(self, path):
        self.imagen = GdkPixbuf.Pixbuf.new_from_file(path)
        self.imagen.savev(self.temp_path, "png", [], [])
        self.queue_draw()

    def __do_draw(self, widget, context):
        if not self.imagen:
            return

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
