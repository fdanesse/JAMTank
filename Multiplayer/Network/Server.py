#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
#   Flavio Danesse <fdanesse@gmail.com>

import socket
import SocketServer

GAME = {
    'mapa': "",
    'enemigos': 0,
    'vidas': 0,
    }

MODEL = {
    'nick': '',
    'tanque': {
        'path': '',
        'pos': '0,0,0',
        'energia': 100,
        },
    'vidas': 0,
    'puntos': 0,
    'bala': '-,-,-'
    }

OCUPADO = False
JUGADORES = {}
PR = True


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):
    pass


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while 1:
            try:
                entrada = self.request.recv(256)
                if not entrada:
                    self.request.close()
                    return

                if PR:
                    print "SERVER Recibe:", entrada

                respuesta = self.__procesar(entrada,
                    str(self.client_address[0]))
                if not respuesta:
                    self.request.close()
                    return

                if PR:
                    print "SERVER Envia:", respuesta

                self.request.send(respuesta)

            except socket.error, err:
                print "Error en Server: ", err, self.client_address[0]
                self.request.close()
                # El HOST cierra: [Errno 104]
                #   Conexión reinicializada por la máquina remota
                # Client se desconecta: [Errno 32] Tubería rota
                return

    def __procesar(self, entrada, ip):
        datos = entrada.split(",")
        if datos:
            if datos[0] == "Config":
                # Host Configurando el juego y sus datos como cliente
                GAME['mapa'] = datos[1]
                GAME['enemigos'] = int(datos[2])
                GAME['vidas'] = int(datos[3])
                JUGADORES[ip] = dict(MODEL)
                JUGADORES[ip]['tanque']['path'] = datos[4]
                JUGADORES[ip]['nick'] = datos[5]
                return "OK"

            elif datos[0] == "UPDATE":
                # Jugador actualizando sus datos
                a, x, y = datos[1:4]
                JUGADORES[ip]['tanque']['pos'] = "%s,%s,%s" % (a, x, y)
                if len(datos) > 4:
                    aa, xx, yy = datos[4:]
                    JUGADORES[ip]['bala'] = "%s,%s,%s" % (aa, xx, yy)

                return self.__get_data()

            elif datos[0] == "JOIN":
                # Nuevo Jugador desea conectarse.
                ips = JUGADORES.keys()
                if not ip in JUGADORES.keys():
                    if len(ips) < GAME['enemigos']:
                        JUGADORES[ip] = dict(MODEL)
                        JUGADORES[ip]['tanque']['path'] = datos[1]
                        JUGADORES[ip]['nick'] = datos[2]
                        return "%s" % str(GAME['mapa'])
                    else:
                        return "CLOSE"
                else:
                    print "El Jugador ya estaba en game", ip

            else:
                print "Mensaje no considerado en el server"

        else:
            return False

    def __get_data(self):
        retorno = ""
        for ip in JUGADORES.keys():
            nick = JUGADORES[ip]['nick']
            tanque = JUGADORES[ip]['tanque']['path']
            datos = "%s,%s,%s,%s,%s" % (ip, nick, tanque,
                JUGADORES[ip]['tanque']['pos'], JUGADORES[ip]['bala'])
            retorno = "%s%s||" % (retorno, datos)
        return retorno.strip()


'''
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
'''
