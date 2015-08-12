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
from gtkWidgets.ConnectingPlayers import ConnectingPlayers
from ServerModelGame import ServerModelGame

BASE = os.path.dirname(__file__)

#gobject.threads_init()


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
        self.handlers = {
            'servermodel': []
            }
        self.servermodel = False

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
        print "Resolución del Monitor:", self.screen_wh
        print "id de la ventana:", xid
        print "Geometria:", "Game:", self.screen_wh[0]/4*3, self.screen_wh[1], "StatusGame:", self.screen_wh[0]/4, self.screen_wh[1]

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
            self.servermodel = ServerModelGame(_dict.get('server', 'localhost'),
                new_dict, _dict.get('nick', 'JAMTank'), _dict.get('tanque', ''))
            _id = self.servermodel.connect("error", self.__server_error)
            self.handlers['servermodel'].append(_id)
            if self.servermodel.server_run():
                win = ConnectingPlayers(self, _dict.get('nick', 'JAMTank'),
                    _dict.get('tanque', ''), new_dict)
                win.connect("accion", self.__accion_connecting_players)
                _id = self.servermodel.connect("players", win.update_playeres)
                self.handlers['servermodel'].append(_id)
                _id = self.servermodel.connect("play-enabled", win.play_enabled)
                self.handlers['servermodel'].append(_id)
                self.servermodel.new_handler_registro(True)
                self.servermodel.new_handler_anuncio(True)
            else:
                print "FIXME:", self.__accion_create_server
        elif accion == "salir":
            self.__switch(False, 1)

    def __accion_connecting_players(self, con_players, valor):
        if valor == "jugar":
            print "FIXME: Se debe mandar running al server para Lanzar el Juego"
            win = StatusGame(self, self.screen_wh)
        elif valor == "cancelar":
            self.__server_error()

    def __kill_server_model(self):
        if self.servermodel:
            for h in self.handlers.get('servermodel', []):
                if self.servermodel.handler_is_connected(h):
                    self.servermodel.handler_disconnect(h)
            for h in self.handlers.get('servermodel', []):
                del(h)
            self.handlers['servermodel'] = []
            self.servermodel.close_all_and_exit()
            del(self.servermodel)
            self.servermodel = False

    def __server_error(self, servermodel=False):
        self.__kill_server_model()
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
        self.__kill_server_model()
        sys.exit(0)


if __name__ == "__main__":
    JAMTank()
    gtk.main()
