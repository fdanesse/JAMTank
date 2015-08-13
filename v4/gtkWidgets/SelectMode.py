#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import gobject


#FIXME: Analizar si no es mejor un dialog
class SelectMode(gtk.Window):

    __gsignals__ = {
    "switch": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self, top):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)

        self.set_resizable(False)
        self.set_position(3)
        self.set_deletable(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        self.set_transient_for(top)

        child = IntroWidget()
        self.add(child)
        self.show_all()

        child.connect("switch", self.__emit_switch)

    def __emit_switch(self, widget, valor):
        self.emit("switch", valor)
        self.destroy()


class IntroWidget(gtk.Table):

    __gsignals__ = {
    "switch": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self):

        gtk.Table.__init__(self, rows=7, columns=3, homogeneous=True)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffeeaa"))
        #self.imagen = False
        #self.temp_path = "/dev/shm/jamtank_intro_img.png"

        boton = gtk.Button("Jugar Solo")
        boton.connect("clicked", self.__emit_switch, "solo")
        self.attach(boton, 1, 2, 1, 2)
        boton.set_sensitive(False)

        boton = gtk.Button("Crear en Red")
        boton.connect("clicked", self.__emit_switch, "red")
        self.attach(boton, 1, 2, 2, 3)

        boton = gtk.Button("Unirse en Red")
        boton.connect("clicked", self.__emit_switch, "join")
        self.attach(boton, 1, 2, 3, 4)

        boton = gtk.Button("Creditos")
        boton.connect("clicked", self.__emit_switch, "creditos")
        self.attach(boton, 1, 2, 4, 5)
        boton.set_sensitive(False)

        boton = gtk.Button("Salir")
        boton.connect("clicked", self.__emit_switch, "salir")
        self.attach(boton, 1, 2, 5, 6)

        self.show_all()

    #def __do_draw(self, widget, event):
    #    context = widget.window.cairo_create()
    #    rect = self.get_allocation()
    #    src = self.imagen
    #    dst = gtk.gdk.pixbuf_new_from_file_at_size(
    #        self.temp_path, rect.width, rect.height)
    #    gtk.gdk.Pixbuf.scale(src, dst, 0, 0, 100, 100, 0, 0, 1.5, 1.5,
    #        0) #GdkPixbuf.InterpType.BILINEAR
    #    x = rect.width / 2 - dst.get_width() / 2
    #    y = rect.height / 2 - dst.get_height() / 2
    #    context.set_source_pixbuf(dst, x, y)
    #    context.paint()
    #    return True

    def __emit_switch(self, widget, valor):
        self.emit("switch", valor)

    #def load(self, path):
    #    """
    #    Carga una imagen para pintar el fondo.
    #    """
    #    if path:
    #        if os.path.exists(path):
    #            self.imagen = gtk.gdk.pixbuf_new_from_file(path)
    #            self.imagen.save(self.temp_path, "png")#, [], [])
    #            self.set_size_request(-1, -1)
    #    self.connect("expose-event", self.__do_draw)
