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
        """
        Acepta la conexión de un jugador
        """

        datos = self.request.recv(200)
        respuesta = self.__procesar(datos)
        self.request.send(respuesta)

    def __registrar_server(self, datos):
        """
        Registra datos del juego:
            mapa
            enemigos
            vidas
        """

        mensajes = datos.split(TERMINATOR)
        print mensajes
        for mensaje in mensajes:
            if mensaje.startswith('M*'):
                GAME['mapa'] = mensaje.split('M*')[-1].strip()

            elif mensaje.startswith('E*'):
                GAME['enemigos'] = int(mensaje.split('E*')[-1].strip())

            elif mensaje.startswith('V*'):
                GAME['vidas'] = int(mensaje.split('V*')[-1].strip())

    def __registrar_jugador(self, datos):
        """
        Registra un nuevo jugador en el juego, enviandole
        el mapa del juego.
        """

        direccion = self.client_address[0]

        if not direccion in JUGADORES.keys():
            JUGADORES[direccion] = MODEL.copy()

        mensajes = datos.split(TERMINATOR)

        for mensaje in mensajes:
            if mensaje.startswith('N*'):
                JUGADORES[direccion]['nick'] = mensaje.split('N*')[-1].strip()

    def __procesar(self, datos):
        """
        Procesa los datos enviados por un cliente.
        """

        if datos.startswith('HOST'):
            self.__registrar_server(
                datos.replace('HOST', ''))
            return TERMINATOR

        elif datos.startswith('REGISTRO'):
            self.__registrar_jugador(
                datos.replace('HOST', ''))
            return GAME['mapa']

        else:
            print datos
            return ""
        '''
        # FIXME: Respetar límite de jugadores.
        direccion = self.client_address[0]

        if not direccion in JUGADORES.keys():
            JUGADORES[direccion] = MODEL.copy()

        mensajes = datos.split(TERMINATOR)

        for mensaje in mensajes:
            # Registro de jugador:
            if mensaje.startswith('N*'):
                JUGADORES[direccion]['nick'] = mensaje.split('N*')[-1].strip()

            elif mensaje.startswith('T*'):
                JUGADORES[direccion]['tanque']['pos'] = mensaje.split('T*')[-1].strip()

            else:
                print mensaje
        '''


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
