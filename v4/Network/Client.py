#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import gobject


class Client(gobject.GObject):

    def __init__(self, ip):

        gobject.GObject.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dir = (ip, 5000)

    def conectarse(self):
        try:
            self.socket.connect(self.dir)
            self.socket.setblocking(0)
            time.sleep(0.5)
            return True
        except socket.error, err:
            # FIXME: socket.error: [Errno 111] Conexión rehusada
            print "Error en el cliente:", err
            return False

    def desconectarse(self):
        self.socket.close()
        time.sleep(0.5)

    def enviar(self, datos):
        enviado = False
        while not enviado:
            try:
                self.socket.sendall(datos)
                enviado = True
            except socket.error, err:
                print "Error del cliente al enviar datos:", err
            time.sleep(0.02)

    def recibir(self):
        entrada = ""
        while not entrada:
            try:
                entrada = self.socket.recv(1024)
            except socket.error, err:
                print "Error del cliente al recibir datos:", err
                time.sleep(0.02)
        return entrada
