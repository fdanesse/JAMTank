
using Gtk;
using Gdk;

//using SDL;
//using SDLImage;
//using SDLGraphics;


public class JAMTank : Gtk.Window{

    //private Juego juego;
    private VideoVisor visor = new VideoVisor();

    public JAMTank(){

        this.set_title("Ventana");
        this.window_position = Gtk.WindowPosition.CENTER;
        this.set("border_width", 2);

        this.add(this.visor);
        this.visor.run.connect(this.__run);

        this.show_all();
        this.realize();

        this.key_press_event.connect ((event) => {
            this.__do_key_press_event(event);
            return true;
            });

        this.key_release_event.connect ((event) => {
            this.__do_key_release_event(event);
            return true;
            });

        this.destroy.connect(this.__salir);
        }

    private void __run(){
        //SDL.init(InitFlag.EVERYTHING);
        //this.juego = new Juego();
        //GLib.Timeout.add(35, this.juego.run);
        //GLib.stdout.printf(GLib.Environment.get_variable("SDL_WINDOWID"));
        //GLib.stdout.flush();
        }

    private void __do_key_press_event(Gdk.EventKey event){
        GLib.stdout.printf("p: %s\n", event.str);
        GLib.stdout.flush();
        }

    private void __do_key_release_event(Gdk.EventKey event){
        GLib.stdout.printf("r: %s\n", event.str);
        GLib.stdout.flush();
        }

    private void __salir(){
        Gtk.main_quit();
        }
}


public class VideoVisor : Gtk.DrawingArea{

    public signal void run();

    public VideoVisor(){
        this.set_size_request(640, 480);
        this.realize.connect(this.__realize);
        this.show_all();
        }

    private void __realize(){
        //uint xid = (uint)Gdk.X11Window.get_xid(this.get_window());
        //string sxid = xid.to_string();
        //GLib.Environment.set_variable("SDL_WINDOWID", sxid, true);
        //GLib.stdout.printf("XID %s\n", GLib.Environment.get_variable("SDL_WINDOWID"));
        //GLib.stdout.flush();
        //this.run();
        }
}


public static int main (string[] args) {
    Gtk.init(ref args);
    JAMTank app = new JAMTank();
    app.show_all();
    Gtk.main();
    return 0;
    }
