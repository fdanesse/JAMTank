#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

BASE = os.path.dirname(__file__)

from IntroWidget import IntroWidget
from GameWidget import GameWidget
from SelectWidget import SelectWidget

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

        self.set_icon_from_file(
            os.path.join(BASE,
            "Iconos", "jamtank.svg"))

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
        Quita todos los widgets de la ventana.
        borra los eventos en la cola.
        """

        for child in self.get_children():
            self.remove(child)
            child.destroy()

        self.eventos = []

    def __do_realize(self, widget):
        """
        Cuando la ventana está realizada,
        se cargan los widgets de Introducción.
        """

        self.switch(1)

    def switch(self, valor, datos=False):
        """
        Cambia los widgets en la ventana:
            1: Introducción
            2: Selecciones para jugar solo
            3: Jugar Solo
            4: Selecciones para jugar en red
            4: Creditos
            5: Salir
        """

        self.__reset()

        if valor == 1:
            # Fase 1: Introduccion
            self.intro_widget = IntroWidget()
            self.intro_widget.connect(
                "switch", self.__intro_switch)
            self.add(self.intro_widget)

            GLib.idle_add(self.intro_widget.load,
                os.path.join(BASE, "Iconos", "jamtank.svg"))

        elif valor == 2:
            # Fase 2: Selecciones de mapa, tanque, oponentes.
            self.select_widget = SelectWidget()
            self.select_widget.connect(
                "salir", self.__select_switch)
            self.select_widget.connect(
                "run", self.__run)
            self.add(self.select_widget)

        elif valor == 3:
            self.widget_game = GameWidget()
            self.add(self.widget_game)
            GLib.idle_add(self.widget_game.setup_init, datos)

        GLib.idle_add(self.queue_draw)

    def __run(self, widget, datos):

        self.switch(3, datos=datos)

    def __select_switch(self, widget):
        """
        Cuando hace click en Anterior de seleccionar mapa.
        """

        self.switch(1)

    def __intro_switch(self, widget, valor):
        """
        Cuando en la ventana de Introducción se
        selecciona el tipo de juego (solo o en red),
        o los creditos o salir.
        """

        if valor == "solo":
            self.switch(2)

        elif valor == "red":
            pass

        elif valor == "creditos":
            pass

        elif valor == "salir":
            self.__salir()

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

    def __update_events(self):

        self.widget_game.juego.update_events(self.eventos)

    def __salir(self, widget=None, event=None):

        import sys

        if self.widget_game:
            self.widget_game.juego.estado = False
            pygame.quit()

        sys.exit(0)


if __name__ == "__main__":
    JAMTank()
    Gtk.main()
