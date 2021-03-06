#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Globales.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

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

import socket
import pango


def get_ip():
    ip = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 80))
        ip = s.getsockname()[0]
    except:
        pass
    return ip


def set_font(widget, tipo, typewidget=""):
    attrlist = pango.AttrList()
    fg_color = pango.AttrForeground(0, 0, 0, 0, -1)
    stype = pango.AttrWeight(pango.WEIGHT_BOLD, 0, -1)
    fontdesc = pango.FontDescription("Monospace 12")
    if tipo == "titulo":
        fontdesc = pango.FontDescription("Monospace 20")
        stype = pango.AttrWeight(pango.WEIGHT_ULTRABOLD, 0, -1)
    elif tipo == "subtitulo1":
        fontdesc = pango.FontDescription("Monospace 16")
    elif tipo == "subtitulo2":
        fontdesc = pango.FontDescription("Monospace 14")
    else:
        fg_color = pango.AttrForeground(0, 27756, 0, 0, -1)
    widget.modify_font(fontdesc)
    attrlist.insert(fg_color)
    attrlist.insert(stype)
    if "Label" in str(type(widget)) or "Label" in typewidget:
        widget.set_attributes(attrlist)
    elif "Frame" in str(type(widget)) or "Frame" in typewidget:
        widget.get_label_widget().set_attributes(attrlist)
    elif "Entry" in str(type(widget)) or "Entry" in typewidget:
        widget.get_layout().set_attributes(attrlist)
    else:
        print str(type(widget))
