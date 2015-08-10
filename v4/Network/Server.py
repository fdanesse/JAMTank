#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import SocketServer
import cPickle as pickle

T = "\r\n\r\n"


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
                entrada = self.rfile.readline().split("\n")[0]
                if not entrada:
                    self.request.close()
                    return

                respuesta = self.__procesar(
                    entrada, str(self.client_address[0]))

                if respuesta:
                    self.wfile.write("%s\n" % respuesta)
                else:
                    self.request.close()

            except socket.error, err:
                print "Error en el Server:", err
                #Desconexion: [Errno 104] Conexión reinicializada por la máquina remota
                self.request.close()

    #def finish(self):
    #def setup(self):

    def __procesar(self, entrada, ip):
        try:
            _dict = pickle.loads(entrada)
            if _dict.get("register", False):
                return self.server.registrar(ip, _dict)
            else:
                return self.__make_resp({})
        except:
            print "Server pickle Error:"
            return self.__make_resp({})

    def __make_resp(self, new):
        new["z"] = ""
        message = pickle.dumps(new, 2)
        message = "%s%s" % (message, T)
        l = len(message)
        if l < 1024:
            x = 1024 - l
            new["z"] = " " * (x - 3)
            message = pickle.dumps(new, 2)
            message = "%s%s" % (message, T)
        elif l > 1023:
            print "Sobre Carga en la Red:", l
        #t = open("/tmp/xx.dat", 'w')
        #pickle.dump(new, t)
        #t.flush()
        #t.close()
        return message


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

        self.registrados = 0
        self._dict_game = dict(_dict)  # n°de jugadores, mapa, vidas
        self._dict_game["mapa"] = _dict["mapa"]
        self._players_dict = {}

        print "Server ON:", "ip:", host, "Port:", port
        print "\tDatos:"
        for item in self._dict_game.items():
            print "\t\t", item

    def __make_resp(self, new):
        new["z"] = ""
        message = pickle.dumps(new, 2)
        message = "%s%s" % (message, T)
        l = len(message)
        if l < 1024:
            x = 1024 - l
            new["z"] = " " * (x - 3)
            message = pickle.dumps(new, 2)
            message = "%s%s" % (message, T)
        elif l > 1023:
            print "Sobre Carga en la Red:", l
        #t = open("/tmp/x.dat", 'w')
        #pickle.dump(new, t)
        #t.flush()
        #t.close()
        return message

    def registrar(self, ip, _dict):
        permitidos = self._dict_game["jugadores"]
        new = {}
        if self.registrados == 0 or self.registrados < permitidos:
            # El jugador se registra
            self._players_dict[ip] = dict(_dict["register"])
            self.registrados = len(self._players_dict.keys())
            self._dict_game["todos"] = bool(
                self.registrados == self._dict_game["jugadores"])
            new["aceptado"] = True
            new["game"] = dict(self._dict_game)
            new["players"] = dict(self._players_dict)
        elif self.registrados != 0 and self.registrados == permitidos:
            # Todos están registrados y el juego está cerrado a nuevas ips
            if self._players_dict.get(ip, False):
                self._dict_game["todos"] = bool(
                    self.registrados == self._dict_game["jugadores"])
                new["aceptado"] = True
                new["game"] = dict(self._dict_game)
                new["players"] = dict(self._players_dict)
                #FIXME: si running, running a todos
            else:
                # este jugador no puede jugar
                new["aceptado"] = False
        else:
            print "FIXME: hay más jugadores de los permitidos"
            # este jugador no puede jugar
            new["aceptado"] = False
        return self.__make_resp(new)

    def shutdown(self):
        print "Server OFF"
        SocketServer.ThreadingTCPServer.shutdown(self)
