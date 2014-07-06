#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import GLib

from SelectWidgets import Lista
from SelectWidgets import OponentesSelectBox

from Globales import get_ip

BASE = os.path.dirname(__file__)

"""
Permite Elegir Opciones del Juego:
    self.game_dict = {
        'server': '',
        'nick': '',
        'mapa': "",
        'tanque': "",
        'enemigos': 1,
        'vidas': 10,
        }

    emit("accion", accion, self.game_dict)
"""


class SelectServer(Gtk.EventBox):

    __gsignals__ = {
    "accion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,
        GObject.TYPE_PYOBJECT))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.temp_path = "/tmp/jamtank_intro_img.png"
        self.imagen = False

        self.game_dict = {
            'server': '',
            'nick': '',
            'mapa': "",
            'tanque': "",
            'enemigos': 1,
            'vidas': 10,
            }

        self.modify_bg(0, Gdk.color_parse("#ffffff"))
        self.set_border_width(10)

        self.lista_mapas = Lista()
        self.lista_tanques = Lista()
        self.mapaview = Gtk.Image()
        self.tanqueview = Gtk.Image()
        self.oponentes = OponentesSelectBox()

        tabla = Gtk.Table(columns=5, rows=8, homogeneous=True)

        frame = Gtk.Frame()
        frame.set_label(" Selecciona el Mapa: ")
        frame.modify_bg(0, Gdk.color_parse("#ffffff"))
        frame.set_border_width(4)
        event = Gtk.EventBox()
        event.modify_bg(0, Gdk.color_parse("#ffffff"))
        event.set_border_width(4)
        frame.add(event)
        self.lista_mapas.set_headers_visible(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista_mapas)
        event.add(scroll)
        tabla.attach_defaults(frame, 0, 2, 0, 4)

        frame = Gtk.Frame()
        frame.set_label(" Selecciona tu Tanque: ")
        frame.modify_bg(0, Gdk.color_parse("#ffffff"))
        frame.set_border_width(4)
        event = Gtk.EventBox()
        event.modify_bg(0, Gdk.color_parse("#ffffff"))
        event.set_border_width(4)
        frame.add(event)
        self.lista_tanques.set_headers_visible(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista_tanques)
        event.add(scroll)
        tabla.attach_defaults(frame, 0, 2, 4, 7)

        event = Gtk.EventBox()
        event.modify_bg(0, Gdk.color_parse("#ffffff"))
        event.set_border_width(10)
        event.add(self.mapaview)
        tabla.attach_defaults(event, 2, 5, 0, 4)

        tabla.attach_defaults(self.tanqueview, 2, 3, 5, 6)

        frame = Gtk.Frame()
        frame.set_label(" Escribe tu Apodo: ")
        frame.modify_bg(0, Gdk.color_parse("#ffffff"))
        frame.set_border_width(4)
        event = Gtk.EventBox()
        event.modify_bg(0, Gdk.color_parse("#ffffff"))
        event.set_border_width(4)
        frame.add(event)
        nick = Gtk.Entry()
        nick.connect("changed", self.__change_nick)
        event.add(nick)
        tabla.attach_defaults(frame, 3, 5, 4, 5)

        event = Gtk.EventBox()
        event.modify_bg(0, Gdk.color_parse("#ffffff"))
        event.set_border_width(4)
        event.add(self.oponentes)
        tabla.attach_defaults(event, 3, 5, 5, 7)

        button = Gtk.Button("Cancelar")
        tabla.attach_defaults(button, 0, 1, 7, 8)
        button.connect("clicked", self.__accion, "salir")

        self.jugar = Gtk.Button("Jugar")
        self.jugar.set_sensitive(False)
        self.jugar.connect("clicked", self.__accion, "run")
        tabla.attach_defaults(self.jugar, 4, 5, 7, 8)

        self.add(tabla)

        self.connect("realize", self.__do_realize)
        self.lista_mapas.connect("nueva-seleccion", self.__seleccion_mapa)
        self.lista_tanques.connect("nueva-seleccion", self.__seleccion_tanque)
        self.oponentes.connect("valor", self.__seleccion_oponentes)

        self.show_all()

    ''' FIXME: Pinta el fondo, no lo uso
    def __do_draw(self, widget, context):
        rect = widget.get_allocation()

        src = self.imagen.copy()
        dst = GdkPixbuf.Pixbuf.new_from_file_at_size(
            self.temp_path, rect.width, rect.height)

        GdkPixbuf.Pixbuf.scale(
            src, dst, 0, 0, 100, 100,
            0, 0, 1.5, 1.5,
            GdkPixbuf.InterpType.BILINEAR)

        x = rect.width / 2 - dst.get_width() / 2
        y = rect.height / 2 - dst.get_height() / 2

        Gdk.cairo_set_source_pixbuf(context, dst, x, y)
        context.paint()
    '''

    def __do_realize(self, widget):
        elementos = []
        mapas_path = os.path.join(BASE, "Mapas")

        for arch in os.listdir(mapas_path):
            path = os.path.join(mapas_path, arch)
            archivo = os.path.basename(path)
            elementos.append([archivo, path])

        self.lista_mapas.limpiar()
        self.lista_mapas.agregar_items(elementos)

        elementos = []
        mapas_path = os.path.join(BASE, "Tanques")

        for arch in os.listdir(mapas_path):
            path = os.path.join(mapas_path, arch)
            archivo = os.path.basename(path)
            elementos.append([archivo, path])

        self.lista_tanques.limpiar()
        self.lista_tanques.agregar_items(elementos)

    def __change_nick(self, widget):
        self.game_dict['nick'] = widget.get_text()

    def __seleccion_tanque(self, widget, path):
        rect = self.tanqueview.get_allocation()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            path, -1, rect.height)
        self.tanqueview.set_from_pixbuf(pixbuf)
        self.game_dict['tanque'] = path

    def __seleccion_mapa(self, widget, path):
        rect = self.mapaview.get_allocation()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            path, -1, rect.height)
        self.mapaview.set_from_pixbuf(pixbuf)
        self.game_dict['mapa'] = path

    def __seleccion_oponentes(self, widget, valor, tipo):
        print valor, tipo
        if tipo == "oponentes":
            self.game_dict['enemigos'] = valor
        elif tipo == "vidas":
            self.game_dict['vidas'] = valor

    def __accion(self, widget, accion):
        self.emit("accion", accion, self.game_dict)

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
