#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import socket
import time
import threading

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client


def __make_anuncio(new):
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


def terminate_thread(thread):
    """
    Termina un hilo python desde otro hilo.
    thread debe ser una instancia threading.Thread
    """
    if not thread.isAlive():
        return
    import ctypes
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
    "error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])}

    def __init__(self, _host, _dict, _nick_host, _tank_host):

        gobject.GObject.__init__(self)

        self._host = _host
        self._dict = _dict  # jugadores, mapa, vidas
        self._nick_host = _nick_host
        self._tank_host = _tank_host
        self.server_thread = False
        self.server = False
        self.publicar = False
        self.registro = False
        self.dict_players = {}

    def new_handler_registro(self, reset):
        if self.registro:
            gobject.source_remove(self.registro)
            self.registro = False
        if reset:
            print "Esperando Jugadores..."
            self.registro = gobject.timeout_add(35, self.__handler_registro)

    def __handler_registro(self):
        #FIXME: Enviar <> recibir
        #   Cuando se recibe, los jugadores debe actualizarse en ConnectingPlayers
        #   Al recibir todos == True, se debe habilitar jugar en ConnectingPlayers
        #Cuando el jugador arctiva jugar en ConnectingPlayers:
        #   Se manda running al Servidor, entonces:
        #       en enviar <> recibir: cuando se recibe running == True
        #           Se debe detener la publicación del server
        #           Se debe detener enviar <> recibir
        #           Y se debe lanzar el juego
        new = {
            "register": {
                "tank": "%s" % self._tank_host,
                "nick": "%s" % self._nick_host,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir()
        del(_dict["z"])
        print "Recibido:", _dict
        '''
        try:
            _dict = pickle.loads(retorno)
            if _dict.get("aceptado", False):
                # Jugador aceptado
                del(_dict["z"])
                print "\tRegistrado:"
                for item in _dict.items():
                    print "\t\t", item
                """
                {
                "aceptado": True,
                "game": {
                    "todos": False, "jugadores": 2, "vidas": 5,
                    "mapa": "fondo0.png"
                    },
                "z": "",
                "players": {
                    "192.168.1.11": {
                        "nick": "flavio",
                        "tank": "tanque-1.png"
                        }
                    }
                }
                """
                self.dict_players = dict(_dict.get("players", {}))
        except:
            print "Server Model pickle Error"
        self.new_handler_registro(False)
        self.__new_handler_anuncio(False)
        self.client.desconectarse()
        '''
        return bool(self.registro)

    def __new_handler_anuncio(self, reset):
        if self.publicar:
            gobject.source_remove(self.publicar)
            self.publicar = False
        if reset:
            print "Publicando Juego en la red..."
            self.publicar = gobject.timeout_add(1000, self.__handler_anuncio)

    def __handler_anuncio(self):
        if not self.server:
            return False
        if self.server.registrados < self._dict.get("jugadores", 0):
            new = dict(self._dict)
            new["ip"] = self._host
            new["nickh"] = self._nick_host
            print "Anunciando:", time.time(), new
            message = "%s\n" % __make_anuncio(new)  # carga debe ser 150
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            my_socket.sendto(message, ("<broadcast>", 10000))
            my_socket.close()
            return True
        else:
            print "FIXME: Todos los Jugadores Conectados"
            return False

    def __client_run(self):
        self.client = Client(self._host)
        connected = self.client.conectarse()
        print "Cliente Creado:", connected
        if connected:
            return self.__register_client_in_server()
        else:
            return False

    def __register_client_in_server(self):
        print "Registrando Cliente del host en el Servidor..."
        new = {
            "register": {
                "tank": "%s" % self._tank_host,
                "nick": "%s" % self._nick_host,
                },
            }
        self.client.enviar(new)
        _dict = self.client.recibir()
        if _dict.get("aceptado", False):
            # Jugador aceptado
            del(_dict["z"])
            print "\tRegistrado:"
            for item in _dict.items():
                print "\t\t", item
            """
            {
            "aceptado": True,
            "game": {
                "todos": False, "jugadores": 2, "vidas": 5,
                "mapa": "fondo0.png"
                },
            "z": "",
            "players": {
                "192.168.1.11": {
                    "nick": "flavio",
                    "tank": "tanque-1.png"
                    }
                }
            }
            """
            self.dict_players = dict(_dict.get("players", {}))
            return True
        else:
            print "Jugador rechazado. FIXME: No debiera ocurrir nunca, dado que este es el host"
            return False

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

        print self._nick_host, "Ha Creado un Juego en la red"

        if self.__client_run():
            return True
        else:
            print "FIXME: El Cliente del host falla en el registro"
            self.client.desconectarse()
            self.__new_handler_anuncio(False)
            self.server.server_close()
            self.server.shutdown()
            self.server.socket.close()
            del(self.server)
            self.server = False
            terminate_thread(self.server_thread)
            del(self.server_thread)
            self.server_thread = False
            self.emit("error")
            return False

    def __join_player(self, servermodel, ip, nick):
        print self.__join_player, ip, nick

    def __remove_player(self, servermodel, ip):
        print self.__remove_player, ip
