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

'''
MODEL = {
    'nick': '',
    'tanque': {
        'path': '',
        'pos': (0, 0, 0),
        'energia': 100,
        },
    'vidas': 0,
    'puntos': 0,
    'bala': ''
    }
'''

JUGADORES = {}
PR = False


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):
    pass


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while 1:
            try:
                datos = self.request.recv(512)
                if PR:
                    print "SERVER Recibe:", datos.split(TERMINATOR)
                respuesta = self.__procesar(datos, str(self.client_address[0]))
                if PR:
                    print "SERVER Envia:", respuesta.split(TERMINATOR)
                self.request.send(respuesta)
            except socket.error, err:
                print "Error en Server: ", err, self.client_address[0]
                self.request.close()
                # El HOST cierra: [Errno 104]
                #   Conexión reinicializada por la máquina remota
                # Client se desconecta: [Errno 32] Tubería rota
                return

    def __procesar(self, datos, ip):
        mensajes = datos.split(TERMINATOR)
        # FIXME: si mensaje es una lista vacía no hay clientes.
        for mensaje in mensajes:
            if mensaje.startswith('CONNECT*'):
                return self.__check_enemigos(ip)

            # Configuración del juego:
            elif mensaje.startswith('M*'):
                GAME['mapa'] = str(mensaje.split('M*')[-1].strip())
            elif mensaje.startswith('E*'):
                GAME['enemigos'] = int(mensaje.split('E*')[-1].strip())
            elif mensaje.startswith('V*'):
                GAME['vidas'] = int(mensaje.split('V*')[-1].strip())

            # Configuración de Jugador:
            elif mensaje.startswith('N*'):
                self.__add_nick(str(mensaje.split('N*')[-1].strip()), ip)
            elif mensaje.startswith('T*'):
                self.__add_tanque(str(mensaje.split('T*')[-1].strip()), ip)

            # Posición y Angulo de Tanque:
            elif mensaje.startswith('TP*'):
                self.__update_player(str(mensaje.split('TP*')[-1].strip()), ip)

            elif mensaje.startswith('BP*'):
                self.__update_bala(str(mensaje.split('BP*')[-1].strip()), ip)

            else:
                pass

        return self.__return_data()

    def __return_data(self):
        _buffer = ""
        for ip in JUGADORES.keys():
            _buffer = "%sPLAYER*%s||" % (_buffer, ip)
            _buffer = "%snick*%s||" % (_buffer, JUGADORES[ip]['nick'])

            path = JUGADORES[ip]['tanque']['path']
            a, x, y = JUGADORES[ip]['tanque']['pos']
            energia = JUGADORES[ip]['tanque']['energia']
            _buffer = "%stanque*%s %s %s %s %s||" % (
                _buffer, path, a, x, y, energia)

            _buffer = "%svidas*%s||" % (_buffer, JUGADORES[ip]['vidas'])
            _buffer = "%spuntos*%s||" % (_buffer, JUGADORES[ip]['puntos'])
            if JUGADORES[ip]['bala']:
                a, x, y = JUGADORES[ip]['bala']
                _buffer = "%sbala*%s %s %s||%s" % (
                    _buffer, a, x, y, TERMINATOR)
            else:
                #_buffer = "%s%s" % (_buffer, TERMINATOR)
                _buffer = "%sbala*||%s" % (_buffer, TERMINATOR)

        return _buffer

    def __check_enemigos(self, ip):
        ips = JUGADORES.keys()
        if ip in ips:
            # FIXME: vidas puede quitarse?
            return "CONNECT*%s %s%s" % (GAME['mapa'],
                GAME['vidas'], TERMINATOR)
        if len(ips) < GAME['enemigos']:
            return "CONNECT*%s %s%s" % (GAME['mapa'],
                GAME['vidas'], TERMINATOR)
        else:
            return "CLOSE*%s" % TERMINATOR

    def __add_nick(self, nick, ip):
        self.__check_jugador(ip)
        JUGADORES[ip]['nick'] = nick

    def __add_tanque(self, tanque, ip):
        self.__check_jugador(ip)
        JUGADORES[ip]['tanque']['path'] = tanque

    def __update_bala(self, mensaje, ip):
        self.__check_jugador(ip)
        if len(mensaje.split()) == 3:
            angulo, x, y = mensaje.split()
            JUGADORES[ip]['bala'] = (int(angulo), int(x), int(y))
        else:
            JUGADORES[ip]['bala'] = ''

    def __update_player(self, mensaje, ip):
        self.__check_jugador(ip)
        angulo, x, y = mensaje.split()
        JUGADORES[ip]['tanque']['pos'] = (int(angulo), int(x), int(y))

    def __check_jugador(self, ip):
        if not ip in JUGADORES.keys():
            JUGADORES[ip] = {
                'nick': '',
                'tanque': {
                    'path': '',
                    'pos': (0, 0, 0),
                    'energia': 100,
                    },
                'vidas': 0,
                'puntos': 0,
                'bala': ''}


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
    GAME['enemigos'] = 10
    GAME['vidas'] = 50

    if ret:
        import threading
        server = Server((ret, 5000), RequestHandler)
        server.allow_reuse_address = True
        server.socket.setblocking(0)
        server.serve_forever()

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()
