#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
#   Flavio Danesse <fdanesse@gmail.com>


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
        #'path': '',
        'pos': (0, 0, 0),
        'energia': 100,
        },
    'vidas': 0,
    'balas': [0],
    'puntos': 0,
    }

JUGADORES = {}


class Server(SocketServer.ThreadingMixIn,
    SocketServer.ThreadingTCPServer):
    pass


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        datos = self.request.recv(200)
        respuesta = self.__procesar(datos)
        self.request.send(respuesta)

    def __procesar(self, datos):
        mensajes = datos.split(TERMINATOR)
        retorno = "OK*"

        for mensaje in mensajes:
            if mensaje.startswith('CONNECT*'):
                return self.__check_enemigos()

            elif mensaje.startswith('M*'):
                GAME['mapa'] = mensaje.split('M*')[-1].strip()
                #return "OK*%s" % TERMINATOR

            elif mensaje.startswith('E*'):
                GAME['enemigos'] = int(mensaje.split('E*')[-1].strip())
                #return "OK*%s" % TERMINATOR

            elif mensaje.startswith('V*'):
                GAME['vidas'] = int(mensaje.split('V*')[-1].strip())
                #return "OK*%s" % TERMINATOR

            elif mensaje.startswith('N*'):
                self.__add_nick(mensaje.strip())

            elif mensaje.startswith('T*'):
                self.__add_tanque(mensaje.strip())

            else:
                pass

        return "%s%s%s%s" % (GAME, TERMINATOR, JUGADORES, TERMINATOR)  #retorno

    def __check_enemigos(self):
        if len(JUGADORES.keys()) < GAME['enemigos']:
            return "CONNECT*%s" % TERMINATOR
        else:
            return "CLOSE*%s" % TERMINATOR

    def __add_nick(self, nick):
        self.__check_jugador()
        JUGADORES[self.client_address[0]]['nick'] = nick

    def __add_tanque(self, tanque):
        self.__check_jugador()
        JUGADORES[self.client_address[0]]['tanque'] = tanque

    def __check_jugador(self):
        if not self.client_address[0] in JUGADORES.keys():
            JUGADORES[self.client_address[0]] = MODEL.copy()

#if __name__ == "__main__":
#    server = Server(("192.168.1.9", 5000), RequestHandler)
#    server.allow_reuse_address = True
#    server.socket.setblocking(0)
#    server.serve_forever()
#    '''
#    server_thread = threading.Thread(target=server.serve_forever)
#    server_thread.setDaemon(True)
#    server_thread.start()
#    '''
