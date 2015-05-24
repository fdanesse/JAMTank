
using Gtk;
using Gdk;

//using SDL;
//using SDLImage;
//using SDLGraphics;


public class JAMTank : Gtk.Window{

    //private Juego juego;
    private IntroWidget introwidget = new IntroWidget();
    //private VideoVisor visor = new VideoVisor();

    public JAMTank(){

        this.set_title("Ventana");
        this.window_position = Gtk.WindowPosition.CENTER;
        this.set("border_width", 2);

        this.add(this.introwidget);
        this.introwidget.accion.connect ((text) => {
            this.__intro_accion(text);
            });
        //this.visor.run.connect(this.__run);

        this.show_all();
        this.fullscreen();

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

    private void __intro_accion(string text){
        if (text == "Salir")
            this.__confirmar_salir();
        }

    private void __do_key_press_event(Gdk.EventKey event){
        if (event.keyval == 65307)
            this.__confirmar_salir();
        else
            GLib.stdout.printf("p: %s\n", event.keyval.to_string());
            GLib.stdout.flush();
        }

    private void __do_key_release_event(Gdk.EventKey event){
        GLib.stdout.printf("r: %s\n", event.str);
        GLib.stdout.flush();
        }

    private void __confirmar_salir(){
        ConfirmarSalir dialog = new ConfirmarSalir(this, "Alerta",
            "¿ Salir de JAMTank ?");
        int resp = dialog.run();
        dialog.destroy();
        if (resp == -5)
            this.__salir();
        }

    private void __salir(){
        Gtk.main_quit();
        }
}


public static int main (string[] args) {
    Gtk.init(ref args);
    JAMTank app = new JAMTank();
    app.show_all();
    Gtk.main();
    return 0;
    }
