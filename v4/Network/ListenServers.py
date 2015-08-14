#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import socket
#import sys
import pickle
import threading
import ctypes


def terminate_thread(thread):
    """
    Termina un hilo python desde otro hilo.
    thread debe ser una instancia threading.Thread
    """
    if not thread.isAlive():
        return
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("No Existe el id de este hilo")
    elif res > 1:
        """
        si devuelve un número mayor que uno, estás en problemas, entonces
        llamas de nuevo con exc = NULL para revertir el efecto.
        """
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ListenServers(gobject.GObject):

    __gsignals__ = {
    "server": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        (gobject.TYPE_PYOBJECT, )),
    }

    def __init__(self):

        gobject.GObject.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 10000))
        self.listen_thread = False
        print "ListenServers Creado"

    def __handler_listen(self):
        print "ListenServers > Buscando Juegos en la Red..."
        while self.listen_thread:
            mensaje, remote = self.socket.recvfrom(10000)
            data = pickle.loads(mensaje)
            #print >>sys.stderr, remote, 'Recibido: "%s"' % data
            self.emit("server", data)

    def new_handler_listen(self, reset):
        print "Activar ListenServers:", reset
        if self.listen_thread:
            terminate_thread(self.listen_thread)
            del(self.listen_thread)
            self.listen_thread = False
        if reset:
            self.listen_thread = threading.Thread(
                target=self.__handler_listen, args=[])
            self.listen_thread.start()
