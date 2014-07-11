#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
#   Flavio Danesse <fdanesse@gmail.com>

import socket
import SocketServer

TERMINATOR = "\r\n\r\n"

GAME = {
    'mapa': "",
    'enemigos': 0,
    'vidas': 0,
    }

MODEL = {
    'nick': '',
    'tanque': {
        'path': '',
        'pos': (0, 0, 0),
        'energia': 100,
        },
    'vidas': 0,
    'puntos': 0,
    'bala': ()
    }

JUGADORES = {}


class Server(SocketServer.ThreadingMixIn,
    SocketServer.ThreadingTCPServer):
    pass


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while 1:
            try:
                datos = self.request.recv(512)
                respuesta = self.__procesar(datos)
                self.request.send(respuesta)
            except socket.error, err:
                print "Error en Server: ", err, self.client_address[0]
                self.request.close()
                return

    def __procesar(self, datos):
        mensajes = datos.split(TERMINATOR)

        for mensaje in mensajes:
            if mensaje.startswith('CONNECT*'):
                return self.__check_enemigos()

            # Configuración del juego:
            elif mensaje.startswith('M*'):
                GAME['mapa'] = mensaje.split('M*')[-1].strip()
            elif mensaje.startswith('E*'):
                GAME['enemigos'] = int(mensaje.split('E*')[-1].strip())
            elif mensaje.startswith('V*'):
                GAME['vidas'] = int(mensaje.split('V*')[-1].strip())

            # Configuración de Jugador:
            elif mensaje.startswith('N*'):
                self.__add_nick(mensaje.split('N*')[-1].strip())
            elif mensaje.startswith('T*'):
                self.__add_tanque(mensaje.split('T*')[-1].strip())

            # Posición y Angulo de Tanque:
            elif mensaje.startswith('TP*'):
                self.__update_player(mensaje.split('TP*')[-1].strip())

            else:
                pass

        return self.__return_data()

    def __return_data(self):
        _buffer = ""
        for ip in JUGADORES.keys():
            _buffer = "%sPLAYER*%s**" % (_buffer, ip)
            _buffer = "%snick*%s**" % (_buffer, JUGADORES[ip].get('nick', " "))

            path = JUGADORES[ip]['tanque']['path']
            a, x, y = JUGADORES[ip]['tanque']['pos']
            energia = JUGADORES[ip]['tanque']['energia']
            _buffer = "%stanque*%s %s %s %s %s**" % (_buffer, path, a, x, y, energia)

            _buffer = "%svidas*%s**" % (_buffer, JUGADORES[ip]['vidas'])
            _buffer = "%spuntos*%s**" % (_buffer, JUGADORES[ip]['puntos'])
            _buffer = "%sbala*%s**" % (_buffer, JUGADORES[ip]['bala'])
            _buffer = "%s%s" % (_buffer, TERMINATOR)

        return _buffer

    def __check_enemigos(self):
        ips = JUGADORES.keys()
        if self.client_address[0] in ips:
            return "CONNECT*%s %s%s" % (GAME['mapa'], GAME['vidas'], TERMINATOR)
        if len(ips) < GAME['enemigos']:
            return "CONNECT*%s %s%s" % (GAME['mapa'], GAME['vidas'], TERMINATOR)
        else:
            return "CLOSE*%s" % TERMINATOR

    def __add_nick(self, nick):
        self.__check_jugador()
        JUGADORES[self.client_address[0]]['nick'] = nick

    def __add_tanque(self, tanque):
        self.__check_jugador()
        JUGADORES[self.client_address[0]]['tanque']['path']= tanque

    def __update_player(self, mensaje):
        self.__check_jugador()
        angulo, x, y = mensaje.split()
        JUGADORES[self.client_address[0]]['tanque']['pos'] = (int(angulo),
            int(x), int(y))

    def __check_jugador(self):
        if not self.client_address[0] in JUGADORES.keys():
            JUGADORES[self.client_address[0]] = MODEL.copy()

if __name__ == "__main__":
    ret = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com", 80))
        ret = s.getsockname()[0]
        s.close()
    except:
        ret = ''

    GAME['mapa'] = "fondo1.png"
    GAME['enemigos'] = 1
    GAME['vidas'] = 10

    if ret:
        import threading
        server = Server((ret, 5000), RequestHandler)
        server.allow_reuse_address = True
        server.socket.setblocking(0)
        server.serve_forever()

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()
