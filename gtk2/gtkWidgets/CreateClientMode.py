#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   CreateClientMode.py por:
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
import time
from Globales import set_font
from SelectWidgets import FrameNick
from SelectWidgets import FrameTanque
from Network.ListenServers import ListenServers

BASE = os.path.dirname(os.path.dirname(__file__))


class CreateClientMode(gtk.Dialog):

    __gsignals__ = {
    "accion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,
        gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))}

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
        self.create_client = CreateClient()
        self.create_client.connect("accion", self.__accion)
        self.vbox.pack_start(self.create_client, True, True, 0)

        self.show_all()

        self._servers = {}
        self._listen_servers = False
        self._update = False

        gobject.timeout_add(500, self.__run_listen)

    def __run_listen(self):
        self._listen_servers = ListenServers()
        self._listen_servers.connect("server", self.__update_servers)
        self._listen_servers.new_handler_listen(True)
        self._update = gobject.timeout_add(300, self.__update)
        return False

    def __update(self):
        t = time.time()
        remove = []
        for key in self._servers.keys():
            if t - self._servers[key].get('time', 0) > 1.4:
                remove.append(key)
        for i in remove:
            del(self._servers[i])
        self.create_client.framejuegos.lista.update_servers(self._servers)

        return bool(self._update)

    def __accion(self, widget, accion, server_dict, player_dict):
        self.kill_all()
        self.emit("accion", accion, server_dict, player_dict)
        self.destroy()

    def __update_servers(self, listen_servers, _dict):
        ip = _dict.get('ip', '')
        del(_dict['ip'])
        del(_dict['z'])
        _dict['time'] = time.time()
        self._servers[ip] = _dict

    def kill_all(self, widget=False):
        if self._listen_servers:
            self._listen_servers.disconnect_by_func(self.__update_servers)
            self._listen_servers.new_handler_listen(False)
            del(self._listen_servers)
            self._listen_servers = False
        if self._update:
            gobject.source_remove(self._update)
            self._update = False


class CreateClient(gtk.EventBox):

    __gsignals__ = {
    "accion": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,
        gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))}

    def __init__(self):

        gtk.EventBox.__init__(self)

        self.set_property("visible-window", False)

        self.player = {}
        self.server = {}

        self.set_border_width(10)

        tabla = gtk.Table(columns=3, rows=9, homogeneous=True)

        self.framejuegos = FrameJuegos()
        tabla.attach_defaults(self.framejuegos, 0, 1, 0, 4)

        self.frametanque = FrameTanque()
        tabla.attach_defaults(self.frametanque, 0, 1, 4, 8)

        self.mapview = gtk.Image()
        tabla.attach_defaults(self.mapview, 1, 3, 0, 4)

        self.tanqueview = gtk.Image()
        tabla.attach_defaults(self.tanqueview, 1, 2, 6, 7)

        self.framenick = FrameNick()
        tabla.attach_defaults(self.framenick, 2, 3, 5, 8)

        button = gtk.Button("Cancelar")
        set_font(button.get_children()[0], "subtitulo1", typewidget="Label")
        tabla.attach_defaults(button, 0, 1, 8, 9)
        button.connect("clicked", self.__accion, "salir")

        self.jugar = gtk.Button("Unirme")
        set_font(self.jugar.get_children()[0],
            "subtitulo1", typewidget="Label")
        self.jugar.set_sensitive(False)
        self.jugar.connect("clicked", self.__accion, "run")
        tabla.attach_defaults(self.jugar, 2, 3, 8, 9)

        self.add(tabla)

        self.connect("realize", self.__do_realize)
        self.frametanque.lista.connect(
            "nueva-seleccion", self.__seleccion_tanque)
        self.framenick.nick.connect("changed", self.__change_nick)
        self.framejuegos.lista.connect("selected", self.__update_server)

        self.show_all()

    def __update_server(self, lista, _dict):
        self.server = _dict
        mapa = self.server.get("mapa", False)
        if mapa:
            path = os.path.join(BASE, "Mapas", mapa)
            rect = self.mapview.get_allocation()
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, -1, rect.height)
            self.mapview.set_from_pixbuf(pixbuf)
        self.__check_dict()

    def __do_realize(self, widget):
        elementos = []
        mapas_path = os.path.join(BASE, "Tanques")
        for arch in sorted(os.listdir(mapas_path)):
            path = os.path.join(mapas_path, arch)
            archivo = os.path.basename(path)
            elementos.append([archivo, path])
        self.frametanque.lista.limpiar()
        self.frametanque.lista.agregar_items(elementos)

    def __change_nick(self, widget):
        self.__check_dict()

    def __seleccion_tanque(self, widget, path):
        rect = self.tanqueview.get_allocation()
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, -1, rect.height)
        self.tanqueview.set_from_pixbuf(pixbuf)
        self.player['tanque'] = os.path.basename(path)
        self.__check_dict()

    def __accion(self, widget, accion):
        self.emit("accion", accion, dict(self.server), dict(self.player))

    def __check_dict(self):
        nick = self.framenick.nick.get_text().replace(
            '\n', '').replace('\r', '')
        nick = nick.replace('*', '').replace(' ', '_').replace('|', '')
        self.player['nick'] = nick
        valor = True
        for item in self.player.items():
            if not item[1]:
                valor = False
                break
        if not self.server:
            valor = False
        self.jugar.set_sensitive(valor)


class FrameJuegos(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_border_width(4)
        self.set_label(" Juegos Creados: ")

        self.lista = NewLista()

        event = gtk.EventBox()
        event.set_border_width(4)
        event.set_property("visible-window", False)
        self.add(event)

        self.lista.set_headers_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(self.lista)
        event.add(scroll)
        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        set_font(self, "subtitulo1", typewidget="Frame")


class NewLista(gtk.TreeView):

    __gsignals__ = {
    "selected": (gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gtk.TreeView.__init__(self, gtk.ListStore(gtk.gdk.Pixbuf,
            gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_INT, gobject.TYPE_INT, gobject.TYPE_STRING))

        self.set_property("rules-hint", True)
        self.set_headers_clickable(True)
        self.set_headers_visible(True)

        self.__setear_columnas()
        self.get_selection().set_select_function(
            self.__selecciones, self.get_model())
        self.show_all()

    def __selecciones(self, path, column):
        _iter = self.get_model().get_iter(path)
        mapa = self.get_model().get_value(_iter, 1)
        nick = self.get_model().get_value(_iter, 2)
        jugadores = self.get_model().get_value(_iter, 3)
        vidas = self.get_model().get_value(_iter, 4)
        ip = self.get_model().get_value(_iter, 5)
        _dict = {
            'mapa': mapa,
            'ip': ip,
            'nick': nick,
            'jugadores': jugadores,
            'vidas': vidas,
            }
        self.emit('selected', _dict)
        self.scroll_to_cell(self.get_model().get_path(_iter))
        return True

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('mapa', 0, True))
        self.append_column(self.__construir_columa('mappath', 1, False))
        self.append_column(self.__construir_columa('nickh', 2, True))
        self.append_column(self.__construir_columa('jugadores', 3, False))
        self.append_column(self.__construir_columa('vidas', 4, False))
        self.append_column(self.__construir_columa('ip', 5, False))

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
            model, _iter = self.get_selection().get_selected()
            if not _iter:
                _iter = model.get_iter_first()
            self.get_selection().select_iter(_iter)
            return False
        pixbuf, mappath, nick, jugadores, vidas, ip = elementos[0]
        if pixbuf:
            if os.path.exists(pixbuf):
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(pixbuf, 50, -1)
        self.get_model().append([pixbuf, mappath, nick, jugadores, vidas, ip])
        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def __buscar(self, texto):
        model = self.get_model()
        _iter = model.get_iter_first()
        while _iter:
            contenido = model.get_value(_iter, 5)
            if texto == contenido:
                return _iter
            _iter = model.iter_next(_iter)
        return None

    def agregar_items(self, elementos):
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def update_servers(self, _dict):
        news = _dict.keys()
        model = self.get_model()
        # Los que no vienen en _dict, hay que quitarlos
        remover = []
        _iter = model.get_iter_first()
        while _iter:
            ip = model.get_value(_iter, 5)
            if ip not in news:
                remover.append(_iter)
            _iter = model.iter_next(_iter)
        for item in reversed(remover):
            model.remove(item)
        # Todos los que vienen en _dict, deben estar en la lista
        items = []
        for key in news:
            _iter = self.__buscar(key)
            if _iter:
                pixbuf = os.path.join(BASE, "Mapas",
                    _dict[key].get('mapa', ''))
                if pixbuf:
                    if os.path.exists(pixbuf):
                        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                            pixbuf, 50, -1)
                        model.set_value(_iter, 0, pixbuf)
                model.set_value(_iter, 1, _dict[key].get('mapa', ''))
                model.set_value(_iter, 2, _dict[key].get('nickh', ''))
                model.set_value(_iter, 3, _dict[key].get('jugadores', ''))
                model.set_value(_iter, 4, _dict[key].get('vidas', ''))
                model.set_value(_iter, 5, key)
            else:
                pixbuf = os.path.join(BASE, "Mapas",
                    _dict[key].get('mapa', ''))
                items.append([pixbuf, _dict[key].get('mapa', ''),
                    _dict[key].get('nickh', ''),
                    _dict[key].get('jugadores', ''),
                    _dict[key].get('vidas', ''), key])
                # FIXME: Emitir sonido de conexión
        if items:
            self.agregar_items(items)
        modelo, _iter = self.get_selection().get_selected()
        if not _iter:
            _dict = {}
            self.emit('selected', _dict)
