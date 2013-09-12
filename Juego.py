#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *

RESOLUCION_INICIAL = (800,600)
BASE_PATH = os.path.dirname(__file__)

class Juego():
    """
    Juego de Batalla entre Tanques.
    """
    
    def __init__(self):
        
        ### Variables de clase
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = False
        
    def config(self):
        """
        Configuración inicial del Juego.
        """
        
        pygame.init()
        self.reloj = pygame.time.Clock()
        
        pygame.display.set_mode(RESOLUCION_INICIAL, 0, 0)
        pygame.display.set_caption("JAMtank 2")
        
        archivo = os.path.join(BASE_PATH,
            "Escenarios", "fondo1.png")
            
        imagen = pygame.image.load(archivo)
        
        self.escenario = pygame.transform.scale(
            imagen, RESOLUCION_INICIAL).convert_alpha()
            
        self.ventana = pygame.display.get_surface()
        
        pygame.mouse.set_visible(False)
        
    def run(self):
        """
        El Juego comienza a Correr.
        """
        
        self.estado = "En Juego"
        
        self.ventana.blit(self.escenario, (0,0))
        pygame.display.update()
        
        while self.estado == "En Juego":
            self.reloj.tick(35)
            pygame.display.update()
            
if __name__ == "__main__":
    juego = Juego()
    juego.config()
    juego.run()
    