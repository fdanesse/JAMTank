#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
import socket
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

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('', 10000))
        self._listen_thread = False
        self._estado = False
        print "ListenServers Creado"

    def __handler_listen(self):
        print "ListenServers > Buscando Juegos en la Red..."
        while self._estado:
            mensaje, remote = self._socket.recvfrom(10000)
            data = pickle.loads(mensaje)
            #print >>sys.stderr, remote, 'Recibido: "%s"' % data
            self.emit("server", data)

    def new_handler_listen(self, reset):
        print "Activar ListenServers:", reset
        if self._estado:
            self._estado = False
        if self._listen_thread:
            terminate_thread(self._listen_thread)
            del(self._listen_thread)
            self._listen_thread = False
        if reset:
            self._estado = True
            self._listen_thread = threading.Thread(
                target=self.__handler_listen, args=[])
            self._listen_thread.start()
        else:
            self._socket.close()
