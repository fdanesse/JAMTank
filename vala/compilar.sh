
valac --pkg glib-2.0 --pkg gio-2.0 --pkg gtk+-3.0 --pkg gdk-3.0 --pkg gdk-x11-3.0 \
    --pkg gee-1.0 --pkg sdl --pkg sdl-image --pkg sdl-gfx -X -lSDL_gfx -X -lSDL_image -o jamtank \
    ventana.vala introwidget.vala gamewidget.vala creditoswidget.vala widgets.vala \
    Juego/juego.vala Juego/protagonista.vala Juego/globales.vala
