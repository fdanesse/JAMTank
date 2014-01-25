#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
#   Flavio Danesse <fdanesse@gmail.com>


import SocketServer

TERMINATOR = "\r\n\r\n"

GAME = {
    'mapa': "",
    'enemigos': 1,
    'vidas': 10,
    }

JUGADORES = {
    #ids: {         # id = self.client_address[0]
    #   'nick': '',
    #   'tanque': {
    #       'path': '',
    #       'pos': (angulo,x,y),
    #   'energia': 100,
    #   'vidas': 10,
    #   'balas': [(x,y), ...]
    #   }
    }


class Server(SocketServer.ThreadingMixIn,
    SocketServer.ThreadingTCPServer):

    pass


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        """
        Acepta la conexión de un jugador
        """

        datos = self.request.recv(200)
        self.__procesar(datos)
        self.request.send(datos)

    def __procesar(self, datos):

        mensages = datos.split(TERMINATOR)

        # Configuración del Juego
        for mensaje in mensages:
            if mensaje.startswith('M*'):
                GAME['mapa'] = mensaje.split('M*')[-1].strip()

            elif mensaje.startswith('E*'):
                GAME['enemigos'] = int(mensaje.split('E*')[-1].strip())

            elif mensaje.startswith('V*'):
                GAME['vidas'] = int(mensaje.split('V*')[-1].strip())

        print self.client_address[0], GAME


if __name__ == "__main__":

    server = Server(("192.168.1.9", 5000), RequestHandler)
    server.allow_reuse_address = True
    server.socket.setblocking(0)
    server.serve_forever()
    '''
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    '''
