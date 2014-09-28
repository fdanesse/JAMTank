#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Server.py por:
#   Flavio Danesse <fdanesse@gmail.com>

import os
import socket
import SocketServer
import time
import json
import codecs


MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_server.log")
if os.path.exists(LOGPATH):
    os.remove(LOGPATH)


def WRITE_LOG(_dict):
    archivo = open(LOGPATH, "w")
    archivo.write(json.dumps(
        _dict, indent=4, separators=(", ", ":"), sort_keys=True))
    archivo.close()


def APPEND_LOG(_dict):
    new = {}
    if os.path.exists(LOGPATH):
        archivo = codecs.open(LOGPATH, "r", "utf-8")
        new = json.JSONDecoder("utf-8").decode(archivo.read())
        archivo.close()
    for key in _dict.keys():
        new[key] = _dict[key]
    WRITE_LOG(new)


def get_model():
    return {
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


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):

    global GAME
    global JUGADORES

    GAME = {
        'mapa': "",
        'enemigos': 0,
        'vidas': 0,
        'estado': True,
        }

    JUGADORES = {}


class RequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        while 1:
            try:
                entrada = self.rfile.readline().strip()
                if not entrada:
                    self.request.close()
                    return

                respuesta = self.__procesar(entrada,
                    str(self.client_address[0]))

                if respuesta:
                    while len(respuesta) < 512:
                        respuesta = "%s*" % respuesta
                    self.wfile.write(respuesta)
                else:
                    if MAKELOG:
                        key = 'server %s' % time.time()
                        ip = self.client_address[0]
                        valor = "Cierre de Conexion: %s" % ip
                        APPEND_LOG({key: valor})
                    self.request.close()
                    #return

            except socket.error, err:
                if MAKELOG:
                    key = "Error: %s" % time.time()
                    APPEND_LOG({key: (str(err), self.client_address[0])})
                self.request.close()

    def __procesar(self, entrada, ip):
        if not GAME['estado']:
            return "END"
        datos = entrada.split(",")
        if datos:
            if datos[0] == "UPDATE":
                self.__actualizar_jugador(ip, datos)
                return self.__get_data()

            elif datos[0] == "REMOVE":
                self.__remover_jugador(ip, datos)
                return "REMOVIDO"

            elif datos[0] == "END":
                self.__remover_jugador(ip, datos)
                # FIXME: Todos los clientes deben desconectarse
                GAME['estado'] = False
                return "END"

            elif datos[0] == "Config":
                self.__config_server(ip, datos)
                return "OK"

            elif datos[0] == "JOIN":
                return self.__connect_client(ip, datos)

            else:
                if MAKELOG:
                    key = "Mensaje no considerado %s" % time.time()
                    APPEND_LOG({key: datos})
                return "*" * 512

        else:
            return ""

    def __actualizar_jugador(self, ip, datos):
        """
        Jugador actualizando sus datos.
        """
        a, x, y = datos[1:4]
        JUGADORES[ip]['tanque']['pos'] = "%s,%s,%s" % (a, x, y)
        #if len(datos) > 4:
        #    aa, xx, yy = datos[4:]
        #    JUGADORES[ip]['bala'] = "%s,%s,%s" % (aa, xx, yy)

    def __remover_jugador(self, ip, datos):
        """
        Jugador Abandonando el Juego.
        """
        if MAKELOG:
            key = "Jugador Removido %s" % time.time()
            APPEND_LOG({key: ip})
        #del(JUGADORES[ip])
        JUGADORES[ip]['tanque']['pos'] = "-,-,-"
        JUGADORES[ip]['bala'] = "-,-,-"

    def __connect_client(self, ip, datos):
        """
        Nuevo Jugador desea conectarse.
        """
        ips = JUGADORES.keys()
        if not ip in JUGADORES.keys():
            if len(ips) < GAME['enemigos']:
                JUGADORES[ip] = get_model()
                JUGADORES[ip]['tanque']['path'] = datos[1].strip()
                JUGADORES[ip]['nick'] = datos[2].strip()
                retorno = "%s" % str(GAME['mapa'].strip())
                if MAKELOG:
                    APPEND_LOG({"JOIN %s" % ip: dict(JUGADORES)})
                return retorno
            else:
                if MAKELOG:
                    key = "Jugador Rechazado %s" % time.time()
                    APPEND_LOG({key: ip})
                return "CLOSE"
        else:
            if MAKELOG:
                key = "El Jugador ya estaba en game %s" % time.time()
                APPEND_LOG({key: ip})
            JUGADORES[ip]['tanque']['path'] = datos[1].strip()
            JUGADORES[ip]['nick'] = datos[2].strip()
            retorno = "%s" % str(GAME['mapa'].strip())
            return retorno

    def __config_server(self, ip, datos):
        """
        Host Configurando el juego y sus datos como cliente.
        """
        GAME['mapa'] = datos[1].strip()
        GAME['enemigos'] = int(datos[2].strip())
        GAME['vidas'] = int(datos[3].strip())
        JUGADORES[ip] = get_model()
        JUGADORES[ip]['tanque']['path'] = datos[4].strip()
        JUGADORES[ip]['nick'] = datos[5].strip()
        if MAKELOG:
            APPEND_LOG({"Configuracion Juego": dict(GAME)})
            APPEND_LOG({"Configuracion Jugadores": dict(JUGADORES)})

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
