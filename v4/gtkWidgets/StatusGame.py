#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk


class StatusGame(gtk.Window):

    def __init__(self, top, screen_wh):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        w, h = screen_wh
        self.set_size_request(w/4, h)
        self.set_resizable(False)
        self.move(w / 4 * 3, 0)
        self.set_deletable(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_transient_for(top)
        #self.set_keep_below(False)
        #self.set_keep_above(True)
        self.show_all()
