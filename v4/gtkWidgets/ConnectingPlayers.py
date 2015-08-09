#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gobject
from SelectWidgets import Lista

ROOTPATH = os.path.dirname(os.path.dirname(__file__))


class ConnectingPlayers(gtk.Dialog):

    __gsignals__ = {
    "accion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self, top, nick, tanque, _dict):

        gtk.Dialog.__init__(self)

        print nick, tanque, _dict
        self.set_resizable(False)
        self.set_position(3)
        self.set_deletable(False)
        self.set_decorated(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_transient_for(top)

        for child in self.vbox.get_children():
            self.vbox.remove(child)
            child.destroy()
        internal_widget = InternalWidget()
        internal_widget.cancelar.connect("clicked", self.__accion)
        internal_widget.jugar.connect("clicked", self.__accion)
        self.vbox.pack_start(internal_widget, True, True, 0)

        self.show_all()

        rect = internal_widget.mapaview.get_allocation()
        path = os.path.join(ROOTPATH, "Mapas", _dict['mapa'])
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, -1, rect.height)
        internal_widget.mapaview.set_from_pixbuf(pixbuf)

    def __accion(self, widget):
        self.emit("accion", widget.get_label().lower())
        self.destroy()


class InternalWidget(gtk.EventBox):

    def __init__(self):

        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(15)

        self.jugadores = Lista()
        self.mapaview = gtk.Image()

        tabla = gtk.Table(columns=6, rows=5, homogeneous=True)
        tabla.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))

        frame = gtk.Frame()
        frame.set_label(" Jugadores: ")
        frame.set_border_width(4)
        event = gtk.EventBox()
        frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.set_border_width(4)
        frame.add(event)
        self.jugadores.set_headers_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.jugadores)
        event.add(scroll)
        tabla.attach_defaults(frame, 0, 3, 0, 6)

        event = gtk.EventBox()
        event.set_border_width(10)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.add(self.mapaview)
        tabla.attach_defaults(event, 3, 6, 0, 5)

        hbox = gtk.HBox()
        self.cancelar = gtk.Button("Cancelar")
        self.jugar = gtk.Button("Jugar")
        self.jugar.set_sensitive(False)
        hbox.pack_end(self.jugar, True, True, 0)
        hbox.pack_end(self.cancelar, True, True, 0)
        tabla.attach_defaults(hbox, 3, 6, 5, 6)

        self.add(tabla)
        self.show_all()
