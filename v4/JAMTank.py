#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMTank.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import gobject
import os
import sys
import gtk

from gtkWidgets.SelectMode import SelectMode
from gtkWidgets.StatusGame import StatusGame
from gtkWidgets.CreateServerMode import CreateServerMode
from gtkWidgets.ConnectingPlayers import ConnectingPlayers
from gtkWidgets.CreateClientMode import CreateClientMode
import Network
from ServerModelGame import ServerModelGame
from ClientModelGame import ClientModelGame

gobject.threads_init()

BASE = os.path.dirname(__file__)


class JAMTank(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self)

        self.set_title("JAMTank")
        self.set_icon_from_file(os.path.join(BASE, "Iconos", "jamtank.svg"))
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        self.fullscreen()

        self.screen_wh = (640, 480)
        self.gameres = (640, 480)
        self.handlers = {
            'selectmode': [],
            'createservermode': [],
            'createclientmode': [],
            'servermodel': [],
            'clientmodel': [],
            'connectingplayers': [],
            }
        self.selectmode = False
        self.servermodel = False
        self.clientmodel = False
        self.createservermode = False
        self.createclientmode = False
        self.connectingplayers = False

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
        self.gameres = (self.screen_wh[0] / 4 * 3, self.screen_wh[1])
        xid = self.get_property('window').xid
        #os.putenv('SDL_WINDOWID', str(xid))
        print "Resolución del Monitor:", self.screen_wh
        print "id de la ventana:", xid
        print "Geometria:"
        print "\tGame:", self.gameres
        print "\tStatusGame:", (self.screen_wh[0] / 4, self.screen_wh[1])

    def __reset(self):
        self.__kill_client_model()
        self.__kill_server_model()
        self.__kill_connectingplayers()
        self.__kill_create_mode()
        self.__kill_select_mode()
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))

    def __select_mode(self, widget, valor):
        self.__reset()  # Necesario
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
        self.__reset()  # Necesario
        if valor == 1:
            # Selección de tipo de juego
            self.selectmode = SelectMode(self)
            _id = self.selectmode.connect("close", self.__salir)
            self.handlers['selectmode'].append(_id)
            _id = self.selectmode.connect("switch", self.__select_mode)
            self.handlers['selectmode'].append(_id)
        elif valor == 2:
            # Jugar Solo
            pass
        elif valor == 3:
            # Crear Juego en Red
            self.createservermode = CreateServerMode(self)
            _id = self.createservermode.connect("close", self.__switch, 1)
            self.handlers['createservermode'].append(_id)
            _id = self.createservermode.connect("accion",
                self.__accion_create_server)
            self.handlers['createservermode'].append(_id)
        elif valor == 4:
            # Unirse a Juego en Red
            self.createclientmode = CreateClientMode(self)
            _id = self.createclientmode.connect("close", self.__switch, 1)
            self.handlers['createclientmode'].append(_id)
            _id = self.createclientmode.connect("accion",
                self.__accion_create_client)
            self.handlers['createclientmode'].append(_id)
        elif valor == 5:
            # Creditos
            pass

    def __accion_create_client(self, mode_client, accion,
        server_dict, player_dict):
        self.__reset()
        if accion == "run":
            host = server_dict.get('ip', 'localhost')
            nickh = server_dict.get('nick', 'JAMTank')
            del(server_dict['ip'])
            del(server_dict['nick'])
            self.clientmodel = ClientModelGame(host, server_dict,
                player_dict.get('nick', 'JAMTank'),
                player_dict.get('tanque', ''))
            _id = self.clientmodel.connect("error", self.__switch, 4)
            self.handlers['clientmodel'].append(_id)
            if self.clientmodel.client_run():
                self.connectingplayers = ConnectingPlayers(
                    self, nickh, server_dict)
                self.connectingplayers.internal_widget.jugar.hide()
                _id = self.connectingplayers.connect("close", self.__switch, 4)
                self.handlers['connectingplayers'].append(_id)
                _id = self.connectingplayers.connect("accion",
                    self.__accion_connecting_players_client)
                self.handlers['connectingplayers'].append(_id)
                _id = self.clientmodel.connect("players",
                    self.connectingplayers.update_playeres)
                self.handlers['clientmodel'].append(_id)
                _id = self.clientmodel.connect("play-run", self.__play_run)
                self.handlers['clientmodel'].append(_id)
                self.clientmodel.new_handler_registro(True)
            else:
                print "FIXME:", self.__accion_create_client
        elif accion == "salir":
            self.__switch(False, 1)

    def __accion_create_server(self, mode_server, accion, _dict):
        self.__reset()
        if accion == "run":
            new_dict = {
                'jugadores': int(_dict.get('enemigos', 1) + 1),
                'mapa': str(_dict.get('mapa', '')),
                'vidas': int(_dict.get('vidas', 5))
                }
            self.servermodel = ServerModelGame(
                _dict.get('server', 'localhost'),
                new_dict, _dict.get('nick', 'JAMTank'),
                _dict.get('tanque', ''))
            _id = self.servermodel.connect("error", self.__switch, 3)
            self.handlers['servermodel'].append(_id)
            if self.servermodel.server_run():
                self.connectingplayers = ConnectingPlayers(self,
                    _dict.get('nick', 'JAMTank'), new_dict)
                _id = self.connectingplayers.connect("close", self.__switch, 3)
                self.handlers['connectingplayers'].append(_id)
                _id = self.connectingplayers.connect("accion",
                    self.__accion_connecting_players_server)
                self.handlers['connectingplayers'].append(_id)
                _id = self.servermodel.connect("players",
                    self.connectingplayers.update_playeres)
                self.handlers['servermodel'].append(_id)
                _id = self.servermodel.connect("play-enabled",
                    self.connectingplayers.play_enabled)
                self.handlers['servermodel'].append(_id)
                self.servermodel.new_handler_registro(True)
            else:
                print "FIXME:", self.__accion_create_server
        elif accion == "salir":
            self.__switch(False, 1)

    def __play_run(self, client_model):
        self.clientmodel.new_handler_registro(False)
        self.__kill_connectingplayers()
        xid = self.get_property('window').xid
        self.clientmodel.rungame(xid, self.gameres)
        #win = StatusGame(self, self.screen_wh)

    def __accion_connecting_players_server(self, con_players, valor):
        if valor == "jugar":
            self.servermodel.new_handler_anuncio(False)
            self.servermodel.new_handler_registro(False)
            self.__kill_connectingplayers()
            xid = self.get_property('window').xid
            self.servermodel.rungame(xid, self.gameres)
            #win = StatusGame(self, self.screen_wh)
        elif valor == "cancelar":
            self.__switch(False, 3)

    def __accion_connecting_players_client(self, con_players, valor):
        #if valor == "jugar":
        #    print "connecting_players_client recibe jugar"
        #elif valor == "cancelar":
        if valor == "cancelar":
            self.__switch(False, 4)

    def __kill_client_model(self):
        if self.clientmodel:
            self.clientmodel.close_all_and_exit()
            for h in self.handlers.get('clientmodel', []):
                if self.clientmodel.handler_is_connected(h):
                    self.clientmodel.handler_disconnect(h)
            for h in self.handlers.get('clientmodel', []):
                del(h)
            try:
                self.clientmodel.destroy()
            except:
                pass
        self.handlers['clientmodel'] = []
        del(self.clientmodel)
        self.clientmodel = False

    def __kill_server_model(self):
        if self.servermodel:
            self.servermodel.close_all_and_exit()
            for h in self.handlers.get('servermodel', []):
                if self.servermodel.handler_is_connected(h):
                    self.servermodel.handler_disconnect(h)
            for h in self.handlers.get('servermodel', []):
                del(h)
            try:
                self.servermodel.destroy()
            except:
                pass
        self.handlers['servermodel'] = []
        del(self.servermodel)
        self.servermodel = False

    def __key_press_event(self, widget, event):
        if self.selectmode:
            if gtk.gdk.keyval_name(event.keyval) == "Escape":
                self.__salir()
                return False
        elif self.servermodel:
            self.servermodel.process_key_press(event)
        elif self.clientmodel:
            self.clientmodel.process_key_press(event)
        return False

    def __key_release_event(self, widget, event):
        if self.servermodel:
            self.servermodel.process_key_release(event)
        elif self.clientmodel:
            self.clientmodel.process_key_release(event)
        return False

    def __kill_create_mode(self):
        if self.createclientmode:
            for h in self.handlers.get('createclientmode', []):
                if self.createclientmode.handler_is_connected(h):
                    self.createclientmode.handler_disconnect(h)
            for h in self.handlers.get('createclientmode', []):
                del(h)
            self.createclientmode.kill_all()
            try:
                self.createclientmode.destroy()
            except:
                pass
        self.handlers['createclientmode'] = []
        del(self.createclientmode)
        self.createclientmode = False
        if self.createservermode:
            for h in self.handlers.get('createservermode', []):
                if self.createservermode.handler_is_connected(h):
                    self.createservermode.handler_disconnect(h)
            for h in self.handlers.get('createservermode', []):
                del(h)
            try:
                self.createservermode.destroy()
            except:
                pass
        self.handlers['createservermode'] = []
        del(self.createservermode)
        self.createservermode = False

    def __kill_select_mode(self):
        if self.selectmode:
            for h in self.handlers.get('selectmode', []):
                if self.selectmode.handler_is_connected(h):
                    self.selectmode.handler_disconnect(h)
            for h in self.handlers.get('selectmode', []):
                del(h)
            try:
                self.selectmode.destroy()
            except:
                pass
        self.handlers['clientmodel'] = []
        del(self.selectmode)
        self.selectmode = False

    def __kill_connectingplayers(self):
        if self.connectingplayers:
            for h in self.handlers.get('connectingplayers', []):
                if self.connectingplayers.handler_is_connected(h):
                    self.connectingplayers.handler_disconnect(h)
            for h in self.handlers.get('connectingplayers', []):
                del(h)
            try:
                self.connectingplayers.destroy()
            except:
                pass
        self.handlers['clientmodel'] = []
        del(self.connectingplayers)
        self.connectingplayers = False

    def __salir(self, widget=None, event=None):
        self.__reset()
        self.disconnect_by_func(self.__salir)
        self.disconnect_by_func(self.__key_press_event)
        self.disconnect_by_func(self.__key_release_event)
        self.disconnect_by_func(self.__do_realize)
        gtk.main_quit()
        sys.exit(0)


if __name__ == "__main__":
    JAMTank()
    gtk.main()
