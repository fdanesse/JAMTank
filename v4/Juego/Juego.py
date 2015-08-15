#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
import random
import gobject
import gtk

RES = (800, 600)
BASE_PATH = os.path.realpath(os.path.dirname(__file__))


class Juego(gobject.GObject):

    #__gsignals__ = {
    #"update": (gobject.SIGNAL_RUN_LAST,
    #    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    #"end": (gobject.SIGNAL_RUN_LAST,
    #    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gobject.GObject.__init__(self)

        self._res = RES
        self._escenario = False
        self._win = False
        self._real_win = False
        self._clock = False
        self._estado = False
        self._client = False
        self._time = 35

        self._jugadores = pygame.sprite.RenderUpdates()
        self._balas = pygame.sprite.RenderUpdates()
        self._explosiones = pygame.sprite.RenderUpdates()

        print "Nuevo Juego Creado"

    def __enviar_datos(self):
        if self._client:
            _dict = {"ingame": {"nada": ""}}
            self._client.enviar(_dict)

    def __recibir_datos(self):
        if self._client:
            _dic = self._client.recibir()
            #print "Juego Recibe:", _dic

    def __emit_update(self):
        if bool(self._estado):
            #self.emit("update", dict(self.JUGADORES))
            #gobject.timeout_add(1500, self.__emit_update)
            pass
        return False

    def __end(self):
        self._estado = False
        pygame.quit()
        if self._client:
            self._client.desconectarse()
            del(self._client)
            self._client = False
        #self.emit("end", dict(self.JUGADORES))

    def run(self):
        print "Comenzando a Correr el juego..."
        self._estado = "En Juego"
        self._win.blit(self._escenario, (0, 0))
        pygame.display.update()
        pygame.time.wait(3)
        #gobject.timeout_add(1500, self.__emit_update)
        while self._estado == "En Juego":
            try:
                self._clock.tick(self._time)
                while gtk.events_pending():
                    gtk.main_iteration()
                self._jugadores.clear(self._win, self._escenario)
                self._balas.clear(self._win, self._escenario)
                self._explosiones.clear(self._win, self._escenario)

                self.__enviar_datos()
                self.__recibir_datos()

                self._explosiones.update()

                self._jugadores.draw(self._win)
                self._balas.draw(self._win)
                self._explosiones.draw(self._win)

                self._real_win.blit(pygame.transform.scale(
                    self._win, self._res), (0, 0))

                pygame.display.update()
                pygame.event.pump()
                pygame.event.clear()
                #pygame.time.wait(1)
            except:
                "Error en run game"
                self._estado = False

    def update_events(self, eventos):
        #if "space" in eventos:
        #    if not self.bala:
        #        self.disparo = True
        #    eventos.remove("space")
        #if self.jugador:
        #    self.jugador.update_events(eventos)
        pass

    def salir(self, valor):
        """
        La Interfaz gtk manda salir del juego.
        """
        self._estado = False
        pygame.quit()
        if self._client:
            #self._client.enviar(valor)
            #datos = self._client.recibir()
            #self._client.desconectarse()
            #del(self._client)
            #self._client = False
            #if datos == "END":
            #    self.__end()
            pass

    def load(self, mapa):
        print "Cargando mapa:", mapa
        imagen = pygame.image.load(mapa)
        self._escenario = pygame.transform.scale(imagen, RES).convert_alpha()
        #path = os.path.dirname(BASE_PATH)
        #sound = os.path.join(path, "Audio", "Juego.ogg")
        #self.sound_juego = pygame.mixer.Sound(sound)
        #self.sound_juego.play(-1)
        #disparo = os.path.join(path, "Audio", "disparo.ogg")
        #self.sound_disparo = pygame.mixer.Sound(disparo)
        #explosion = os.path.join(path, "Audio", "explosion.ogg")
        #self.sound_explosion = pygame.mixer.Sound(explosion)
        #self.jugador = Jugador(self.JUGADORES[self.ip]["tanque"],
        #    RES, self.ip)
        #self._jugadores.add(self.jugador)

    def config(self, time=35, res=(800, 600), client=False, xid=False):
        print "Configurando Juego:"
        print "\ttime:", time
        print "\tres:", res
        print "\tclient", client
        print "\txid", xid
        self._time = time
        self._res = res
        self._client = client
        if xid:
            os.putenv("SDL_WINDOWID", str(xid))
        pygame.init()
        self._clock = pygame.time.Clock()
        from pygame.locals import MOUSEMOTION
        from pygame.locals import MOUSEBUTTONUP
        from pygame.locals import MOUSEBUTTONDOWN
        from pygame.locals import JOYAXISMOTION
        from pygame.locals import JOYBALLMOTION
        from pygame.locals import JOYHATMOTION
        from pygame.locals import JOYBUTTONUP
        from pygame.locals import JOYBUTTONDOWN
        from pygame.locals import VIDEORESIZE
        from pygame.locals import VIDEOEXPOSE
        from pygame.locals import USEREVENT
        from pygame.locals import QUIT
        from pygame.locals import ACTIVEEVENT
        from pygame.locals import KEYDOWN
        from pygame.locals import KEYUP
        pygame.event.set_blocked([MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN,
            JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP,
            JOYBUTTONDOWN, ACTIVEEVENT, USEREVENT, KEYDOWN, KEYUP])
        pygame.event.set_allowed([QUIT, VIDEORESIZE, VIDEOEXPOSE])
        #pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)
        pygame.display.set_mode(self._res, pygame.DOUBLEBUF, 0)
        pygame.display.set_caption("JAMtank")
        self._win = pygame.Surface(RES)
        self._real_win = pygame.display.get_surface()
        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)


if __name__ == "__main__":
    mapa = os.path.join(os.path.dirname(BASE_PATH), "Mapas", "f2.png")
    juego = Juego()
    juego.config(time=35, res=(800, 600), client=False, xid=False)
    juego.load(mapa)
    juego.run()
