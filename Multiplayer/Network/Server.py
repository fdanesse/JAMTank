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
        'pos': (0, 0, 0),
        'energia': 100,
        },
    'vidas': 0,
    'puntos': 0,
    'bala': ''
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
                #OCUPADO = False

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
            #OCUPADO = True

            if datos[0] == "Config":
            # Host Configurando el juego y sus datos como cliente
                GAME['mapa'] = datos[1]
                GAME['enemigos'] = int(datos[2])
                GAME['vidas'] = int(datos[3])
                JUGADORES[ip] = dict(MODEL)
                JUGADORES[ip]['tanque']['path'] = datos[4]
                JUGADORES[ip]['nick'] = datos[5]
                return "OK"

            else:
                #self.__update_player(str(mensaje.split('TP*')[-1].strip()), ip)
                pass

            return self.__return_data()
        else:
            return False

    #def __add(self, tanque, nick, ip):
    #    if not ip in JUGADORES.keys():
    #        JUGADORES[ip] = dict(MODEL)
    #    JUGADORES[ip]['tanque']['path'] = tanque
    #    JUGADORES[ip]['nick'] = nick

    #def __check_enemigos(self, ip):
    #    ips = JUGADORES.keys()
    #    #if ip in ips:
    #    #    return "Config,%s" % GAME['mapa']
    #    if len(ips) < GAME['enemigos']:
    #        return "Config,%s" % GAME['mapa']
    #    else:
    #        return "CLOSE,"
    '''
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
                _buffer = "%sbala*||%s" % (_buffer, TERMINATOR)

        return _buffer
    '''
    '''
    def __update_player(self, mensaje, ip):
        self.__check_jugador(ip)
        try:
            angulo, x, y = mensaje.split()
            JUGADORES[ip]['tanque']['pos'] = (int(angulo), int(x), int(y))
        except:
            print "ERROR:", self.__update_player
    '''
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
