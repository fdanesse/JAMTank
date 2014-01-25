#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Client.py por:
#   Flavio Danesse <fdanesse@gmail.com>

import socket

from gi.repository import GObject

GObject.threads_init()

TERMINATOR = "\r\n\r\n"


class Client(GObject.Object):

    def __init__(self, ip):

        GObject.Object.__init__(self)

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

        self.dir = (ip, 5000)

    def conectarse(self):

        self.socket.connect(self.dir)
        self.socket.setblocking(0)

    def desconectarse(self):
        print "Cerrando el socket"
        self.socket.close()

    def enviar(self, datos):
        """
        Envia datos al Servidor.
        """

        self.socket.send(datos)

    def recibir(self):
        """
        Recibe los datos del server (incluyendo los propios)
        """

        entrada = ""
        mensajes = []

        while not entrada:
            try:
                entrada = self.socket.recv(200)
                mensajes = entrada.split(TERMINATOR)

            except socket.error, e:
                pass

        return mensajes


if __name__ == "__main__":

    client = Client('192.168.1.9')
    client.enviar("A" * 200)
    client.recibir()
