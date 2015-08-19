#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gobject
import socket
import time
import threading
import ctypes
import cPickle as pickle
import gtk

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client
from Juego.Juego import Juego

BASE_PATH = os.path.realpath(os.path.dirname(__file__))


def terminate_thread(thread):
    """
    Termina un hilo python desde otro hilo.
    thread debe ser una instancia threading.Thread
    """
    if not thread.isAlive():
        return
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("No Existe el id de este hilo")
    elif res > 1:
        """
        si devuelve un número mayor que uno, estás en problemas, entonces
        llamas de nuevo con exc = NULL para revertir el efecto.
        """
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ServerModelGame(gobject.GObject):

    __gsignals__ = {
    "error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
    "players": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, )),
    "play-enabled": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_BOOLEAN, ))}

    def __init__(self, _host, _dict, _nick, _tank):

        gobject.GObject.__init__(self)

        self._host = _host
        self._dict = _dict  # jugadores, mapa, vidas
        self._nick = _nick
        self._tank = _tank
        self.server_thread = False
        self.server = False
        self.client = False
        self.juego = False
        self.eventos = []
        self.publicar = False
        self.registro = False
        self.default_retorno = {"aceptado": False, "game": {}}

    def __handler_registro(self):
        new = {
            "register": {
                "tank": "%s" % self._tank,
                "nick": "%s" % self._nick,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir(dict(self.default_retorno))
        self.default_retorno["aceptado"] = _dict.get("aceptado", False)
        if _dict.get("aceptado", False):
            self.emit("players", dict(_dict.get("players", {})))
            self.default_retorno["game"] = _dict.get("game", {})
            dict_game = _dict.get("game", False)
            if dict_game.get("todos", False):
                self.new_handler_anuncio(False)
                self.emit("play-enabled", True)
            else:
                self.emit("play-enabled", False)
                if not self.publicar:
                    self.new_handler_anuncio(True)
        else:
            print "FIXME: Host no aceptado como jugador."
            self.emit("error")
        return bool(self.registro)

    def __make_anuncio(self, new):
        # carga debe ser 150
        new["z"] = ""
        message = pickle.dumps(new, 2)
        l = len(message)
        if l < 150:
            x = 149 - l
            new["z"] = " " * x
            message = pickle.dumps(new, 2)
        elif l > 150:
            print "Sobre Carga en la Red:", l
        return message

    def __handler_anuncio(self):
        if not self.server:
            return False
        new = dict(self._dict)
        new["ip"] = self._host
        new["nickh"] = self._nick
        message = "%s\n" % self.__make_anuncio(new)  # carga debe ser 150
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        my_socket.sendto(message, ("<broadcast>", 10000))
        my_socket.close()
        return bool(self.publicar)

    def __client_run(self):
        self.client = Client(self._host)
        connected = self.client.conectarse()
        print "Cliente del Host Creado:", connected
        if connected:
            self.client.connect("error", self.__client_error)
            return self.__register_client_in_server()
        else:
            return False

    def __register_client_in_server(self):
        print "Registrando Cliente del host en el Servidor..."
        new = {
            "register": {
                "tank": "%s" % self._tank,
                "nick": "%s" % self._nick,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir(dict(self.default_retorno))
        self.default_retorno["aceptado"] = _dict.get("aceptado", False)
        if _dict.get("aceptado", False):
            print "\tCliente del Host Registrado:"
            for item in _dict.items():
                print "\t\t", item
            return True
        else:
            print "Cliente del Host rechazado por el Servidor"
            return False

    def __kill_server(self):
        if self.server:
            self.server.server_close()
            self.server.shutdown()
            self.server.socket.close()
            del(self.server)
            self.server = False
        if self.server_thread:
            terminate_thread(self.server_thread)
            del(self.server_thread)
            self.server_thread = False

    def __kill_client(self):
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False

    def __client_error(self, client, valor):
        print valor
        self.emit("error")

    def new_handler_anuncio(self, reset):
        if self.publicar:
            gobject.source_remove(self.publicar)
            self.publicar = False
        if reset:
            print "Publicando Juego en la red..."
            self.publicar = gobject.timeout_add(1000, self.__handler_anuncio)

    def new_handler_registro(self, reset):
        if self.registro:
            gobject.source_remove(self.registro)
            self.registro = False
        if reset:
            print "Esperando Jugadores..."
            self.registro = gobject.timeout_add(100, self.__handler_registro)

    def server_run(self):
        try:
            self.server = Server(host=self._host,
                port=5000, handler=RequestHandler, _dict=self._dict)
            self.server_thread = threading.Thread(
                target=self.server.serve_forever)
            self.server_thread.setDaemon(True)
            self.server_thread.start()
            time.sleep(0.5)
        except:
            print "EL Servidor no pudo Iniciar."
            self.emit("error")
            return False

        print "Server Corriendo: True"
        print self._nick, "Ha Creado un Juego en la red"

        if self.__client_run():
            return True
        else:
            print "FIXME: El Cliente del host falla en el registro"
            self.__kill_client()
            self.__kill_server()
            self.emit("error")
            return False

    def close_all_and_exit(self):
        self.new_handler_anuncio(False)
        self.new_handler_registro(False)

        # FIXME: Terminar juego

        if self.client:
            time.sleep(0.5)
            new = {"register": {"off": True}}
            self.client.enviar(new)
            _dict = self.client.recibir(dict(self.default_retorno))
            print "ServerModel recibe:", _dict
            time.sleep(0.5)

        self.__kill_client()
        self.__kill_server()

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
        mapa = os.path.join(BASE_PATH, "Mapas", self._dict.get('mapa', ''))
        self.juego = Juego()
        self.juego.connect("exit", self.__exit_game)
        self.juego.config(time=35, res=res, client=self.client, xid=xid)
        tanque = os.path.join(BASE_PATH, "Tanques", self._tank)
        self.juego.load(mapa, tanque, self._nick)
        self.juego.run()

    def __exit_game(self, game):
        if self.juego:
            self.juego.disconnect_by_func(self.__exit_game)
            del(self.juego)
            self.juego = False
        # FIXME: El servidor debe desconectar a los clientes
        self.emit("error")
