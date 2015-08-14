#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import socket
import time

from Network.Client import Client


class ClientModelGame(gobject.GObject):

    __gsignals__ = {
    "error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    "players": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, )),
    #"play-enabled": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
    #    (gobject.TYPE_BOOLEAN, )),
    "play-run": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])}

    def __init__(self, _host, _dict, _nick_host, _tank_host):

        gobject.GObject.__init__(self)

        self._host = _host
        self._dict = _dict  # jugadores, mapa, vidas
        self._nick_host = _nick_host
        self._tank_host = _tank_host
        self.registro = False
        #self.running = False

    def __handler_registro(self):
        new = {
            "register": {
                "tank": "%s" % self._tank_host,
                "nick": "%s" % self._nick_host,
                },
            }
        #if self.running:
        #    new['running'] = True
        self.client.enviar(new)
        _dict = self.client.recibir()
        if _dict.get("aceptado", False):
            self.emit("players", dict(_dict.get("players", {})))
            #if _dict.get("todos", False):
            #    self.emit("play-enabled", True)
            #else:
            #    # FIXME: Verificar esto 2
            #    self.running = False
            #    self.emit("play-enabled", False)
            #    if not self.publicar:
            #        self.new_handler_anuncio(True)
            if _dict.get("running", False):
                # FIXME: Verificar si esto debe ir acá
                #self.new_handler_anuncio(False)
                self.new_handler_registro(False)
                self.emit("play-run")
        else:
            print "FIXME: Cliente no aceptado como jugador."
            self.close_all_and_exit()
            self.emit("error")
        return bool(self.registro)

    def client_run(self):
        self.client = Client(self._host)
        connected = self.client.conectarse()
        print "Cliente Creado:", connected
        if connected:
            return self.__register_client_in_server()
        else:
            return False

    def __register_client_in_server(self):
        print "Registrando Cliente no host en el Servidor..."
        new = {
            "register": {
                "tank": "%s" % self._tank_host,
                "nick": "%s" % self._nick_host,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir()
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

    def new_handler_registro(self, reset):
        if self.registro:
            gobject.source_remove(self.registro)
            self.registro = False
        if reset:
            print "Esperando Jugadores..."
            self.registro = gobject.timeout_add(100, self.__handler_registro)

    def close_all_and_exit(self):
        #self.running = False
        self.new_handler_registro(False)
        self.__kill_client()
