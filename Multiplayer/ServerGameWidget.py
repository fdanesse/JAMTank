#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading
import json
import codecs

from gi.repository import Gtk
from gi.repository import GdkX11
from gi.repository import GObject
from gi.repository import GLib

from Network.Server import Server
from Network.Server import RequestHandler
from Network.Client import Client
from Juego import Juego

MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")
if os.path.exists(LOGPATH):
    os.remove(LOGPATH)


def WRITE_LOG(_dict):
    archivo = open(LOGPATH, "w")
    archivo.write(json.dumps(
        _dict, indent=4, separators=(", ", ":"), sort_keys=True))
    archivo.close()


def APPEND_LOG(_dict):
    archivo = codecs.open(LOGPATH, "r", "utf-8")
    new = json.JSONDecoder("utf-8").decode(archivo.read())
    archivo.close()
    for key in _dict.keys():
        new[key] = _dict[key]
    WRITE_LOG(new)


def terminate_thread(thread):
    """
    Termina un hilo python desde otro hilo.
    thread debe ser una instancia threading.Thread
    """

    if not thread.isAlive():
        return

    import ctypes
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


class GameWidget(Gtk.DrawingArea):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.server_thread = False
        self.client = False
        self.server = False
        self.juego = False

        self.show_all()

    def __run_client(self, _dict):
        """
        El Cliente Host, se encarga de configurar el Server con:
            mapa, vidas, enemigos,
                tanque y nick (propios)
        """
        server = str(_dict['server'])
        mapa = os.path.basename(str(_dict['mapa']))
        tanque = os.path.basename(str(_dict['tanque']))
        enemigos = str(_dict['enemigos'])
        vidas = str(_dict['vidas'])
        nick = str(_dict['nick'])

        self.client = Client(server)
        connected = self.client.conectarse()

        if connected:
            _buffer = "Config,%s,%s,%s,%s,%s" % (mapa, enemigos,
                vidas, tanque, nick)

            self.client.enviar(_buffer)
            retorno = self.client.recibir()

            if retorno == "OK":
                tanque = str(_dict['tanque'])
                mapa = str(_dict['mapa'])

                new_dict = {
                    'tanque': tanque,
                    'nick': nick,
                    'mapa': mapa,
                    }

                if MAKELOG:
                    APPEND_LOG({'client': new_dict})
                time.sleep(0.5)
                self.__run_game(new_dict)
            else:
                dialog = Dialogo(parent=self.get_toplevel(),
                    text="Algo salió mal al Configurar el Servidor.")
                dialog.run()
                self.salir()
        else:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Cliente no pudo Conectarse con el Servidor.")
            dialog.run()
            self.salir()

    def __run_game(self, _dict):
        """
        Comienza a correr el Juego.
        """
        try:
            xid = self.get_property('window').get_xid()
            os.putenv('SDL_WINDOWID', str(xid))
            self.juego = Juego(dict(_dict), self.client)
            self.juego.config()
            time.sleep(0.5)
            self.juego.run()
        except:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Juego no pudo Iniciar.")
            dialog.run()
            self.salir()

    def setup_init(self, _dict):
        """
        Comienza a correr el Server.
        """
        try:
            self.server = Server((str(_dict['server']), 5000), RequestHandler)
            self.server.allow_reuse_address = True
            self.server.socket.setblocking(0)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.setDaemon(True)
            self.server_thread.start()
            time.sleep(0.5)
            if MAKELOG:
                WRITE_LOG({'server': _dict})
            self.__run_client(dict(_dict))
        except:
            dialog = Dialogo(parent=self.get_toplevel(),
                text="EL Servidor no pudo Iniciar.")
            dialog.run()
            self.salir()
        return False

    def do_draw(self, context):
        """
        Reescalado en gtk, reescala en pygame.
        """
        rect = self.get_allocation()
        if self.juego:
            self.juego.escalar((rect.width, rect.height))

    def update_events(self, eventos):
        """
        Eventos gtk, se pasan a pygame
        """
        if "Escape" in eventos:
            self.salir()
        else:
            if self.juego:
                self.juego.update_events(eventos)
        if "space" in eventos:
            eventos.remove("space")

    def salir(self):
        if self.juego:
            self.juego.salir("END,")
            del(self.juego)
            self.juego = False
        if self.client:
            self.client.desconectarse()
            del(self.client)
            self.client = False
        if self.server:
            self.server.shutdown()
            self.server.socket.close()
            del(self.server)
            self.server = False
        if self.server_thread:
            terminate_thread(self.server_thread)
            del(self.server_thread)
            self.server_thread = False
        self.emit('salir')


class Dialogo(Gtk.Dialog):

    def __init__(self, parent=None, text=""):

        Gtk.Dialog.__init__(self,
            parent=parent,
            flags=Gtk.DialogFlags.MODAL)

        #self.set_decorated(False)
        #self.modify_bg(0, get_colors("window"))
        self.set_border_width(15)

        label = Gtk.Label(text)
        label.show()

        self.vbox.pack_start(label, True, True, 5)

        self.connect("realize", self.__do_realize)

    def __do_realize(self, widget):
        GLib.timeout_add(2000, self.__destroy)

    def __destroy(self):
        self.destroy()
        return False
