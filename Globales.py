#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Globals.py por:
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


def get_ip():
    #import socket
    #try:
    #    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #    s.connect(("google.com", 80))
    #    ret = s.getsockname()[0]
    #    s.close()
    #    return ret
    #except socket.error, err:
    #    print "Error", get_ip, err
    #    return "localhost"
    import commands
    text = commands.getoutput('ifconfig eth0').splitlines()
    datos = ''
    for linea in text:
        if 'Direc. inet:' in linea and 'Difus.:' in linea and 'Másc:' in linea:
            datos = linea
            break
    ip = 'localhost'
    if datos:
        ip = datos.split('Direc. inet:')[1].split('Difus.:')[0].strip()
    return ip
