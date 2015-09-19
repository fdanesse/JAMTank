#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   CreateServerMode.py por:
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
from SelectWidgets import Lista
from SelectWidgets import OponentesSelectBox
from SelectWidgets import FrameNick
from SelectWidgets import FrameTanque
from Globales import get_ip
from Globales import set_font

BASE = os.path.dirname(os.path.dirname(__file__))


class CreateServerMode(gtk.Dialog):

    __gsignals__ = {
    "accion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,
        gobject.TYPE_PYOBJECT))}

    def __init__(self, top):

        gtk.Dialog.__init__(self)

        self.set_resizable(False)
        self.set_position(3)
        self.set_deletable(False)
        self.set_decorated(False)
        self.set_transient_for(top)

        for child in self.vbox.get_children():
            self.vbox.remove(child)
            child.destroy()
        create_server = CreateServer()
        create_server.connect("accion", self.__accion)
        self.vbox.pack_start(create_server, True, True, 0)

        self.show_all()

    def __accion(self, widget, accion, _dict):
        self.emit("accion", accion, _dict)


class CreateServer(gtk.EventBox):

    __gsignals__ = {
    "accion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,
        gobject.TYPE_PYOBJECT))}

    def __init__(self):

        gtk.EventBox.__init__(self)

        self.set_property("visible-window", False)

        self.game_dict = {
            'server': get_ip(),
            'nick': '',
            'mapa': "",
            'tanque': "",
            'enemigos': 2,
            'vidas': 5,
            }

        self.set_border_width(10)

        self.mapaview = gtk.Image()
        self.tanqueview = gtk.Image()
        self.oponentes = OponentesSelectBox()

        tabla = gtk.Table(columns=5, rows=6, homogeneous=True)

        self.framemapa = FrameMapa()
        tabla.attach_defaults(self.framemapa, 0, 2, 0, 3)

        self.frametanque = FrameTanque()
        tabla.attach_defaults(self.frametanque, 0, 2, 3, 5)

        event = gtk.EventBox()
        event.set_border_width(10)
        event.set_property("visible-window", False)
        event.add(self.mapaview)
        tabla.attach_defaults(event, 2, 5, 0, 3)

        tabla.attach_defaults(self.tanqueview, 2, 3, 4, 5)

        self.framenick = FrameNick()
        tabla.attach_defaults(self.framenick, 2, 5, 3, 4)

        event = gtk.EventBox()
        event.set_property("visible-window", False)
        event.set_border_width(4)
        event.add(self.oponentes)
        tabla.attach_defaults(event, 3, 5, 4, 5)

        button = gtk.Button("Cancelar")
        set_font(button.get_children()[0], "subtitulo1")
        tabla.attach_defaults(button, 0, 1, 5, 6)
        button.connect("clicked", self.__accion, "salir")

        self.jugar = gtk.Button("Crear")
        set_font(self.jugar.get_children()[0], "subtitulo1")
        self.jugar.set_sensitive(False)
        self.jugar.connect("clicked", self.__accion, "run")
        tabla.attach_defaults(self.jugar, 4, 5, 5, 6)

        self.add(tabla)

        self.connect("realize", self.__do_realize)
        self.framemapa.lista.connect(
            "nueva-seleccion", self.__seleccion_mapa)
        self.frametanque.lista.connect(
            "nueva-seleccion", self.__seleccion_tanque)
        self.oponentes.connect("valor", self.__seleccion_oponentes)
        self.framenick.nick.connect("changed", self.__change_nick)

        self.show_all()

    def __do_realize(self, widget):
        elementos = []
        mapas_path = os.path.join(BASE, "Mapas")
        for arch in sorted(os.listdir(mapas_path)):
            path = os.path.join(mapas_path, arch)
            archivo = os.path.basename(path)
            elementos.append([archivo, path])
        self.framemapa.lista.limpiar()
        self.framemapa.lista.agregar_items(elementos)
        elementos = []
        mapas_path = os.path.join(BASE, "Tanques")
        for arch in sorted(os.listdir(mapas_path)):
            path = os.path.join(mapas_path, arch)
            archivo = os.path.basename(path)
            elementos.append([archivo, path])
        self.frametanque.lista.limpiar()
        self.frametanque.lista.agregar_items(elementos)

    def __change_nick(self, widget):
        nick = widget.get_text().replace('\n', '').replace('\r', '')
        nick = nick.replace('*', '').replace(' ', '_').replace('|', '')
        self.game_dict['nick'] = nick
        self.__check_dict()

    def __seleccion_tanque(self, widget, path):
        rect = self.tanqueview.get_allocation()
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, -1, rect.height)
        self.tanqueview.set_from_pixbuf(pixbuf)
        self.game_dict['tanque'] = os.path.basename(path)
        self.__check_dict()

    def __seleccion_mapa(self, widget, path):
        rect = self.mapaview.get_allocation()
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, -1, rect.height)
        self.mapaview.set_from_pixbuf(pixbuf)
        self.game_dict['mapa'] = os.path.basename(path)
        self.__check_dict()

    def __seleccion_oponentes(self, widget, valor, tipo):
        if tipo == "oponentes":
            self.game_dict['enemigos'] = valor
        elif tipo == "vidas":
            self.game_dict['vidas'] = valor
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


class FrameMapa(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" Selecciona el Mapa: ")

        event = gtk.EventBox()
        event.set_property("visible-window", False)
        event.set_border_width(4)
        self.add(event)

        self.lista = Lista()
        self.lista.set_headers_visible(False)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(self.lista)
        event.add(scroll)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1")
