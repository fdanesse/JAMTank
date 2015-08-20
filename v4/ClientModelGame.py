#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gobject
import gtk
import time
from Network.Client import Client
from Juego.Juego import Juego

BASE_PATH = os.path.realpath(os.path.dirname(__file__))


class ClientModelGame(gobject.GObject):

    __gsignals__ = {
    "error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    "players": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, )),
    "play-run": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    "end-game": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, _host, _dict, _nick, _tank):

        gobject.GObject.__init__(self)

        self._host = _host
        self._dict = _dict  # jugadores, mapa, vidas
        self._nick = _nick
        self._tank = _tank
        self.client = False
        self.juego = False
        self.eventos = []
        self.registro = False
        self.default_retorno = {"aceptado": False, "game": {}}

    def __handler_registro(self):
        new = {
            "register": {
                "t": "%s" % self._tank,
                "n": "%s" % self._nick,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir(dict(self.default_retorno))
        self.default_retorno["aceptado"] = _dict.get("aceptado", False)
        if _dict.get("aceptado", False):
            self.emit("players", dict(_dict.get("players", {})))
            self.default_retorno["game"] = _dict.get("game", {})
            if _dict["game"].get("run", False):
                self.emit("play-run")
        else:
            print "FIXME: Cliente no aceptado como jugador."
            self.emit("error")
        return bool(self.registro)

    def __register_client_in_server(self):
        print "Registrando Cliente no host en el Servidor..."
        new = {
            "register": {
                "t": "%s" % self._tank,
                "n": "%s" % self._nick,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir(dict(self.default_retorno))
        self.default_retorno["aceptado"] = _dict.get("aceptado", False)
        if _dict.get("aceptado", False):
            print "\t Cliente no Host Registrado:"
            for item in _dict.items():
                print "\t\t", item
            return True
        else:
            print "Cliente no Host rechazado por el Servidor"
            return False

    def __kill_client(self):
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False

    def __client_error(self, client, valor):
        print "Error del Cliente recibido en ClientModel", valor
        self.emit("error")

    def new_handler_registro(self, reset):
        if self.registro:
            gobject.source_remove(self.registro)
            self.registro = False
        if reset:
            print "Esperando Jugadores..."
            self.registro = gobject.timeout_add(100, self.__handler_registro)

    def client_run(self):
        self.client = Client(self._host)
        connected = self.client.conectarse()
        print "Cliente Creado:", connected
        if connected:
            self.client.connect("error", self.__client_error)
            return self.__register_client_in_server()
        else:
            return False

    def close_all_and_exit(self):
        self.new_handler_registro(False)
        self.__kill_client()

    def process_key_press(self, event):
        nombre = gtk.gdk.keyval_name(event.keyval)
        if self.juego:
            teclas = ["w", "s", "d", "a", "space", "Escape"]
            if nombre in teclas and not nombre in self.eventos:
                if nombre == "w" and "s" in self.eventos:
                    self.eventos.remove("s")
                elif nombre == "s" and "w" in self.eventos:
                    self.eventos.remove("w")
                elif nombre == "d" and "a" in self.eventos:
                    self.eventos.remove("a")
                elif nombre == "a" and "d" in self.eventos:
                    self.eventos.remove("d")
                self.eventos.append(nombre)
            self.juego.update_events(self.eventos)
        else:
            if nombre == "Escape":
                self.emit("error")

    def process_key_release(self, event):
        if self.juego:
            nombre = gtk.gdk.keyval_name(event.keyval)
            teclas = ["w", "s", "d", "a", "space", "Escape"]
            if nombre in teclas and nombre in self.eventos:
                self.eventos.remove(nombre)
            self.juego.update_events(self.eventos)
        else:
            self.eventos = []

    def rungame(self, xid, res):
        # Debe comenzar a correr en menos de 1.5 segundos
        mapa = os.path.join(BASE_PATH, "Mapas", self._dict.get("mapa", ""))
        self.juego = Juego()
        self.juego.connect("exit", self.__exit_game)
        self.juego.config(time=35, res=res, client=self.client, xid=xid)
        tanque = os.path.join(BASE_PATH, "Tanques", self._tank)
        self.juego.load(mapa, tanque, self._nick)
        self.juego.run()

    def __exit_game(self, game, _dict):
        if self.juego:
            self.juego.disconnect_by_func(self.__exit_game)
            del(self.juego)
            self.juego = False
            time.sleep(0.5)
        self.__kill_client()
        self.emit("end-game", _dict)
