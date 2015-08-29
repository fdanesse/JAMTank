#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk


class DialogoEndGame(gtk.Dialog):

    def __init__(self, parent=None, _dict={}):

        gtk.Dialog.__init__(self, parent=parent,
        buttons=("Salir", gtk.RESPONSE_CANCEL))

        self.set_decorated(False)
        #self.modify_bg(gtk.STATE_NORMAL, get_colors("window"))
        self.set_border_width(15)

        # ('192.168.1.12',
        #    {'a': 0, 'b': [], 'n': 'cacho', 's': {'p': 12, 'e': 100, 'v': 4}, 't': 't1.png', 'y': 300, 'x': 400})
        # ('192.168.1.11',
        #   {'a': 0, 'b': [], 'n': 'flavio', 's': {'p': 12, 'e': 100, 'v': 4}, 't': 't5.png', 'y': 300, 'x': 400})

        #label = gtk.Label(text)
        #label.show()

        #self.vbox.pack_start(label, True, True, 5)

        print "Juego Terminado:"
        for item in _dict.items():
            print "\t", item
