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
from gtkWidgets.CreateClientMode import CreateClientMode
from ListenServers import ListenServers
from ClientModelGame import ClientModelGame

BASE = os.path.dirname(__file__)

gobject.threads_init()


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
            'servermodel': [],
            'clientmodel': [],
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
            win.connect("close", self.__switch, 1)  # Escape en dialog
            win.connect("accion", self.__accion_create_server)
        elif valor == 4:
            # Unirse a Juego en Red
            print "Esta PC será Cliente"
            win = CreateClientMode(self, ListenServers())
            win.connect("close", self.__switch, 1)  # Escape en dialog
            win.connect("accion", self.__accion_create_client)
        elif valor == 5:
            # Creditos
            pass

    def __accion_create_client(self, mode_client, accion, server_dict, player_dict):
        if accion == "run":
            #print server_dict, player_dict
            host = server_dict.get('ip', 'localhost')
            nickh = server_dict.get('nick', 'JAMTank')
            del(server_dict['ip'])
            del(server_dict['nick'])
            self.clientmodel = ClientModelGame(host, server_dict,
                player_dict.get('nick', 'JAMTank'), player_dict.get('tanque', ''))
            _id = self.clientmodel.connect("error", self.__client_error)
            self.handlers['clientmodel'].append(_id)
            if self.clientmodel.client_run():
                win = ConnectingPlayers(self, nickh, server_dict)
                win.internal_widget.jugar.hide()
                win.connect("accion", self.__accion_connecting_players_client)
                _id = self.clientmodel.connect("players", win.update_playeres)
                self.handlers['clientmodel'].append(_id)
                #_id = self.clientmodel.connect("play-enabled", win.play_enabled)
                #self.handlers['clientmodel'].append(_id)
                _id = self.clientmodel.connect("play-run", self.__play_run)
                self.handlers['clientmodel'].append(_id)
                self.clientmodel.new_handler_registro(True)
            else:
                print "FIXME:", self.__accion_create_client
        elif accion == "salir":
            self.__switch(False, 1)

    def __accion_create_server(self, mode_server, accion, _dict):
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
                win = ConnectingPlayers(self,
                    _dict.get('nick', 'JAMTank'), new_dict)
                win.connect("accion", self.__accion_connecting_players_server)
                _id = self.servermodel.connect("players", win.update_playeres)
                self.handlers['servermodel'].append(_id)
                _id = self.servermodel.connect("play-enabled", win.play_enabled)
                self.handlers['servermodel'].append(_id)
                _id = self.servermodel.connect("play-run", self.__play_run)
                self.handlers['servermodel'].append(_id)
                self.servermodel.new_handler_registro(True)
                self.servermodel.new_handler_anuncio(True)
            else:
                print "FIXME:", self.__accion_create_server
        elif accion == "salir":
            self.__switch(False, 1)

    def __play_run(self, server_or_client_model):
        print "FIXME: Lanzar el juego (cambiar 'register' por otro mensaje)"
        #win = StatusGame(self, self.screen_wh)

    def __accion_connecting_players_server(self, con_players, valor):
        if valor == "jugar":
            self.servermodel.running = True
        elif valor == "cancelar":
            self.__server_error()

    def __accion_connecting_players_client(self, con_players, valor):
        if valor == "jugar":
            #self.clientmodel.running = True
            print "connecting_players_client recibe jugar"
        elif valor == "cancelar":
            self.__client_error()

    def __kill_client_model(self):
        if self.clientmodel:
            for h in self.handlers.get('clientmodel', []):
                if self.clientmodel.handler_is_connected(h):
                    self.clientmodel.handler_disconnect(h)
            for h in self.handlers.get('clientmodel', []):
                del(h)
            self.handlers['clientmodel'] = []
            self.clientmodel.close_all_and_exit()
            del(self.clientmodel)
            self.clientmodel = False

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

    def __client_error(self, clientmodel=False):
        self.__kill_client_model()
        self.__switch(False, 4)

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
        gtk.main_quit()
        sys.exit(0)


if __name__ == "__main__":
    JAMTank()
    gtk.main()
