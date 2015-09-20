#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   WidgetsGenerales.py por:
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
from Globales import set_font

BASE = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


class FrameVolumen(gtk.Frame):

    __gsignals__ = {
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, gobject.TYPE_STRING))}

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" Volumen ")

        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)

        self._musica = ControlVolumen()
        self._efectos = ControlVolumen()

        vbox = gtk.HBox()
        frame = gtk.Frame()
        frame.connect("realize", self.__frame_realize)
        frame.set_label(" Música ")
        frame.add(self._musica)
        vbox.pack_end(frame, False, False, 0)

        frame = gtk.Frame()
        frame.connect("realize", self.__frame_realize)
        frame.set_label(" Efectos ")
        frame.add(self._efectos)
        vbox.pack_end(frame, False, False, 0)

        event.add(vbox)
        self.add(event)
        self.connect("realize", self.__realize)
        self.show_all()

        self._musica.connect("volumen", self.__emit_volumen, "musica")
        self._efectos.connect("volumen", self.__emit_volumen, "efectos")

    def __realize(self, widget):
        set_font(widget, "subtitulo1", typewidget="Frame")

    def __frame_realize(self, widget):
        set_font(widget, "subtitulo2", typewidget="Frame")

    def __emit_volumen(self, widget, valor, text):
        self.emit("volumen", valor, text)


class FrameProgress(gtk.Frame):

    def __init__(self, text):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" %s " % text)
        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)
        self._progress = Progreso()
        event.add(self._progress)
        self.add(event)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")

    def update(self, _max, val):
        self._progress.set_progress(100 * val / _max)


class Progreso(gtk.EventBox):
    """
    Barra de progreso para mostrar energia.
    """

    def __init__(self):

        gtk.EventBox.__init__(self)

        self.escala = ProgressBar(
            gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))

        self.set_property("visible-window", False)
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


class ProgressBar(gtk.HScale):

    def __init__(self, ajuste):

        gtk.HScale.__init__(self)

        self.ajuste = ajuste
        self.set_digits(0)
        self.set_draw_value(False)
        self.borde = 10
        self.connect("expose-event", self.__do_draw)
        self.show_all()

    def __do_draw(self, widget, event):
        x, y, w, h = self.get_allocation()
        gc = gtk.gdk.Drawable.new_gc(self.window)

        # todo el widget
        #gc.set_rgb_fg_color(gtk.gdk.Color(255, 255, 255))
        #self.window.draw_rectangle(gc, True, x, y, w, h)

        # vacio
        gc.set_rgb_fg_color(gtk.gdk.Color(0, 0, 0))
        ww = w - 10 * 2
        xx = x + w / 2 - ww / 2
        hh = 10
        yy = y + h / 2 - 10 / 2
        self.window.draw_rectangle(gc, True, xx, yy, ww, hh)

        # progreso
        ximage = int(self.ajuste.get_value() * ww / 100)
        gc.set_rgb_fg_color(gtk.gdk.Color(23000, 41000, 12000))
        self.window.draw_rectangle(gc, True, xx, yy, ximage, hh)

        # borde de progreso
        #gc.set_rgb_fg_color(get_colors("window"))
        #self.window.draw_rectangle(gc, False, xx, yy, ww, hh)
        return True


class ControlVolumen(gtk.VolumeButton):

    __gsignals__ = {
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, ))}

    def __init__(self):

        gtk.VolumeButton.__init__(self)

        self.connect("value-changed", self.__value_changed)
        self.show_all()

        self.set_value(0.1)

    def __value_changed(self, widget, valor):
        self.emit('volumen', valor)


class DialogoSalir(gtk.Dialog):

    def __init__(self, parent=None, text=""):

        gtk.Dialog.__init__(self, parent=parent,
        buttons=("No", gtk.RESPONSE_CANCEL,
        "Si", gtk.RESPONSE_ACCEPT))

        self.set_decorated(False)
        self.set_border_width(15)

        label = gtk.Label(text)
        set_font(label, "subtitulo2", typewidget="Label")
        label.show()

        self.vbox.pack_start(label, True, True, 5)
        button = self.get_widget_for_response(gtk.RESPONSE_ACCEPT)
        set_font(button.get_children()[0], "subtitulo2", typewidget="Label")
        button = self.get_widget_for_response(gtk.RESPONSE_CANCEL)
        set_font(button.get_children()[0], "subtitulo2", typewidget="Label")
