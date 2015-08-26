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
    s.RequestHandlerClass.finish                 s.RequestHandlerClass.timeout
    s.RequestHandlerClass.handle                 s.RequestHandlerClass.wbufsize
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
                ["__class__", "__del__", "__delattr__", "__doc__",
                "__format__", "__getattribute__", "__hash__", "__init__",
                "__iter__","__module__", "__new__", "__reduce__",
                "__reduce_ex__", "__repr__", "__setattr__", "__sizeof__",
                "__slots__", "__str__", "__subclasshook__", "_close",
                "_getclosed", "_rbuf", "_rbufsize", "_sock", "_wbuf",
                "_wbuf_len", "_wbufsize", "bufsize", "close", "closed",
                "default_bufsize", "fileno", "flush", "mode", "name",
                "next", "read", "readline", "readlines", "softspace",
                "write", "writelines"]
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
    RequestHandlerClass     finish_request        process_request_thread
    address_family          get_request           server_bind
    allow_reuse_address     handle_error          server_close
    close_request           handle_request        request_queue_size
    daemon_threads          handle_timeout        serve_forever
    fileno                  process_request       server_activate
    socket_type             socket                shutdown_request
    shutdown                verify_request        timeout
    server_address
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
        self._latencias = {}
        self._max_lat = 0.0
        self._enviar_lat = []

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
                del(self._latencias[ip])
                self.__latency_recalc()

    def __latency_recalc(self):
        self._max_lat = float("%.3f" % max(self._latencias.values()))
        print "Server Recalculando Latencia General:", self._max_lat
        # ips a las que se debe informar
        self._enviar_lat = self._latencias.keys()

    def __latency_check(self, ip, latencia, new):
        # Almacenar latencias de clientes
        if latencia:
            self._latencias[ip] = latencia
            print "Server Almacenando Latencia:", ip, latencia
            if len(self._latencias) == self._dict_game["jugadores"]:
                # Cuando todos esten conectados se calcula latencia general
                self.__latency_recalc()
        if ip in self._enviar_lat:
            # Informe de latencia
            self._enviar_lat.remove(ip)
            new["l"] = self._max_lat

    def __convert_colisiones(self, ip):
        # Convertir colisiones en explosiones
        col = list(self._players_dict[ip].get("c", []))
        exp = []
        for c in col:
            exp.append({"x": c["x"], "y": c["y"]})
        self._players_dict[ip]["e"] = exp
        if "c" in self._players_dict[ip].keys():
            del(self._players_dict[ip]["c"])

        # Convertir colisiones en energia, vidas, puntos,
        #'s': {'p': 0, 'e': 100, 'v': 5})
        for c in col:
            _ip, x, y = c["ip"], c["x"], c["y"]
            self._players_dict[_ip]["s"]["e"] -= 10
            self._players_dict[ip]["s"]["p"] += 1
            if self._players_dict[_ip]["s"]["e"] <= 0:
                self._players_dict[_ip]["s"]["v"] -= 1
                self._players_dict[ip]["s"]["p"] += 2
            if self._players_dict[_ip]["s"]["v"] <= 0:
                #Este jugador no puede jugar más
                pass
        # FIXME: Checkeo de fin del juego

    def __registrar(self, ip, _dict):
        self._players_dict[ip] = dict(_dict["register"])
        self._players_dict[ip]["s"] = {"e": 100,
            "v": self._dict_game["vidas"], "p": 0}
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
            # Persistencia de datos de jugador FIXME: y sus balas
            _ing = dict(_dict["ingame"])

            for key in _ing.keys():
                self._players_dict[ip][key] = _ing[key]

            # Convertir colisiones en energia, vidas, puntos, explosiones
            self.__convert_colisiones(ip)

            new = {"ingame": dict(self._players_dict)}

            # Control de latencia
            self.__latency_check(ip,
                float("%.3f" % (_dict.get("l", 0.0))), new)

        else:
            # El host manda salir
            new = {
                "ingame": dict(self._players_dict),
                "off": True}
        return new

    def shutdown(self):
        SocketServer.ThreadingTCPServer.shutdown(self)
        print "Server OFF"
