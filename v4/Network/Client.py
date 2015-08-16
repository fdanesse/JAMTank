#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Errores: https://docs.python.org/2/library/errno.html

import socket
import time
import gobject
import ast

T = "\n"


class Client(gobject.GObject):

    __gsignals__ = {
    "error": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_STRING,))}

    def __init__(self, ip):

        gobject.GObject.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dir = (ip, 5000)
        self.rfile = False

    def conectarse(self):
        try:
            self.socket.connect(self.dir)
            #self.socket.setblocking(0)
            self.rfile = self.socket.makefile("rwb") #, bufsize=1024
            self.rfile.flush()
            time.sleep(0.5)
            return True
        except socket.error, err:
            # FIXME: socket.error: [Errno 111] Conexión rehusada
            self.emit("error", "Cliente Conectarse: %s" % err)
            return False

    def desconectarse(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.rfile.close()
            time.sleep(0.5)
        except:
            pass

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
                self.emit("error", "Cliente Enviar: %s" % err)
                break
            time.sleep(0.02)

    def recibir(self, ret):
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
                ret = entrada
            except socket.error, err:
                # [Errno 11] Recurso no disponible temporalmente
                # Desconexion: [Errno 104] Conexión reinicializada por la máquina remota
                if err[0] == 11:
                    print "FIXME: break recibir en cliente"
                else:
                    self.emit("error", "Cliente Recibir: %s" % err)
                break
                time.sleep(0.02)
        return ret
