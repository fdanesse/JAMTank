#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import GLib

BASE = os.path.dirname(__file__)

"""
Permite Elegir Opciones del Juego:
    self.game_dict = {
        'server': '',
        'nick': '',
        'tipo': tipo,
        'mapa': "",
        'tanque': "",
        'enemigos': 1,
        'vidas': 10,
        }

    emit("run", self.game_dict)
"""


class SelectWidget(Gtk.EventBox):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, []),
    "run": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self, tipo='single'):

        Gtk.EventBox.__init__(self)

        self.game_dict = {
            'server': '',
            'nick': '',
            'tipo': tipo,
            'mapa': "",
            'tanque': "",
            'enemigos': 1,
            'vidas': 10,
            }

        self.modify_bg(0, Gdk.color_parse("#ffffff"))
        self.set_border_width(20)
        self.select_box = False
        self.show_all()
