using SDL;


public class GameWidget : Gtk.Grid{

    public signal void accion(string text);

    private Gtk.DrawingArea visor = new Gtk.DrawingArea();
    private Juego juego;
    private uint actualizador = 0;

    public GameWidget(){

        this.set_property("column_homogeneous", true);
        this.set_property("row_homogeneous", true);

        this.visor.set_size_request(640, 480);
        this.attach(this.visor, 0, 0, 1, 1);
        this.visor.realize.connect(this.__realize);

        this.show_all();
        }

    private void __realize(){
        /*
        Configura SDL para dibujar en nuestro widget de gtk.
        */
        uint xid = (uint)Gdk.X11Window.get_xid(this.visor.get_window());
        string sxid = xid.to_string();
        GLib.Environment.set_variable("SDL_WINDOWID", sxid, true);
        GLib.stdout.printf("XID %s\n", GLib.Environment.get_variable("SDL_WINDOWID"));
        GLib.stdout.flush();
        this.__game_run();
        }

    private void __game_run(){
        /*
        Lanza el juego.
        */
        SDL.init(InitFlag.EVERYTHING);
        this.juego = new Juego();
        if (this.actualizador > 0){
            GLib.Source.remove(this.actualizador);
            this.actualizador = 0;
            }
        this.actualizador = GLib.Timeout.add(35, this.juego.run);
        }

    public void press(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla presionada.
        */
        if (event.keyval == 65307)
            this.__confirmar_salir();
        else
            GLib.stdout.printf("p: %s\n", event.str);
            GLib.stdout.flush();
        }

    public void release(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla que deja de estar presionada.
        */
        GLib.stdout.printf("r: %s\n", event.str);
        GLib.stdout.flush();
        }

    private void __confirmar_salir(){
        /*
        Abre Dialogo para confirmar salida.
        */
        this.juego.paused = true;
        ConfirmarSalir dialog = new ConfirmarSalir(
            this.get_toplevel() as Gtk.Window, "Alerta",
            "¿ Abandonar el Juego ?");
        int resp = dialog.run();
        dialog.destroy();
        if (resp == -5){
            this.__salir();
            }
        else{
            this.juego.paused = false;
            }
        }

    private void __salir(){
        if (this.actualizador > 0){
            GLib.Source.remove(this.actualizador);
            this.actualizador = 0;
            }
        this.juego.running = false;
        this.juego.paused = false;
        //this.juego.unref();
        SDL.quit();
        this.accion("Salir");
        }
}
