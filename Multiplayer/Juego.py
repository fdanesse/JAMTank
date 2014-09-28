#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygame
import json
import codecs

from gi.repository import GObject
from gi.repository import Gtk

from Jugador import Jugador
#from Bala import Bala

RESOLUCION_INICIAL = (800, 600)
BASE_PATH = os.path.dirname(__file__)

MODEL = {
    'nick': '',
    'tanque': '',
    'puntos': 0,
    }


def get_ip():
    import commands
    text = commands.getoutput('ifconfig wlan0').splitlines()
    datos = ''
    for linea in text:
        if 'Direc. inet:' in linea and 'Difus.:' in linea and 'Másc:' in linea:
            datos = linea
            break
    ip = 'localhost'
    if datos:
        ip = datos.split('Direc. inet:')[1].split('Difus.:')[0].strip()
    return ip


MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")


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


class Juego(GObject.Object):

    __gsignals__ = {
    "update": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, []),
    "end": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self, _dict, client):

        GObject.Object.__init__(self)

        self.GAME = {}
        self.GAME['mapa'] = str(_dict['mapa'].strip())

        self.ip = get_ip()
        self.JUGADORES = {}
        self.JUGADORES[self.ip] = dict(MODEL)
        self.JUGADORES[self.ip]['nick'] = str(_dict['nick'].strip())
        self.JUGADORES[self.ip]['tanque'] = str(_dict['tanque'].strip())

        self.client = client

        self.resolucionreal = RESOLUCION_INICIAL
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = False
        self.jugador = False
        #self.bala = False
        #self.disparo = False

        self.jugadores = pygame.sprite.RenderUpdates()
        #self.balas = pygame.sprite.RenderUpdates()
        #self.explosiones = pygame.sprite.RenderUpdates()

    def __enviar_datos(self):
        self.jugador.update()
        a, x, y = self.jugador.get_datos()

        datos = "UPDATE,%s,%s,%s" % (a, x, y)
        #if self.disparo:
        #    datos = "%s,%s,%s,%s" % (datos, a, x, y)
        #    self.disparo = False
        #elif self.bala:
        #    self.bala.update()
        #    a, x, y = self.bala.get_datos()
        #    datos = "%s,%s,%s,%s" % (datos, a, x, y)
        #else:
        #    datos = "%s,-,-,-" % datos

        self.client.enviar(datos)

    def __recibir_datos(self):
        datos = self.client.recibir()

        if not datos:
            print "Se recibió datos vacíos en el Juego"
            return

        if datos == "END":
            self.estado = False
            pygame.quit()
            if self.client:
                self.client.desconectarse()
                del(self.client)
                self.client = False
            self.emit("end")
            return

        for client in datos.split("||"):
            if not client:
                return

            #ip, nick, tanque, a, x, y, aa, xx, yy = client.split(",")
            ip, nick, tanque, a, x, y = client.split(",")

            if a == '-' and x == '-' and y == '-':
                for j in self.jugadores.sprites():
                    if ip == j.ip:
                        self.__eliminar_jugador(j, ip)
                        break
            else:
                a = int(a)
                x = int(x)
                y = int(y)

                self.__actualizar_tanque(ip, nick, tanque, a, x, y)

            #if aa != '-' and xx != '-' and yy != '-':
            #    aa = int(aa)
            #    xx = int(xx)
            #    yy = int(yy)

            #    self.__actualizar_bala(ip, aa, xx, yy)

            #else:
            #    for bala in self.balas.sprites():
            #        if ip == bala.ip:
            #            self.__eliminar_bala(bala, ip)
            #            break

        #self.__checkear_colisiones()

    #def __checkear_colisiones(self):
    #    """
    #    Checkea colisiones entre balas y de balas agenas con mi tanque.
    #    """
    #    # colisiones entre balas
    #    rect = self.jugador.rect
    #    for bala in self.balas.sprites():
    #        if self.ip == bala.ip:
    #            continue
    #        x, y = bala.rect.centerx, bala.rect.centery
    #        if rect.collidepoint(x, y):
    #            self.jugador.tocado()
    #            # explosion

    def __actualizar_tanque(self, ip, nick, tanque, a, x, y):
        """
        Actualiza posiciòn de tanque.
        """
        if not ip in self.JUGADORES.keys():
            self.JUGADORES[ip] = dict(MODEL)
            self.JUGADORES[ip]['nick'] = nick
            self.JUGADORES[ip]['tanque'] = os.path.join(
                os.path.dirname(BASE_PATH), "Tanques", tanque)

            ips = []
            for j in self.jugadores.sprites():
                if not j.ip in ips:
                    ips.append(j.ip)

            if not ip in ips:
                j = Jugador(self.JUGADORES[ip]['tanque'],
                    RESOLUCION_INICIAL, ip)
                self.jugadores.add(j)

            key = "Jugador Remoto Agregado en Juego.py %s" % ip
            new = {key: {"Actuales:": dict(self.JUGADORES)}}
            APPEND_LOG(new)

        for j in self.jugadores.sprites():
            if ip == j.ip:
                # FIXME: nick y tanque deben actualizarse
                j.update_data(a, x, y)
                break

    '''
    def __actualizar_bala(self, ip, aa, xx, yy):
        """
        Actualiza la posiciòn de las balas.
        """
        if not ip in BALAS.keys():
            BALAS[ip] = True
            image_path = os.path.join(os.path.dirname(
                os.path.dirname(self.GAME['mapa'])), 'Iconos', 'bala.png')
            bala = Bala(aa, xx, yy, image_path, RESOLUCION_INICIAL, ip)
            self.balas.add(bala)
            if ip == self.ip:
                self.bala = bala

        else:
            for bala in self.balas.sprites():
                if ip == bala.ip:
                    valor = bala.set_posicion(centerx=xx, centery=yy)
                    if not valor:
                        self.__eliminar_bala(bala, ip)
                    break

    def __eliminar_bala(self, bala, ip):
        """
        Elimina una bala.
        """
        bala.kill()
        del(bala)
        bala = False
        if BALAS.get(ip, False):
            del(BALAS[ip])
        if ip == self.ip:
            del(self.bala)
            self.bala = False
    '''

    def __eliminar_jugador(self, j, ip):
        j.kill()
        del(j)
        del(self.JUGADORES[ip])
        if ip == self.ip:
            del(self.jugador)
            self.jugador = False

    def run(self):
        self.estado = "En Juego"
        self.ventana.blit(self.escenario, (0, 0))
        pygame.display.update()
        pygame.time.wait(3)
        while self.estado == "En Juego":
            try:
                self.reloj.tick(35)
                while Gtk.events_pending():
                    Gtk.main_iteration()
                self.jugadores.clear(self.ventana, self.escenario)
                #self.balas.clear(self.ventana, self.escenario)
                #self.explosiones.clear(self.ventana, self.escenario)

                self.__enviar_datos()
                self.__recibir_datos()

                self.jugadores.draw(self.ventana)
                #self.balas.draw(self.ventana)
                #self.explosiones.draw(self.ventana)

                self.ventana_real.blit(pygame.transform.scale(self.ventana,
                    self.resolucionreal), (0, 0))

                pygame.display.update()
                pygame.event.pump()
                pygame.event.clear()
                pygame.time.wait(1)

            except:
                self.estado = False

    def escalar(self, resolucion):
        self.resolucionreal = resolucion

    def update_events(self, eventos):
        #if "space" in eventos and not self.bala:
        #    self.disparo = True
        self.jugador.update_events(eventos)

    def salir(self, valor):
        """
        La Interfaz gtk manda salir del juego.
        """
        self.estado = False
        pygame.quit()
        if self.client:
            self.client.enviar(valor)
            datos = self.client.recibir()
            self.client.desconectarse()
            del(self.client)
            self.client = False

    def config(self):
        pygame.init()
        self.reloj = pygame.time.Clock()

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

        pygame.display.set_mode(
            (0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)

        pygame.display.set_caption("JAMtank")
        imagen = pygame.image.load(self.GAME['mapa'])
        self.escenario = pygame.transform.scale(imagen,
            RESOLUCION_INICIAL).convert_alpha()

        self.ventana = pygame.Surface((RESOLUCION_INICIAL[0],
            RESOLUCION_INICIAL[1]))
        self.ventana_real = pygame.display.get_surface()

        pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.music.set_volume(1.0)
        #sonido_juego.play(-1)

        self.jugador = Jugador(self.JUGADORES[self.ip]['tanque'],
            RESOLUCION_INICIAL, self.ip)
        self.jugadores.add(self.jugador)
        x, y = RESOLUCION_INICIAL
        self.jugador.update_data(centerx=x/2, centery=y/2)
        APPEND_LOG({"Jugador Local": self.ip})


#if __name__ == "__main__":
#    juego = Juego()
#    juego.config()
#    juego.run()
