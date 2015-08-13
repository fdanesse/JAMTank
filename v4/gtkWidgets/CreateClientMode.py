#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gobject

from SelectWidgets import Lista

IMGPATH = os.path.dirname(os.path.dirname(__file__))


class CreateClientMode(gtk.Dialog):

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
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_transient_for(top)

        for child in self.vbox.get_children():
            self.vbox.remove(child)
            child.destroy()
        create_client = CreateClient()
        create_client.connect("accion", self.__accion)
        self.vbox.pack_start(create_client, True, True, 0)
        self.show_all()

    def __accion(self, widget, accion, _dict):
        self.emit("accion", accion, _dict)
        self.destroy()


class CreateClient(gtk.EventBox):

    __gsignals__ = {
    "accion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,
        gobject.TYPE_PYOBJECT))}

    def __init__(self):

        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))

        self.game_dict = {
            'server': "",
            'nick': '',
            'tanque': "",
            }

        self.set_border_width(10)

        tabla = gtk.Table(columns=5, rows=6, homogeneous=True)
        tabla.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))

        self.framejuegos = FrameJuegos()
        tabla.attach_defaults(self.framejuegos, 0, 3, 0, 3)

        self.mapview = gtk.Image()
        tabla.attach_defaults(self.mapview, 3, 5, 3, 5)

        self.frametanque = FrameTanque()
        tabla.attach_defaults(self.frametanque, 0, 2, 3, 5)

        self.tanqueview = gtk.Image()
        tabla.attach_defaults(self.tanqueview, 2, 3, 4, 5)

        self.framenick = FrameNick()
        tabla.attach_defaults(self.framenick, 2, 5, 3, 4)

        button = gtk.Button("Cancelar")
        tabla.attach_defaults(button, 0, 1, 5, 6)
        button.connect("clicked", self.__accion, "salir")

        self.jugar = gtk.Button("Unirme")
        self.jugar.set_sensitive(False)
        self.jugar.connect("clicked", self.__accion, "run")
        tabla.attach_defaults(self.jugar, 4, 5, 5, 6)

        self.add(tabla)

        self.connect("realize", self.__do_realize)
        self.frametanque.lista.connect("nueva-seleccion", self.__seleccion_tanque)
        self.framenick.nick.connect("changed", self.__change_nick)

        self.show_all()

    def __do_realize(self, widget):
        elementos = []
        mapas_path = os.path.join(IMGPATH, "Tanques")
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

    def __accion(self, widget, accion):
        self.emit("accion", accion, dict(self.game_dict))

    def __check_dict(self):
        valor = True
        for item in self.game_dict.items():
            if not item[1]:
                valor = False
                break
        self.jugar.set_sensitive(valor)


class FrameTanque(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(4)
        self.set_label(" Selecciona tu Tanque: ")

        self.lista = Lista()

        event = gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.add(event)

        self.lista.set_headers_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(self.lista)
        event.add(scroll)

        self.show_all()


class FrameNick(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(4)
        self.set_label(" Escribe tu Apodo: ")

        event = gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.add(event)
        self.nick = gtk.Entry()
        self.nick.set_max_length(10)
        event.add(self.nick)

        self.show_all()


class FrameJuegos(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(4)
        self.set_label(" Juegos Creados: ")

        self.lista = Lista()

        event = gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.add(event)

        self.lista.set_headers_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(self.lista)
        event.add(scroll)

        self.show_all()
