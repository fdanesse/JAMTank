#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SelectWidgets.py por:
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
from Globales import set_font


class OponentesSelectBox(gtk.VBox):
    """
    Widget para seleccionar cantidad de enemigos y vidas.
    """

    __gsignals__ = {
    "valor": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_INT,
        gobject.TYPE_STRING))}

    def __init__(self):

        gtk.VBox.__init__(self)

        hbox = gtk.HBox()
        oponentes = gtk.Label("Oponentes")
        set_font(oponentes, "text", typewidget="Label")
        spin = NumBox(range(1, 11))
        spin.connect("valor", self.__emit_valor, "oponentes")
        hbox.pack_end(spin, False, False, 5)
        hbox.pack_end(oponentes, False, False, 5)
        self.pack_start(hbox, False, False, 0)

        hbox = gtk.HBox()
        limite = gtk.Label("Vidas")
        set_font(limite, "text", typewidget="Label")
        spin = NumBox(range(5, 51))
        spin.connect("valor", self.__emit_valor, "vidas")
        hbox.pack_end(spin, False, False, 5)
        hbox.pack_end(limite, False, False, 5)
        self.pack_start(hbox, False, False, 0)

        self.show_all()

    def __emit_valor(self, widget, valor, tipo):
        self.emit("valor", valor, tipo)


class NumBox(gtk.EventBox):
    """
    Spin para cambiar la cantidad de vidas o enemigos.
    """

    __gsignals__ = {
    "valor": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_INT, ))}

    def __init__(self, rango):

        gtk.EventBox.__init__(self)

        self.set_border_width(2)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        self.rango = rango
        self.valor = min(self.rango)

        hbox = gtk.HBox()
        vbox = gtk.VBox()

        self.mas = gtk.Button()
        self.mas.add(gtk.Arrow(0, 1))
        self.mas.connect("clicked", self.__change, "+")
        vbox.pack_start(self.mas, False, False, 0)

        self.menos = gtk.Button()
        self.menos.add(gtk.Arrow(1, 1))
        self.menos.connect("clicked", self.__change, "-")
        vbox.pack_start(self.menos, False, False, 0)

        self.label = gtk.Label("0")
        set_font(self.label, "text", typewidget="Label")

        hbox.pack_end(vbox, False, False, 0)
        hbox.pack_end(self.label, False, False, 3)

        self.add(hbox)
        self.show_all()

        self.label.set_text(str(self.valor))
        self.menos.set_sensitive(False)
        gobject.idle_add(self.emit, "valor", self.valor)

    def __change(self, widget, tipo):
        if tipo == "-":
            if self.valor - 1 >= min(self.rango):
                self.valor -= 1
        elif tipo == "+":
            if self.valor + 1 <= max(self.rango):
                self.valor += 1
        if self.valor == min(self.rango):
            self.menos.set_sensitive(False)
        else:
            self.menos.set_sensitive(True)
        if self.valor == max(self.rango):
            self.mas.set_sensitive(False)
        else:
            self.mas.set_sensitive(True)
        self.emit("valor", self.valor)
        self.label.set_text(str(self.valor))


class FrameNick(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" Escribe tu Apodo: ")

        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)
        self.add(event)
        self.nick = gtk.Entry()
        set_font(self.nick, "text", typewidget="Entry")
        self.nick.set_max_length(15)
        event.add(self.nick)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")


class FrameTanque(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" Selecciona tu Tanque: ")

        self.lista = Lista()
        self.lista.set_headers_visible(False)

        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)
        self.add(event)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(self.lista)
        event.add(scroll)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")


class Lista(gtk.TreeView):

    __gsignals__ = {
    "nueva-seleccion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gtk.TreeView.__init__(self, gtk.ListStore(gtk.gdk.Pixbuf,
            gobject.TYPE_STRING, gobject.TYPE_STRING))

        self.set_property("rules-hint", True)
        self.set_headers_clickable(True)
        self.set_headers_visible(True)

        self.permitir_select = True
        self.valor_select = None
        self.__setear_columnas()

        self.get_selection().connect('changed', self.__selecciones)
        self.show_all()

    def __selecciones(self, seleccion):
        if not self.permitir_select:
            return True
        model, pathlist = seleccion.get_selected_rows()
        _iter = model.get_iter(pathlist[0])
        valor = model.get_value(_iter, 2)
        self.valor_select = valor
        self.scroll_to_cell(model.get_path(_iter))
        self.emit('nueva-seleccion', self.valor_select)
        return True

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('', 0, True))
        self.append_column(self.__construir_columa('Nombre', 1, True))
        self.append_column(self.__construir_columa('', 2, False))

    def __construir_columa(self, text, index, visible):
        render = gtk.CellRendererText()
        columna = gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __construir_columa_icono(self, text, index, visible):
        render = gtk.CellRendererPixbuf()
        columna = gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            self.permitir_select = True
            self.seleccionar_primero()
            self.get_toplevel().set_sensitive(True)
            return False

        texto, path = elementos[0]
        texto = texto.split('.')[0]
        icono = os.path.join(path)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono, 50, -1)
        self.get_model().append([pixbuf, texto, path])

        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def limpiar(self):
        self.permitir_select = False
        self.get_model().clear()
        self.permitir_select = True

    def agregar_items(self, elementos):
        self.get_toplevel().set_sensitive(False)
        self.permitir_select = False
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def seleccionar_primero(self, widget=None):
        self.get_selection().select_iter(self.get_model().get_iter_first())
