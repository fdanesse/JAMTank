#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import GLib

BASE = os.path.dirname(__file__)


def describe_archivo(archivo):
    """
    Devuelve el tipo de un archivo (imagen, video, texto).
    -z, --uncompress para ver dentro de los zip.
    """

    import commands

    datos = commands.getoutput(
        'file -ik %s%s%s' % ("\"", archivo, "\""))

    retorno = ""

    for dat in datos.split(":")[1:]:
        retorno += " %s" % (dat)

    return retorno


class SelectWidget(Gtk.EventBox):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, []),
    "run": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self, tipo='single'):

        Gtk.EventBox.__init__(self)

        self.game_dict = {
            'tipo': tipo,
            'mapa': "",
            'tanque': "",
            'enemigos': 1,
            'vidas': 10,
            }

        self.set_border_width(20)

        self.select_box = False

        self.show_all()

        self.__switch("mapa")

    def __switch(self, valor):

        for child in self.get_children():
            self.remove(child)
            child.destroy()

        if valor == "mapa":
            self.select_box = SelectBox("Mapa")
            self.add(self.select_box)
            self.select_box.connect(
                "accion", self.__accion_mapa)
            self.select_box.connect(
                "seleccion", self.__seleccion_mapa)

        elif valor == "tanque":
            self.select_box = SelectBox("Tanque")
            self.select_box.connect(
                "valor", self.__set_valores)
            self.add(self.select_box)
            self.select_box.connect(
                "accion", self.__accion_tanque)
            self.select_box.connect(
                "seleccion", self.__seleccion_tanque)

    def __set_valores(self, widget, valor, tipo):

        if tipo == "oponentes":
            self.game_dict['enemigos'] = valor

        elif tipo == "vidas":
            self.game_dict['vidas'] = valor

    def __seleccion_mapa(self, widget, path):

        self.game_dict['mapa'] = path

    def __seleccion_tanque(self, widget, path):

        self.game_dict['tanque'] = path

    def __accion_mapa(self, widget, accion):

        if accion == "Anterior":
            # volver a intro
            self.emit("salir")

        elif accion == "Siguiente":
            # ir a elegir tanque
            self.__switch("tanque")

    def __accion_tanque(self, widget, accion):

        if accion == "Anterior":
            # volver a elegir mapa
            self.__switch("mapa")

        elif accion == "Siguiente":
            # comenzar juego
            self.emit("run", self.game_dict)


class SelectBox(Gtk.VBox):
    """
    Widget para seleccionar un mapa o un tanque.
    """

    __gsignals__ = {
    "accion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "seleccion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "valor": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_INT,
        GObject.TYPE_STRING))}

    def __init__(self, tipo):

        Gtk.VBox.__init__(self)

        self.frame = Gtk.Frame()
        self.frame.set_label("Selecciona un %s" % tipo)
        self.frame.set_label_align(0.5, 0.5)

        if 'Mapa' in tipo:
            self.select = SelectPanelMapa()

        elif 'Tanque' in tipo:
            self.select = SelectPanelTanque()
            self.select.connect("valor", self.__emit_valor)

        self.frame.add(self.select)

        hbox = Gtk.HBox()
        button = Gtk.Button("Anterior")
        button.connect("clicked", self.__accion, "Anterior")
        hbox.pack_start(button, False, False, 0)
        button = Gtk.Button("Siguiente")

        if 'Tanque' in tipo:
            button.set_label("Jugar")

        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self.__accion, "Siguiente")

        self.pack_start(self.frame, True, True, 0)
        self.pack_end(hbox, False, False, 0)

        self.show_all()

        self.select.connect("seleccion", self.__emit_seleccion)

    def __emit_valor(self, widget, valor, tipo):

        self.emit("valor", valor, tipo)

    def __emit_seleccion(self, widget, path):

        self.emit("seleccion", path)

    def __accion(self, widget, accion):

        self.emit("accion", accion)


class SelectPanelMapa(Gtk.Paned):
    """
    Panel con lista de mapas para
    que el usuario elija.
    """

    __gsignals__ = {
    "seleccion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Paned.__init__(self,
            orientation=Gtk.Orientation.HORIZONTAL)

        self.lista = Lista()
        self.preview = Gtk.Image()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista)

        self.pack1(scroll,
            resize=False, shrink=False)
        self.pack2(self.preview,
            resize=True, shrink=True)

        scroll.set_size_request(230, -1)

        self.connect("realize", self.__do_realize)

        self.lista.connect(
            "nueva-seleccion", self.__set_image)

        self.show_all()

    def __do_realize(self, widget):

        elementos = []
        mapas_path = os.path.join(BASE, "Mapas")

        for arch in os.listdir(mapas_path):
            path = os.path.join(mapas_path, arch)

            if os.path.isfile(path):
                tipo = describe_archivo(path)

                if 'image' in tipo and not 'iso' in tipo:
                    archivo = os.path.basename(path)
                    elementos.append([archivo, path])

        self.lista.limpiar()
        self.lista.agregar_items(elementos)

    def __set_image(self, widget, path):

        rect = self.preview.get_allocation()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            path, -1, rect.height)
        self.preview.set_from_pixbuf(pixbuf)

        self.emit("seleccion", path)


class SelectPanelTanque(Gtk.Paned):
    """
    Panel con lista de mapas para
    que el usuario elija.
    """

    __gsignals__ = {
    "seleccion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "valor": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_INT,
        GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.Paned.__init__(self,
            orientation=Gtk.Orientation.HORIZONTAL)

        self.lista = Lista()
        self.preview = Gtk.Image()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista)

        self.pack1(scroll,
            resize=False, shrink=False)

        vbox = Gtk.VBox()
        oponentes = OponentesSelectBox()
        oponentes.connect("valor", self.__emit_valor)
        vbox.pack_start(self.preview, True, True, 0)
        vbox.pack_start(oponentes, True, True, 0)
        self.pack2(vbox,
            resize=True, shrink=True)

        scroll.set_size_request(230, -1)

        self.connect("realize", self.__do_realize)

        self.lista.connect(
            "nueva-seleccion", self.__set_image)

        self.show_all()

    def __emit_valor(self, widget, valor, tipo):

        self.emit("valor", valor, tipo)

    def __do_realize(self, widget):

        elementos = []
        mapas_path = os.path.join(BASE, "Tanques")

        for arch in os.listdir(mapas_path):
            path = os.path.join(mapas_path, arch)

            if os.path.isfile(path):
                tipo = describe_archivo(path)

                if 'image' in tipo and not 'iso' in tipo:
                    archivo = os.path.basename(path)
                    elementos.append([archivo, path])

        self.lista.limpiar()
        self.lista.agregar_items(elementos)

    def __set_image(self, widget, path):

        rect = self.preview.get_allocation()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            path, -1, rect.height)
        self.preview.set_from_pixbuf(pixbuf)

        self.emit("seleccion", path)


class OponentesSelectBox(Gtk.VBox):
    """
    Widget para seleccionar cantidad de enemigos y vidas.
    """

    __gsignals__ = {
    "valor": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_INT,
        GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.VBox.__init__(self)

        hbox = Gtk.HBox()
        oponentes = Gtk.Label("Oponentes:")
        spin = NumBox(range(1, 10))
        spin.connect("valor", self.__emit_valor, "oponentes")
        hbox.pack_start(oponentes, False, False, 5)
        hbox.pack_start(spin, False, False, 5)
        self.pack_start(hbox, False, False, 0)

        hbox = Gtk.HBox()
        limite = Gtk.Label("Vidas:")
        spin = NumBox(range(10, 50))
        spin.connect("valor", self.__emit_valor, "vidas")
        hbox.pack_start(limite, False, False, 5)
        hbox.pack_start(spin, False, False, 5)
        self.pack_start(hbox, False, False, 0)

        self.show_all()

    def __emit_valor(self, widget, valor, tipo):

        self.emit("valor", valor, tipo)


class NumBox(Gtk.HBox):
    """
    Spin para cambiar la cantidad de vidas o enemigos.
    """

    __gsignals__ = {
    "valor": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_INT, ))}

    def __init__(self, rango):

        Gtk.HBox.__init__(self)

        self.rango = rango
        self.valor = min(self.rango)

        menos = Gtk.Button("-")
        menos.connect("clicked", self.__change)
        self.label = Gtk.Label("0")
        mas = Gtk.Button("+")
        mas.connect("clicked", self.__change)

        self.pack_start(menos, False, False, 5)
        self.pack_start(self.label, False, False, 5)
        self.pack_start(mas, False, False, 5)

        self.show_all()

        self.label.set_text(str(self.valor))

    def __change(self, widget):

        label = widget.get_label()

        if label == "-":
            if self.valor - 1 >= min(self.rango):
                self.valor -= 1
                self.emit("valor", self.valor)

        elif label == "+":
            if self.valor + 1 <= max(self.rango) + 1:
                self.valor += 1
                self.emit("valor", self.valor)

        self.label.set_text(str(self.valor))


class Lista(Gtk.TreeView):
    """
    Lista generica.
    """

    __gsignals__ = {
    "nueva-seleccion": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self):

        Gtk.TreeView.__init__(self)

        self.set_property("rules-hint", True)
        self.set_headers_clickable(True)
        self.set_headers_visible(True)

        self.permitir_select = True
        self.valor_select = None

        self.modelo = Gtk.ListStore(
            GdkPixbuf.Pixbuf,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING)

        self.__setear_columnas()

        self.get_selection().set_select_function(
            self.__selecciones, self.modelo)

        self.set_model(self.modelo)
        self.show_all()

    def __selecciones(self, treeselection,
        model, path, is_selected, listore):
        """
        Cuando se selecciona un item en la lista.
        """

        if not self.permitir_select:
            return True

        # model y listore son ==
        iter = model.get_iter(path)
        valor = model.get_value(iter, 2)

        if not is_selected and self.valor_select != valor:
            self.scroll_to_cell(model.get_path(iter))
            self.valor_select = valor
            self.emit('nueva-seleccion', self.valor_select)

        return True

    def __setear_columnas(self):

        self.append_column(self.__construir_columa_icono('', 0, True))
        self.append_column(self.__construir_columa('Nombre', 1, True))
        self.append_column(self.__construir_columa('', 2, False))

    def __construir_columa(self, text, index, visible):

        render = Gtk.CellRendererText()

        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        return columna

    def __construir_columa_icono(self, text, index, visible):

        render = Gtk.CellRendererPixbuf()

        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        return columna

    def limpiar(self):

        self.permitir_select = False
        self.modelo.clear()
        self.permitir_select = True

    def agregar_items(self, elementos):
        """
        Recibe lista de: [texto para mostrar, path oculto] y
        Comienza secuencia de agregado a la lista.
        """

        self.get_toplevel().set_sensitive(False)
        self.permitir_select = False

        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def __ejecutar_agregar_elemento(self, elementos):
        """
        Agrega los items a la lista, uno a uno, actualizando.
        """

        if not elementos:
            self.permitir_select = True
            self.seleccionar_primero()
            self.get_toplevel().set_sensitive(True)
            return False

        texto, path = elementos[0]

        icono = False

        tipo = describe_archivo(path)

        if 'image' in tipo and not 'iso' in tipo:
            icono = os.path.join(path)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                icono, 50, -1)
            self.modelo.append([pixbuf, texto, path])

        elementos.remove(elementos[0])

        GLib.idle_add(
            self.__ejecutar_agregar_elemento, elementos)

        return False

    '''
    def seleccionar_siguiente(self, widget=None):

        modelo, iter = self.treeselection.get_selected()

        try:
            self.treeselection.select_iter(
                modelo.iter_next(iter))

        except:
            self.seleccionar_primero()

        return False

    def seleccionar_anterior(self, widget=None):

        modelo, iter = self.treeselection.get_selected()

        try:
            self.treeselection.select_iter(
                modelo.iter_previous(iter))

        except:
            self.seleccionar_ultimo()

        return False
    '''

    def seleccionar_primero(self, widget=None):

        self.get_selection().select_path(0)

    '''
    def seleccionar_ultimo(self, widget=None):

        model = self.get_model()
        item = model.get_iter_first()

        iter = None

        while item:
            iter = item
            item = model.iter_next(item)

        if iter:
            self.treeselection.select_iter(iter)
            #path = model.get_path(iter)
    '''
