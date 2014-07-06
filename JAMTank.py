#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pygame

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

BASE = os.path.dirname(__file__)

from IntroWidget import IntroWidget
from GameWidget import GameWidget
from SelectServer import SelectServer

#GObject.threads_init()
#Gdk.threads_init()


class JAMTank(Gtk.Window):
    """
    Ventana Gtk principal del Juego.
    """

    __gtype_name__ = 'JAMTank'

    def __init__(self):

        Gtk.Window.__init__(self)

        self.set_title("JAMTank")
        self.modify_bg(0, Gdk.color_parse("#ffffff"))
        self.set_icon_from_file(os.path.join(BASE, "Iconos", "jamtank.svg"))

        self.set_resizable(True)
        self.set_size_request(640, 480)
        self.set_border_width(2)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Fase 1: Introduccion
        self.intro_widget = False
        # Fase 2: Elegir
        self.select_widget = False
        # Fase 3: Jugar Solo
        self.widget_game = False

        self.connect("delete-event", self.__salir)
        self.connect("realize", self.__do_realize)

        self.eventos = []
        self.show_all()

    def __reset(self):
        """
        Quita todos los widgets de la ventana y borra los eventos en la cola.
        """
        for child in self.get_children():
            self.remove(child)
            child.destroy()
        self.eventos = []

    def __do_realize(self, widget):
        """
        Cuando la ventana está realizada, carga los widgets de Introducción.
        """
        self.switch(False, 1, datos=False)

    def __solo_run(self, widget, datos):
        """
        El Usuario lanza juego (single o multiplayer).
        """
        self.__reset()
        self.widget_game = GameWidget()
        self.add(self.widget_game)
        GLib.idle_add(self.widget_game.setup_init, datos)

    def __update_events(self):
        self.widget_game.juego.update_events(self.eventos)

    def __salir(self, widget=None, event=None):
        if self.widget_game:
            if self.widget_game.juego:
                self.widget_game.juego.estado = False
                pygame.quit()
            if self.widget_game.client:
                self.widget_game.client.desconectarse()
        sys.exit(0)

    def __intro_switch(self, widget, valor):
        """
        Recibe opción de juego desde IntroWidget
        """

        if valor == "solo":
            self.switch(False, 2, datos=False)

        elif valor == "red":
            self.switch(False, 3, datos=False)

        elif valor == "join":
            self.switch(False, 4, datos=False)

        elif valor == "salir":
            self.__salir()

    def __server_select_accion(self, wiidget, accion, _dict):
        if accion == 'salir':
            self.switch(False, 1, datos=False)
        else:
            print accion, _dict

    def switch(self, widget, valor, datos=False):
        """
        Cambia los widgets en la ventana:
        """
        self.__reset()
        if valor == 1:
            # Introduccion, opciones de juego.
            self.intro_widget = IntroWidget()
            self.intro_widget.connect("switch", self.__intro_switch)
            self.add(self.intro_widget)
            GLib.idle_add(self.intro_widget.load, os.path.join(
                BASE, "Iconos", "jamtank.svg"))

        elif valor == 2:
            print "FIXME: Comenzar Guión del Juego"
            '''
            self.select_widget = SelectWidget(tipo='single')
            self.select_widget.connect("salir", self.switch, 1, False)
            self.select_widget.connect("run", self.__solo_run)
            self.add(self.select_widget)
            '''

        elif valor == 3:
            # Selección nick, mapa, tanque, oponentes y vidas.
            print "FIXME: Esta PC será Servidor"
            self.select_widget = SelectServer()
            self.add(self.select_widget)
            #GLib.idle_add(self.select_widget.load, os.path.join(
            #    BASE, "Iconos", "jamtank.svg"))
            self.select_widget.connect("accion", self.__server_select_accion)

        elif valor == 4:
            # Selección de nick, ip y tanque para unirse a partida multiplayer.
            print "FIXME: Esta PC será Cliente"
            '''
            self.select_widget = SelectWidget(tipo='join')
            self.select_widget.connect("salir", self.switch, 1, False)
            self.select_widget.connect("run", self.__run)
            self.add(self.select_widget)
            '''
        GLib.idle_add(self.queue_draw)
    '''
    def do_key_press_event(self, event):
        """
        Agrega eventos para mover el tanque o disparar.
        """

        if not self.widget_game:
            return

        nombre = Gdk.keyval_name(event.keyval)
        teclas = ["Up", "Down", "Right", "Left", "space"]
        if nombre in teclas and not nombre in self.eventos:

            if nombre == "Up" and "Down" in self.eventos:
                self.eventos.remove("Down")

            elif nombre == "Down" and "Up" in self.eventos:
                self.eventos.remove("Up")

            elif nombre == "Right" and "Left" in self.eventos:
                self.eventos.remove("Left")

            elif nombre == "Left" and "Right" in self.eventos:
                self.eventos.remove("Right")

            self.eventos.append(nombre)

        self.__update_events()
        return False

    def do_key_release_event(self, event):
        """
        Quita eventos de mover el tanque.
        """

        if not self.widget_game:
            return

        nombre = Gdk.keyval_name(event.keyval)
        teclas = ["Up", "Down", "Right", "Left", "space"]
        if nombre in teclas and nombre in self.eventos:
            self.eventos.remove(nombre)

        self.__update_events()
        return False
    '''

if __name__ == "__main__":
    JAMTank()
    Gtk.main()
