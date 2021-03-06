#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SingleStatusGame.py por:
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


class SingleDialogoEndGame(gtk.Dialog):

    def __init__(self, parent, text, _dict1, _dict2):

        btns = ("Salir", gtk.RESPONSE_CANCEL)
        if "Game Over" in text:
            btns = ("Salir", gtk.RESPONSE_CANCEL)
        else:
            btns = ("Continuar", gtk.RESPONSE_CANCEL)

        gtk.Dialog.__init__(self, parent=parent, buttons=btns)

        self.set_decorated(False)
        self.set_border_width(15)

        self._ranking1 = Ranking(_dict1, "En este Nivel")
        self._ranking2 = Ranking(_dict2, "Suma de Niveles")
        label = gtk.Label(text)
        set_font(label, "titulo", typewidget="Label")
        self.vbox.pack_start(label, True, True, 5)
        self.vbox.pack_start(self._ranking1, True, True, 5)
        self.vbox.pack_start(self._ranking2, True, True, 5)

        self.vbox.show_all()
        self.set_sensitive(False)
        gobject.timeout_add(4000, self.__sensitive)
        button = self.get_widget_for_response(gtk.RESPONSE_CANCEL)
        set_font(button.get_children()[0], "subtitulo2", typewidget="Label")

    def __sensitive(self):
        self.set_sensitive(True)
        return False


class SingleStatusGame(gtk.Window):

    __gsignals__ = {
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, gobject.TYPE_STRING))}

    def __init__(self, top, screen_wh):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        w, h = screen_wh
        self.set_size_request(w / 4, h)
        self.set_resizable(False)
        self.move(w / 4 * 3, 0)
        self.set_deletable(False)
        self.set_transient_for(top)

        self._label_nivel = gtk.Label()
        set_font(self._label_nivel, "titulo", typewidget="Label")

        self._volumenes = FrameVolumen()
        self._framejugador = FrameJugador()
        image = gtk.Image()
        path = os.path.join(BASE, "Iconos", "teclas.svg")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, w / 4 / 3 * 2, -1)
        image.set_from_pixbuf(pixbuf)

        vbox = gtk.VBox()
        vbox.pack_end(self._volumenes, False, False, 0)
        vbox.pack_start(self._label_nivel, False, False, 0)
        vbox.pack_start(self._framejugador, False, False, 0)
        vbox.pack_start(image, True, True, 0)
        self.add(vbox)
        self.show_all()

        self._volumenes.connect("volumen", self.__emit_volumen)

    def __emit_volumen(self, widget, valor, text):
        self.emit("volumen", valor, text)

    def set_nivel(self, nivel):
        text = "Nivel %i" % nivel
        self._label_nivel.set_text(text)

    def update(self, juego, _dict):
        new = _dict.get(0, {})
        new["tanque"] = "t5.png"
        self._framejugador.update(new)


class Ranking(gtk.Frame):

    def __init__(self, _dict, text):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" %s: " % text)
        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)
        vbox = gtk.VBox()

        hbox = gtk.HBox()
        self._puntos = gtk.Label("Puntos = %s" % 0)
        set_font(self._puntos, "text", typewidget="Label")
        hbox.pack_start(self._puntos, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        self._disparos = gtk.Label("Disparos = %s" % 0)
        set_font(self._disparos, "text", typewidget="Label")
        hbox.pack_start(self._disparos, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        self._aciertos = gtk.Label("Aciertos = %s" % 0)
        set_font(self._aciertos, "text", typewidget="Label")
        hbox.pack_start(self._aciertos, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        self._porcenta = gtk.Label("Efectividad = %s %s" % (0, "%"))
        set_font(self._porcenta, "text", typewidget="Label")
        hbox.pack_start(self._porcenta, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        event.add(vbox)
        self.add(event)
        self.connect("realize", self.__realize)
        self.show_all()
        if _dict:
            self.update(_dict)

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")

    def update(self, _dict):
        self._puntos.set_text("Puntos = %s" % _dict.get("puntos", 0))
        self._disparos.set_text("Disparos = %s" % _dict.get("disparos", 0))
        self._aciertos.set_text("Aciertos = %s" % _dict.get("aciertos", 0))
        try:
            self._porcenta.set_text("Efectividad = %s %s" % (
                _dict.get("aciertos", 0) * 100 / _dict.get("disparos", 0), "%"))
        except:
            self._porcenta.set_text("Efectividad = 0 %s" % ("%"))


class FrameJugador(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)

        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)

        self._preview = gtk.Image()
        self._pixbuf = False
        self._ranking = Ranking({}, "Puntajes")
        self._energia = FrameProgress("Energía:")

        vbox = gtk.VBox()
        vbox.pack_start(self._ranking, False, False, 0)
        vbox.pack_start(self._preview, False, False, 0)
        vbox.pack_start(self._energia, False, False, 0)

        event.add(vbox)
        self.add(event)
        self.show_all()

    def update(self, _dict):
        try:
            if not self._pixbuf:
                path = os.path.join(BASE, "Tanques", _dict["tanque"])
                self._pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 80, -1)
                self._preview.set_from_pixbuf(self._pixbuf)
            self._ranking.update(_dict)
            self._energia.update(100, _dict["energia"])
        except:
            print "ERROR:", self.update, _dict
