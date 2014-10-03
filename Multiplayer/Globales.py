#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import codecs


def __return_ip(interfaz):
    import commands
    import platform
    sistema = platform.platform()
    text = commands.getoutput('ifconfig %s' % interfaz).splitlines()
    datos = ''
    for linea in text:
        if 'olpc' in sistema:
            if 'inet ' in linea and 'netmask ' in linea and 'broadcast ' in linea:
                datos = linea
                break
        else:
            if 'Direc. inet:' in linea and 'Difus.:' in linea and 'Másc:' in linea:
                datos = linea
                break
    ip = ''
    if datos:
        if 'olpc' in sistema:
            ip = datos.split('inet ')[1].split('netmask ')[0].strip()
        else:
            ip = datos.split('Direc. inet:')[1].split('Difus.:')[0].strip()
    return ip


def get_ip():
    ip = __return_ip("wlan0")
    if not ip:
        ip = __return_ip("eth0")
    if not ip:
        ip = 'localhost'
    return ip


MAKELOG = True
LOGPATH = os.path.join(os.environ["HOME"], "JAMTank_load.log")


def reset_log():
    if os.path.exists(LOGPATH):
        os.remove(LOGPATH)


def WRITE_LOG(_dict):
    archivo = open(LOGPATH, "w")
    archivo.write(json.dumps(
        _dict, indent=4, separators=(", ", ":"), sort_keys=True))
    archivo.close()


def APPEND_LOG(_dict):
    new = {}
    if os.path.exists(LOGPATH):
        archivo = codecs.open(LOGPATH, "r", "utf-8")
        new = json.JSONDecoder("utf-8").decode(archivo.read())
        archivo.close()
    for key in _dict.keys():
        new[key] = _dict[key]
    WRITE_LOG(new)
