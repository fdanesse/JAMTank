#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SelectClient.py por:
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
from gi.repository import GdkPixbuf
from gi.repository import GObject

from SelectWidgets import Lista

BASE = os.path.dirname(__file__)

"""
Permite Elegir Opciones del Juego:
    self.game_dict = {
        'nick': "",
        'tanque': "",
        'server': ""
        }

    emit("accion", accion, self.game_dict)
"""


class SelectClient(Gtk.EventBox):

    __gsignals__ = {
    "accion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,
        GObject.TYPE_PYOBJECT))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        #self.temp_path = "    mp/jamtank_intro_img.png"
        #self.imagen = False

        self.game_dict = {
            'nick': "",
            'tanque': "",
            'server': ""
            }

        self.set_border_width(10)

        self.lista_tanques = Lista()
        self.tanqueview = Gtk.Image()

        tabla = Gtk.Table(columns=4, rows=6, homogeneous=True)

        frame = Gtk.Frame()
        frame.set_label(" Selecciona tu Tanque: ")
        frame.set_border_width(4)
        event = Gtk.EventBox()
        event.set_border_width(4)
        frame.add(event)
        self.lista_tanques.set_headers_visible(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista_tanques)
        event.add(scroll)
        tabla.attach_defaults(frame, 0, 2, 0, 4)

        frame = Gtk.Frame()
        frame.set_label(" Escribe la Ip del Servidor: ")
        frame.set_border_width(4)
        event = Gtk.EventBox()
        event.set_border_width(4)
        frame.add(event)
        server = Gtk.Entry()
        server.connect("changed", self.__change_server)
        event.add(server)
        tabla.attach_defaults(frame, 2, 4, 0, 1)

        frame = Gtk.Frame()
        frame.set_label(" Escribe tu Apodo: ")
        frame.set_border_width(4)
        event = Gtk.EventBox()
        event.set_border_width(4)
        frame.add(event)
        nick = Gtk.Entry()
        nick.set_max_length(10)
        nick.connect("changed", self.__change_nick)
        event.add(nick)
        tabla.attach_defaults(frame, 2, 4, 1, 2)

        tabla.attach_defaults(self.tanqueview, 2, 4, 3, 4)

        button = Gtk.Button("Cancelar")
        tabla.attach_defaults(button, 0, 1, 5, 6)
        button.connect("clicked", self.__accion, "salir")

        self.jugar = Gtk.Button("Jugar")
        self.jugar.set_sensitive(False)
        self.jugar.connect("clicked", self.__accion, "run")
        tabla.attach_defaults(self.jugar, 3, 4, 5, 6)

        self.add(tabla)

        self.connect("realize", self.__do_realize)
        self.lista_tanques.connect("nueva-seleccion", self.__seleccion_tanque)

        self.show_all()

    ''' FIXME: Pinta el fondo, no lo uso
    def __do_draw(self, widget, context):
        rect = widget.get_allocation()

        src = self.imagen.copy()
        dst = GdkPixbuf.Pixbuf.new_from_file_at_size(
            self.temp_path, rect.width, rect.height)

        GdkPixbuf.Pixbuf.scale(src, dst, 0, 0, 100, 100, 0, 0, 1.5, 1.5,
            GdkPixbuf.InterpType.BILINEAR)

        x = rect.width / 2 - dst.get_width() / 2
        y = rect.height / 2 - dst.get_height() / 2

        Gdk.cairo_set_source_pixbuf(context, dst, x, y)
        context.paint()
    '''

    def __do_realize(self, widget):
        elementos = []
        mapas_path = os.path.join(BASE, "Tanques")

        for arch in sorted(os.listdir(mapas_path)):
            path = os.path.join(mapas_path, arch)
            archivo = os.path.basename(path)
            elementos.append([archivo, path])

        self.lista_tanques.limpiar()
        self.lista_tanques.agregar_items(elementos)

    def __change_nick(self, widget):
        nick = widget.get_text().replace('\n', '').replace('\r', '')
        nick = nick.replace('*', '').replace(' ', '_').replace('|', '')
        self.game_dict['nick'] = nick
        self.__check_dict()

    def __change_server(self, widget):
        server = widget.get_text().strip()
        valida = True
        num = server.split(".")
        if len(num) == 4:
            for n in num:
                try:
                    nu = int(n)
                    if nu > 0 and nu < 255 and nu != 127:
                        pass
                    else:
                        valida = False
                        break
                    valida = True
                except:
                    valida = False
                    break
        if valida:
            self.game_dict['server'] = server
        else:
            self.game_dict['server'] = ""
        self.__check_dict()

    def __seleccion_tanque(self, widget, path):
        rect = self.tanqueview.get_allocation()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, -1, rect.height)
        self.tanqueview.set_from_pixbuf(pixbuf)
        self.game_dict['tanque'] = path
        self.__check_dict()

    def __accion(self, widget, accion):
        self.emit("accion", accion, dict(self.game_dict))

    def __check_dict(self):
        valor = True
        for item in self.game_dict.items():
            if not item[1]:
                valor = False
                break
        self.jugar.set_sensitive(valor)

    ''' FIXME: Pinta el fondo, no lo uso
    def load(self, path):
        """
        Carga una imagen para pintar el fondo.
        """
        if path:
            if os.path.exists(path):
                self.imagen = GdkPixbuf.Pixbuf.new_from_file(path)
                self.imagen.savev(self.temp_path, "png", [], [])
                self.set_size_request(-1, -1)
        self.get_child().connect("draw", self.__do_draw)
    '''
