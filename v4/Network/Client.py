#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import gobject
import ast

T = "\n"


class Client(gobject.GObject):

    def __init__(self, ip):

        gobject.GObject.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dir = (ip, 5000)
        self.rfile = False

    def conectarse(self):
        try:
            self.socket.connect(self.dir)
            self.socket.setblocking(0)
            self.rfile = self.socket.makefile("rwb") #, bufsize=1024
            self.rfile.flush()
            time.sleep(0.5)
            return True
        except socket.error, err:
            # FIXME: socket.error: [Errno 111] Conexión rehusada
            print "Error en el cliente:", err
            return False

    def desconectarse(self):
        self.socket.close()
        self.rfile.close()
        time.sleep(0.5)

    def enviar(self, message):
        """
        Escribe un diccionario convertido a str y con la terminacion "\n"
        """
        enviado = False
        while not enviado:
            try:
                self.rfile.write("%s%s" % (message, T))
                self.rfile.flush()
                enviado = True
            except socket.error, err:
                print "Error del cliente al enviar datos:", err
            time.sleep(0.02)

    def recibir(self):
        """
        Espera una linea string que termina con "\n" y que ast puede convertir
        en un diccionario python.
        """
        entrada = {}
        while not entrada:
            try:
                entrada = self.rfile.readline()
                entrada = ast.literal_eval(entrada)
                self.rfile.flush()
            except socket.error, err:
                print "Error del cliente al recibir datos:", err
                # [Errno 11] Recurso no disponible temporalmente
                time.sleep(0.02)
        return entrada
