#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject


class IntroWidget(Gtk.Table):

    __gsignals__ = {
        "switch": (GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Table.__init__(self, rows=7, columns=3, homogeneous=True)

        self.imagen_original = None
        self.image_path = None
        self.angulo = 0
        self.rotacion = GdkPixbuf.PixbufRotation.NONE
        self.zoom_valor = 0
        self.imagen = False
        self.temp_path = "/dev/shm/jamtank_intro_img.png"

        boton = Gtk.Button("Jugar Solo")
        boton.connect("clicked",
            self.__emit_switch, "solo")
        self.attach(
            boton,
            1, 2, 1, 2)

        boton = Gtk.Button("Crear Juego en Red")
        boton.connect("clicked",
            self.__emit_switch, "red")
        self.attach(
            boton,
            1, 2, 2, 3)

        boton = Gtk.Button("Unirse a Juego Existente")
        boton.connect("clicked",
            self.__emit_switch, "join")
        self.attach(
            boton,
            1, 2, 3, 4)

        boton = Gtk.Button("Creditos")
        boton.connect("clicked",
            self.__emit_switch, "creditos")
        self.attach(
            boton,
            1, 2, 4, 5)

        boton = Gtk.Button("Salir")
        boton.connect("clicked",
            self.__emit_switch, "salir")
        self.attach(
            boton,
            1, 2, 5, 6)

        self.show_all()

    def __emit_switch(self, widget, valor):

        self.emit("switch", valor)

    def load(self, path):
        """
        Carga una imagen.
        """

        if path:
            if os.path.exists(path):
                self.angulo = 0
                self.rotacion = GdkPixbuf.PixbufRotation.NONE
                self.zoom_valor = 0
                self.image_path = path
                self.imagen_original = GdkPixbuf.Pixbuf.new_from_file(path)
                self.imagen = self.imagen_original.copy()
                self.imagen.savev(self.temp_path, "png", [], [])

                self.set_size_request(-1, -1)

        self.connect("draw", self.__do_draw)

    def __do_draw(self, widget, context):

        if not self.image_path:
            return

        rect = self.get_allocation()

        src = self.imagen
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
