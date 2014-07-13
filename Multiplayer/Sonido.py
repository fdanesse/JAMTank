#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gst', '1.0')

from gi.repository import GObject
from gi.repository import Gst

GObject.threads_init()
Gst.init([])


def play(sound):
    player = Gst.ElementFactory.make("playbin", "player")
    fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
    player.set_property('video-sink', fakesink)
    audiosink = Gst.ElementFactory.make("autoaudiosink", "audiosink")
    player.set_property('audio-sink', audiosink)
    direccion = Gst.filename_to_uri(sound)
    player.set_property("uri", direccion)
    player.set_state(Gst.State.PLAYING)


class Motor(GObject.GObject):

    __gsignals__ = {
    "endfile": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self, sound):

        GObject.GObject.__init__(self)

        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property('video-sink', fakesink)
        audiosink = Gst.ElementFactory.make("autoaudiosink", "audiosink")
        self.player.set_property('audio-sink', audiosink)
        direccion = Gst.filename_to_uri(sound)
        self.player.set_property("uri", direccion)

        self.bus = self.player.get_bus()
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message', self.__sync_message)

        self.player.set_state(Gst.State.PLAYING)

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.EOS:
            print "\n Gst.MessageType.EOS:"
            self.emit("endfile")
        elif mensaje.type == Gst.MessageType.ERROR:
            print "\n Gst.MessageType.ERROR:"
            print mensaje.parse_error()
