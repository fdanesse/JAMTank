#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Globales.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import json
import codecs
import socket


def get_ip():
    ip = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 80))
        ip = s.getsockname()[0]
    except:
        pass
    return ip

'''
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
'''
