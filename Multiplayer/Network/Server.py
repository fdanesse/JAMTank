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
        if not self.server.GAME['estado']:
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
                self.server.GAME['estado'] = False
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
        self.server.JUGADORES[ip]['tanque']['pos'] = "%s,%s,%s" % (a, x, y)
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
        self.server.JUGADORES[ip]['tanque']['pos'] = "-,-,-"
        self.server.JUGADORES[ip]['bala'] = "-,-,-"

    def __connect_client(self, ip, datos):
        """
        Nuevo Jugador desea conectarse.
        """
        ips = self.server.JUGADORES.keys()
        if not ip in self.server.JUGADORES.keys():
            if len(ips) < self.server.GAME['enemigos']:
                self.server.JUGADORES[ip] = get_model()
                self.server.JUGADORES[ip]['tanque']['path'] = datos[1].strip()
                self.server.JUGADORES[ip]['nick'] = datos[2].strip()
                retorno = "%s" % str(self.server.GAME['mapa'].strip())
                if MAKELOG:
                    APPEND_LOG({"JOIN %s" % ip: dict(self.server.JUGADORES)})
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
            self.server.JUGADORES[ip]['tanque']['path'] = datos[1].strip()
            self.server.JUGADORES[ip]['nick'] = datos[2].strip()
            retorno = "%s" % str(self.server.GAME['mapa'].strip())
            return retorno

    def __config_server(self, ip, datos):
        """
        Host Configurando el juego y sus datos como cliente.
        """
        self.server.GAME['mapa'] = datos[1].strip()
        self.server.GAME['enemigos'] = int(datos[2].strip())
        self.server.GAME['vidas'] = int(datos[3].strip())
        self.server.JUGADORES[ip] = get_model()
        self.server.JUGADORES[ip]['tanque']['path'] = datos[4].strip()
        self.server.JUGADORES[ip]['nick'] = datos[5].strip()
        if MAKELOG:
            APPEND_LOG({"Configuracion Juego": dict(self.server.GAME)})
            APPEND_LOG({
                "Configuracion Jugadores": dict(self.server.JUGADORES)})

    def __get_data(self):
        retorno = ""
        for ip in self.server.JUGADORES.keys():
            nick = self.server.JUGADORES[ip]['nick']
            tanque = self.server.JUGADORES[ip]['tanque']['path']
            #datos = "%s,%s,%s,%s,%s" % (ip, nick, tanque,
            #    JUGADORES[ip]['tanque']['pos'], JUGADORES[ip]['bala'])
            datos = "%s,%s,%s,%s" % (ip, nick, tanque,
                self.server.JUGADORES[ip]['tanque']['pos'])
            retorno = "%s%s||" % (retorno, datos)
        return retorno.strip()


class Server(SocketServer.ThreadingMixIn, SocketServer.ThreadingTCPServer):

    def __init__(self, logger=None, host='localhost',
        port=5000, handler=RequestHandler):

        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.allow_reuse_address = True
        self.socket.setblocking(0)

        self.GAME = {
            'mapa': "",
            'enemigos': 0,
            'vidas': 0,
            'estado': True,
            }

        self.JUGADORES = {}

        print "Server ON . . ."

    def shutdown(self):
        print "Server OFF"
        SocketServer.ThreadingTCPServer.shutdown(self)


if __name__ == "__main__":
    ip = ''
    import commands
    text = commands.getoutput('ifconfig wlan0').splitlines()
    datos = ''
    for linea in text:
        if 'Direc. inet:' in linea and 'Difus.:' in linea and 'Másc:' in linea:
            datos = linea
            break
    ip = 'localhost'
    if datos:
        ip = datos.split('Direc. inet:')[1].split('Difus.:')[0].strip()

    if ip:
        server = Server(host=ip, port=5000, handler=RequestHandler)
        server.GAME['mapa'] = "fondo1.png"
        server.GAME['enemigos'] = 10
        server.GAME['vidas'] = 50
        server.serve_forever()
