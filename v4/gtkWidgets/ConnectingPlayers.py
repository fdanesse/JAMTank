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

        self.set_resizable(False)
        self.set_position(3)
        self.set_deletable(False)
        self.set_decorated(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_transient_for(top)

        for child in self.vbox.get_children():
            self.vbox.remove(child)
            child.destroy()
        self.internal_widget = InternalWidget()
        self.internal_widget.cancelar.connect("clicked", self.__accion)
        self.internal_widget.jugar.connect("clicked", self.__accion)
        self.vbox.pack_start(self.internal_widget, True, True, 0)

        self.show_all()

        text = "Host: %s  Límite de Vidas: %s" % (
            nick, _dict['vidas'])
        self.internal_widget.label.set_text(text)
        rect = self.internal_widget.framemapa.mapaview.get_allocation()
        path = os.path.join(ROOTPATH, "Mapas", _dict['mapa'])
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, -1, rect.height)
        self.internal_widget.framemapa.mapaview.set_from_pixbuf(pixbuf)

        # FIXME: Analizar esto, requiere cambios en:
        # self.internal_widget.framejugadores.jugadores.update_playeres(_dict)
        #items = []
        #for x in range(_dict['jugadores']):
        #    pix = None
        #    nom = "Esperando..."
        #    items.append([pix, nom, ""])
        #self.internal_widget.framejugadores.jugadores.limpiar()
        #self.internal_widget.framejugadores.jugadores.agregar_items(items)

    def __accion(self, widget):
        self.emit("accion", widget.get_label().lower())
        self.destroy()

    def update_playeres(self, servermodel, _dict):
        self.internal_widget.framejugadores.jugadores.update_playeres(_dict)


class InternalWidget(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(15)
        self.set_label(" Esperando Jugadores... ")

        event = gtk.EventBox()
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.set_border_width(6)

        tabla = gtk.Table(columns=4, rows=8, homogeneous=True)
        tabla.set_col_spacing(1, 10)
        tabla.set_col_spacing(2, 5)
        tabla.set_row_spacing(6, 10)
        tabla.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        tabla.set_border_width(6)

        self.label = gtk.Label()
        tabla.attach_defaults(self.label, 0, 4, 0, 1)

        self.framejugadores = FrameJugadores()
        tabla.attach_defaults(self.framejugadores, 0, 2, 1, 8)

        self.framemapa = FrameMapa()
        tabla.attach_defaults(self.framemapa, 2, 4, 1, 7)

        self.cancelar = gtk.Button("Cancelar")
        self.jugar = gtk.Button("Jugar")
        self.jugar.set_sensitive(False)
        tabla.attach_defaults(self.cancelar, 2, 3, 7, 8)
        tabla.attach_defaults(self.jugar, 3, 4, 7, 8)

        event.add(tabla)
        self.add(event)
        self.show_all()


class FrameJugadores(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_label(" Jugadores: ")
        self.set_border_width(4)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))

        event = gtk.EventBox()
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.set_border_width(4)
        self.jugadores = NewLista()
        self.jugadores.set_headers_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.jugadores)
        event.add(scroll)
        self.add(event)
        self.show_all()


class FrameMapa(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)

        self.set_label(" Mapa: ")
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_border_width(4)

        self.mapaview = gtk.Image()
        event = gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        event.add(self.mapaview)

        self.add(event)
        self.show_all()


class NewLista(Lista):
    # FIXME: Analizar independizar esta clase de su herencia

    def __init__(self):

        Lista.__init__(self)

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            return False
        pixbuf, nick, ip = elementos[0]
        if pixbuf:
            if os.path.exists(pixbuf):
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(pixbuf, 50, -1)
        self.modelo.append([pixbuf, nick, ip])
        elementos.remove(elementos[0])
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def __buscar(self, texto):
        model = self.get_model()
        _iter = model.get_iter_first()
        while _iter:
            contenido = model.get_value(_iter, 2)
            if texto == contenido:
                return _iter
            _iter = model.iter_next(_iter)
        return None

    def agregar_items(self, elementos):
        gobject.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def update_playeres(self, _dict):
        #{'192.168.1.11': {'nick': 'flavio', 'tank': 't1.png'}}
        news = _dict.keys()
        model = self.get_model()
        # Los que no vienen en _dict, hay que quitarlos
        remover = []
        _iter = model.get_iter_first()
        while _iter:
            ip = model.get_value(_iter, 2)
            if ip not in news:
                remover.append(_iter)
            _iter = model.iter_next(_iter)
        for item in remover:
            model.remove(item)
        # Todos los que vienen en _dict, deben estar en la lista
        items = []
        for key in news:
            _iter = self.__buscar(key)
            if _iter:
                pixbuf = os.path.join(ROOTPATH, "Tanques",
                    _dict[key].get('tank', ''))
                if pixbuf:
                    if os.path.exists(pixbuf):
                        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                            pixbuf, 50, -1)
                        model.set_value(_iter, 0, pixbuf)
                model.set_value(_iter, 1, _dict[key].get('nick', ''))
                model.set_value(_iter, 2, key)
            else:
                pixbuf = os.path.join(ROOTPATH, "Tanques",
                    _dict[key].get('tank', ''))
                items.append([pixbuf, _dict[key].get('nick', ''), key])
        if items:
            self.agregar_items(items)
