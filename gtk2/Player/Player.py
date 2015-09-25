#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Player.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import gobject
import gst

gobject.threads_init()


class Player(gobject.GObject):

    __gsignals__ = {
    "endfile": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, []),
        }

    # Estados: playing, paused, None

    def __init__(self):

        gobject.GObject.__init__(self)

        self.player = None
        self.bus = None

        self.player = gst.element_factory_make("playbin2", "player")
        self.player.set_property("buffer-size", 50000)

        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_mensaje)
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message', self.__sync_message)

    def __sync_message(self, bus, message):
        if message.type == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "PLayer ERROR:"
            print "\t%s" % err
            print "\t%s" % debug

    def __on_mensaje(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.emit("endfile")

        elif message.type == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "PLayer ERROR:"
            print "\t%s" % err
            print "\t%s" % debug

    def play(self):
        self.player.set_state(gst.STATE_PLAYING)

    def stop(self):
        self.player.set_state(gst.STATE_NULL)

    def load(self, uri):
        if not uri:
            return False
        if os.path.exists(uri):
            #direccion = gst.filename_to_uri(uri)
            direccion = "file://" + uri
            self.player.set_property("uri", direccion)
        else:
            if gst.uri_is_valid(uri):
                self.player.set_property("uri", uri)
        return False

    def set_volumen(self, volumen):
        self.player.set_property('volume', volumen)
