#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
#   Flavio Danesse <fdanesse@gmail.com>

import os
import socket
import SocketServer


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):

    global GAME
    global MODEL
    global JUGADORES
    global LOG

    path = os.path.join(os.environ["HOME"], "server.log")
    if os.path.exists(path):
        os.remove(path)
    LOG = open(path, "w")

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

    JUGADORES = {}


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while 1:
            try:
                entrada = self.rfile.readline().strip()
                #LOG.write("Recibo: %s\n" % entrada)
                if not entrada:
                    self.request.close()
                    return

                respuesta = self.__procesar(entrada,
                    str(self.client_address[0]))
                if respuesta:
                    #LOG.write("Envio: %s\n" % respuesta)
                    while len(respuesta) < 512:
                        respuesta = "%s*" % respuesta
                    self.wfile.write(respuesta)
                else:
                    LOG.write("Cierre de Conexion: %s\n" % self.client_address[0])
                    self.request.close()
                    #return

            except socket.error, err:
                LOG.write("Error: %s %s\n" % (err, self.client_address[0]))
                self.request.close()
                # El HOST cierra: [Errno 104]
                #   Conexión reinicializada por la máquina remota
                # Client se desconecta: [Errno 32] Tubería rota
                #return

    def __procesar(self, entrada, ip):
        datos = entrada.split(",")
        if datos:
            if datos[0] == "Config":
                # Host Configurando el juego y sus datos como cliente
                GAME['mapa'] = datos[1].strip()
                GAME['enemigos'] = int(datos[2].strip())
                GAME['vidas'] = int(datos[3].strip())
                JUGADORES[ip] = dict(MODEL)
                JUGADORES[ip]['tanque']['path'] = datos[4].strip()
                JUGADORES[ip]['nick'] = datos[5].strip()
                return "OK"

            elif datos[0] == "UPDATE":
                # Jugador actualizando sus datos
                a, x, y = datos[1:4]
                JUGADORES[ip]['tanque']['pos'] = "%s,%s,%s" % (a, x, y)
                #if len(datos) > 4:
                #    aa, xx, yy = datos[4:]
                #    JUGADORES[ip]['bala'] = "%s,%s,%s" % (aa, xx, yy)
                return self.__get_data()

            elif datos[0] == "JOIN":
                # Nuevo Jugador desea conectarse.
                ips = JUGADORES.keys()
                if not ip in JUGADORES.keys():
                    if len(ips) < GAME['enemigos']:
                        JUGADORES[ip] = dict(MODEL)
                        JUGADORES[ip]['tanque']['path'] = datos[1].strip()
                        JUGADORES[ip]['nick'] = datos[2].strip()
                        retorno = "%s" % str(GAME['mapa'].strip())
                        return retorno
                    else:
                        return "CLOSE"
                else:
                    print "El Jugador ya estaba en game", ip
                    retorno = "%s" % str(GAME['mapa'].strip())
                    return retorno

            else:
                LOG.write("Mensaje no considerado en el server: %s\n" % datos)
                return "*" * 512

        else:
            return ""

    def __get_data(self):
        retorno = ""
        for ip in JUGADORES.keys():
            nick = JUGADORES[ip]['nick']
            tanque = JUGADORES[ip]['tanque']['path']
            #datos = "%s,%s,%s,%s,%s" % (ip, nick, tanque,
            #    JUGADORES[ip]['tanque']['pos'], JUGADORES[ip]['bala'])
            datos = "%s,%s,%s,%s" % (ip, nick, tanque,
                JUGADORES[ip]['tanque']['pos'])
            retorno = "%s%s||" % (retorno, datos)
        return retorno.strip()


if __name__ == "__main__":
    ret = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 80))
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
