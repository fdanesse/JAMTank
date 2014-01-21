#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
#import pygame
import threading

from gi.repository import Gtk
#from gi.repository import GObject
#from gi.repository import Gdk
from gi.repository import GdkX11
#from gi.repository import GLib


class GameWidget(Gtk.DrawingArea):

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.juego = False
        self.game_thread = False

        self.show_all()

    def do_draw(self, context):

        rect = self.get_allocation()

        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def setup_init(self, datos):

        from Juego import Juego

        xid = self.get_property('window').get_xid()
        os.putenv('SDL_WINDOWID', str(xid))

        self.juego = Juego(datos)
        self.juego.config()

        self.game_thread = threading.Thread(
            target=self.juego.run,
            args=[])

        self.game_thread.start()
