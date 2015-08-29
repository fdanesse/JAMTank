#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gobject
import gtk

BASE_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


class StatusGame(gtk.Window):

    def __init__(self, top, screen_wh, ip):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        self._ip = ip
        w, h = screen_wh
        self.set_size_request(w / 4, h)
        self.set_resizable(False)
        self.move(w / 4 * 3, 0)
        self.set_deletable(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_transient_for(top)
        #self.set_keep_below(False)
        #self.set_keep_above(True)

        self._ranking = Ranking()
        self._framejugador = FrameJugador()

        vbox = gtk.VBox()
        vbox.pack_start(self._ranking, False, False, 0)
        vbox.pack_end(self._framejugador, False, False, 0)
        self.add(vbox)

        self.show_all()

    def update(self, juego, _dict):
        self._ranking._lista.update(_dict)
        self._framejugador.update(_dict.get(self._ip))


class Ranking(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(4)
        self.set_label(" Ranking ")
        event = gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self._lista = Lista()
        event.add(self._lista)
        self.add(event)
        self.show_all()


class Lista(gtk.TreeView):

    def __init__(self):

        gtk.TreeView.__init__(self, gtk.ListStore(gobject.TYPE_STRING,
            gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_INT))

        self.set_property("rules-hint", True)
        self.set_headers_clickable(False)
        self.set_headers_visible(False)
        self.__setear_columnas()
        self.get_model().set_sort_column_id(4, gtk.SORT_DESCENDING)
        self.show_all()

    def __setear_columnas(self):
        self.append_column(self.__construir_columa("Ip", 0, False))
        self.append_column(self.__construir_columa_icono("Tanque", 1, True))
        self.append_column(self.__construir_columa("Path", 2, False))
        self.append_column(self.__construir_columa("Nombre", 3, True))
        self.append_column(self.__construir_columa("Puntos", 4, True))

    def __construir_columa(self, text, index, visible):
        render = gtk.CellRendererText()
        columna = gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property("visible", visible)
        columna.set_property("resizable", False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __construir_columa_icono(self, text, index, visible):
        render = gtk.CellRendererPixbuf()
        columna = gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property("visible", visible)
        columna.set_property("resizable", False)
        columna.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            return False
        ip, pixbuf, path, nick, puntos = elementos[0]
        self.get_model().append([ip, pixbuf, path, nick, puntos])
        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def __buscar(self, texto):
        model = self.get_model()
        _iter = model.get_iter_first()
        while _iter:
            contenido = model.get_value(_iter, 0)
            if texto == contenido:
                return _iter
            _iter = model.iter_next(_iter)
        return None

    def agregar_items(self, elementos):
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def update(self, _dict):
        items = []
        for ip in _dict.keys():
            _iter = self.__buscar(ip)
            if _iter:
                model = self.get_model()
                model.set_value(_iter, 4, _dict[ip]["s"]["p"])
            else:
                path = os.path.join(BASE_PATH, "Tanques", _dict[ip]["t"])
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 50, -1)
                nick = _dict[ip]["n"]
                puntos = _dict[ip]["s"]["p"]
                items.append([ip, pixbuf, path, nick, puntos])
        self.agregar_items(items)


class FrameJugador(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(4)
        self.set_label(" Ranking ")
        event = gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self._preview = gtk.Image()
        event.add(self._preview)
        self.add(event)
        self.show_all()

    def update(self, _dict):
        nick = _dict["n"]
        tanque = _dict["t"]
        energia = _dict["s"]["e"]
        vidas = _dict["s"]["v"]
        if self.get_label() != nick:
            self.set_label(" %s " % nick)
            path = os.path.join(BASE_PATH, "Tanques", _dict["t"])
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 80, -1)
            self._preview.set_from_pixbuf(pixbuf)
