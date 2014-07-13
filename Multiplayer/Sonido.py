#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gst', '1.0')

from gi.repository import GObject
from gi.repository import Gst

#GObject.threads_init()
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
