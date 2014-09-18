#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Client.py por:
#   Flavio Danesse <fdanesse@gmail.com>

import socket
import time
from gi.repository import GObject

#GObject.threads_init()


class Client(GObject.Object):

    def __init__(self, ip):

        GObject.Object.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dir = (ip, 5000)

    def conectarse(self):
        self.socket.connect(self.dir)
        self.socket.setblocking(0)
        time.sleep(0.5)

    def desconectarse(self):
        self.socket.close()
        time.sleep(0.5)

    def enviar(self, datos):
        self.socket.send(datos)
        time.sleep(0.02)

    def recibir(self):
        entrada = ""
        #while not entrada:
        try:
            entrada = self.socket.recv(256)
        except socket.error, err:
            print "ERROR CLIENT recibir", err
        return entrada


#if __name__ == "__main__":
#    client = Client('192.168.1.9')
#    client.enviar("A" * 200)
#    client.recibir()
