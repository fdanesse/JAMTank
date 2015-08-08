#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMTank.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import sys
import gtk
import gobject

from gtkWidgets.SelectMode import SelectMode
from gtkWidgets.StatusGame import StatusGame
from gtkWidgets.CreateServerMode import CreateServerMode
from ServerModelGame import ServerModelGame

BASE = os.path.dirname(__file__)


class JAMTank(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self)

        self.set_title("JAMTank")
        self.set_icon_from_file(os.path.join(BASE, "Iconos", "jamtank.svg"))
        #self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.fullscreen()

        self.screen_wh = (640, 480)
        self.widget_game = False
        self.eventos = []

        self.connect("delete-event", self.__salir)
        self.connect('key-press-event', self.__key_press_event)
        self.connect('key-release-event', self.__key_release_event)
        self.connect("realize", self.__do_realize)

        self.show_all()
        print "JAMTank pid:", os.getpid()
        gobject.idle_add(self.__switch, False, 1)

    def __do_realize(self, widget):
        screen = self.get_screen()
        self.screen_wh = (screen.get_width(), screen.get_height())
        xid = self.get_property('window').xid
        #os.putenv('SDL_WINDOWID', str(xid))
        print "Monitor:", self.screen_wh
        print "gtk widget id:", xid
        print ("Geometria:", "Game:", self.screen_wh[0]/4*3,
            self.screen_wh[1], "StatusGame:",
            self.screen_wh[0]/4, self.screen_wh[1])

    def __reset(self):
        #for child in self.get_children():
        #    self.remove(child)
        #    child.destroy()
        #if self.widget_game:
        #    self.disconnect_by_func(self.__key_press_event)
        #    self.disconnect_by_func(self.__key_release_event)
        #    self.widget_game.disconnect_by_func(self.switch)
        #    del(self.widget_game)
        #    self.widget_game = False
        self.eventos = []

    def __select_mode(self, widget, valor):
        if valor == "solo":
            self.__switch(False, 2)
        elif valor == "red":
            self.__switch(False, 3)
        elif valor == "join":
            self.__switch(False, 4)
        elif valor == "creditos":
            self.__switch(False, 5)
        elif valor == "salir":
            self.__salir()

    def __switch(self, widget, valor):
        self.__reset()
        if valor == 1:
            # Selección de tipo de juego
            win = SelectMode(self)
            win.connect("switch", self.__select_mode)
        elif valor == 2:
            # Jugar Solo
            pass
        elif valor == 3:
            # Crear Juego en Red
            print "Esta PC será Servidor"
            win = CreateServerMode(self)
            win.connect("close", self.__switch, 1)
            win.connect("accion", self.__accion_create_server)
        elif valor == 4:
            # Unirse a Juego en Red
            print "Esta PC será Cliente"
        elif valor == 5:
            # Creditos
            pass

    def __accion_create_server(self, create_server, accion, _dict):
        if accion == "run":
            new_dict = {
                'jugadores': int(_dict.get('enemigos', 1) + 1),
                'mapa': str(_dict.get('mapa', '')),
                'vidas': int(_dict.get('vidas', 5))
                }
            model = ServerModelGame(_dict.get('server', 'localhost'),
                new_dict, _dict.get('nick', 'JAMTank'), _dict.get('tanque', ''))
            model.connect("error", self.__server_error)
            win = StatusGame(self, self.screen_wh)
            #model.connect('salir', self.__switch, 3)
            model.server_run()
        elif accion == "salir":
            self.__switch(False, 1)

    def __server_error(self, servermodel):
        print ("FIXME:", self.__server_error)
        # FIXME: Quitar panel lateral
        del(servermodel)
        self.__switch(False, 3)

    def __key_press_event(self, widget, event):
        if gtk.gdk.keyval_name(event.keyval) == "Escape":
            self.__salir()
            return False
        #if not self.widget_game:
        #    return False
        #nombre = gtk.gdk.keyval_name(event.keyval)
        #teclas = ["w", "s", "d", "a", "space", "Escape"]
        #if nombre in teclas and not nombre in self.eventos:
        #    if nombre == "w" and "s" in self.eventos:
        #        self.eventos.remove("s")
        #    elif nombre == "s" and "w" in self.eventos:
        #        self.eventos.remove("w")
        #    elif nombre == "d" and "a" in self.eventos:
        #        self.eventos.remove("a")
        #    elif nombre == "a" and "d" in self.eventos:
        #        self.eventos.remove("d")
        #    self.eventos.append(nombre)
        #self.__update_events()
        return False

    def __key_release_event(self, widget, event):
        #if not self.widget_game:
        #    return False
        #nombre = gtk.gdk.keyval_name(event.keyval)
        #teclas = ["w", "s", "d", "a", "space", "Escape"]
        #if nombre in teclas and nombre in self.eventos:
        #    self.eventos.remove(nombre)
        #self.__update_events()
        return False

    #def __update_events(self):
    #    if self.widget_game:
    #        self.widget_game.update_events(self.eventos)

    def __salir(self, widget=None, event=None):
        #if self.widget_game:
        #    self.widget_game.salir()
        sys.exit(0)


if __name__ == "__main__":
    JAMTank()
    gtk.main()