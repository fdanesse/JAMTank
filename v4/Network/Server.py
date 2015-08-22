#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import SocketServer
import ast
import time

T = "\n"


class RequestHandler(SocketServer.StreamRequestHandler):
    """
    s.RequestHandlerClass.disable_nagle_algorithm  s.RequestHandlerClass.setup
    s.RequestHandlerClass.finish                   s.RequestHandlerClass.timeout
    s.RequestHandlerClass.handle                   s.RequestHandlerClass.wbufsize
    s.RequestHandlerClass.rbufsize
    """
    """
    ["_RequestHandler__procesar", "__doc__", "__init__", "__module__",
    "client_address", "connection", "disable_nagle_algorithm", "finish",
    "handle", "rbufsize", "request", "rfile", "server", "setup", "timeout",
    "wbufsize", "wfile"]
    """
    def handle(self):
        while 1:
            try:
                """
                ["__class__", "__del__", "__delattr__", "__doc__", "__format__",
                "__getattribute__", "__hash__", "__init__", "__iter__", "__module__",
                "__new__", "__reduce__", "__reduce_ex__", "__repr__", "__setattr__",
                "__sizeof__", "__slots__", "__str__", "__subclasshook__",
                "_close", "_getclosed", "_rbuf", "_rbufsize", "_sock", "_wbuf",
                "_wbuf_len", "_wbufsize", "bufsize", "close", "closed",
                "default_bufsize", "fileno", "flush", "mode", "name", "next",
                "read", "readline", "readlines", "softspace", "write", "writelines"]
                """
                entrada = self.rfile.readline()
                if not entrada:
                    self.request.close()
                    return

                respuesta = self.__procesar(
                    entrada, str(self.client_address[0]))

                if respuesta:
                    self.wfile.write(respuesta)
                else:
                    self.request.close()

            except socket.error, err:
                print "Error en el Server:", err
                #Desconexion: [Errno 104] Conexión reinicializada por la máquina remota
                self.request.close()

    #def finish(self):
    #def setup(self):

    def __procesar(self, entrada, ip):
        """
        Espera una linea string que termina con "\n" y que ast puede convertir
        en un diccionario python.
        """
        ret = {"aceptado": False}
        try:
            _dict = ast.literal_eval(entrada)
            if _dict.get("register", False):
                ret = self.server.registrar(ip, _dict)
            elif _dict.get("ingame", False):
                ret = self.server.ingame(ip, _dict)
            else:
                print "No Implementado Server Recibe:", entrada
        except:
            print "Server Error:", entrada
        return self.__make_resp(ret)

    def __make_resp(self, new):
        """
        Escribe un diccionario convertido a str y con la terminacion "\n"
        """
        return "%s%s" % (str(new), T)


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):
    """
    s.RequestHandlerClass     s.finish_request          s.process_request_thread
    s.address_family          s.get_request             s.server_bind
    s.allow_reuse_address     s.handle_error            s.server_close
    s.close_request           s.handle_request          s.request_queue_size
    s.daemon_threads          s.handle_timeout          s.serve_forever
    s.fileno                  s.process_request         s.server_activate
    s.socket_type             s.socket                  s.shutdown_request
    s.shutdown                s.verify_request          s.timeout
    s.server_address
    """

    def __init__(self, logger=None, host="localhost",
        port=5000, handler=RequestHandler, _dict={}):

        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.allow_reuse_address = True
        self.socket.setblocking(0)

        self.ip = host
        self._dict_game = dict(_dict)  # n°de jugadores, mapa, vidas
        self._players_dict = {}
        self._time_control_players = {}
        self.latency = {}

        print "Server ON:", "ip:", host, "Port:", port
        print "\tDatos:"
        for item in self._dict_game.items():
            print "\t\t", item

    def __timer_control_players(self, _ip):
        """
        Más de 1.5 segundos entre conexiones = jugador desconectado
        """
        now = time.time()
        self._time_control_players[_ip] = now
        for ip in self._players_dict.keys():
            if now - self._time_control_players[ip] > 1.5:
                del(self._players_dict[ip])
                del(self._time_control_players[ip])
                del(self.latency[ip])

    def __registrar(self, ip, _dict):
        self._players_dict[ip] = dict(_dict["register"])
        self._dict_game["todos"] = bool(
            len(self._players_dict.keys()) == self._dict_game["jugadores"])
        if _dict.get("register", False):
            del(_dict["register"])
        _dict["aceptado"] = True
        _dict["game"] = dict(self._dict_game)
        _dict["players"] = dict(self._players_dict)
        return _dict

    def registrar(self, ip, _dict):
        self.__timer_control_players(ip)

        if ip == self.ip:
            if _dict["register"].get("off", False):
                print "Server Recibe register off:", _dict
                self._dict_game["jugadores"] = 0
                self._players_dict = {}

        permitidos = self._dict_game["jugadores"]
        new = {}
        if self._players_dict.get(ip, False):
            # jugadores en handler registro
            new = self.__registrar(ip, _dict)
        else:
            if len(self._players_dict.keys()) < permitidos:
                # El jugador se registra
                print "Servidor Registrando un nuevo jugador:", ip, _dict
                new = self.__registrar(ip, _dict)
            else:
                # Este jugador no jugara, el juego está cerrado a nuevas ips.
                new["aceptado"] = False
        return new

    def ingame(self, ip, _dict):
        self.__timer_control_players(ip)
        if ip == self.ip:
            if _dict.get("off", False):
                # El host quiere salir, manda desconectar a todos
                self._dict_game["run"] = False
            else:
                # Anuncia inicio del juego a quienes estan en fase de registro
                self._dict_game["run"] = True

        new = {"ingame": True, "off": True}
        if self._dict_game["run"]:

            # Persistencia de datos de jugador
            _ing = dict(_dict["ingame"])
            for key in _ing.keys():
                self._players_dict[ip][key] = _ing[key]
            new = {"ingame": dict(self._players_dict)}

            # Recalculo de latencia
            if "l" in _dict.keys():
                self.latency[ip] = int(_dict.get("l", 0))
                l = 0
                lat = dict(self.latency)
                del(lat[ip])
                if lat:
                    l = max(lat.values())
                new["l"] = l

        else:
            # El host manda salir
            new = {
                "ingame": dict(self._players_dict),
                "off": True}
        return new

    def shutdown(self):
        SocketServer.ThreadingTCPServer.shutdown(self)
        print "Server OFF"
