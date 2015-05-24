
using Gtk;
using Gdk;

//using SDL;
//using SDLImage;
//using SDLGraphics;


public class JAMTank : Gtk.Window{

    //private Juego juego;
    private IntroWidget introwidget;
    private GameWidget gamewidget;
    private CreditosWidget creditoswidget;
    //private VideoVisor visor = new VideoVisor();

    public JAMTank(){

        this.set_title("Ventana");
        this.window_position = Gtk.WindowPosition.CENTER;
        this.set("border_width", 2);

        //this.visor.run.connect(this.__run);

        this.show_all();
        this.fullscreen();
        this.__switch("Intro");

        this.key_press_event.connect ((event) => {
            this.__do_key_press_event(event);
            return true;
            });

        this.key_release_event.connect ((event) => {
            this.__do_key_release_event(event);
            return true;
            });

        //this.destroy.connect(this.__salir);
        }

    private void __switch(string text){
        /*
        Cambia la interfaz interna:
            Introducción
            Juego Gtk + SDL
            Creditos
        */
        weak Gtk.Widget widget = this.get_child();
        widget.destroy();
        widget.unref();
        if (text == "Intro"){
            this.introwidget = new IntroWidget();
            this.add(this.introwidget);
            this.introwidget.accion.connect ((text) => {
                this.__intro_accion(text);
                });
            }
        else if (text == "Jugar"){
            this.gamewidget = new GameWidget();
            this.add(this.gamewidget);
            this.gamewidget.accion.connect ((text) => {
                this.__game_accion(text);
                });
            }
        else if (text == "Creditos"){
            this.creditoswidget = new CreditosWidget();
            this.add(this.creditoswidget);
            this.creditoswidget.accion.connect ((text) => {
                this.__creditos_accion(text);
                });
            }
        }

    private void __run(){
        //SDL.init(InitFlag.EVERYTHING);
        //this.juego = new Juego();
        //GLib.Timeout.add(35, this.juego.run);
        //GLib.stdout.printf(GLib.Environment.get_variable("SDL_WINDOWID"));
        //GLib.stdout.flush();
        }

    private void __intro_accion(string text){
        /*
        Gestiona las acciones desde introwidget.
        */
        if (text == "Salir")
            this.__confirmar_salir();
        else
            this.__switch(text);
        }

    private void __game_accion(string text){
        /*
        Gestiona las acciones que llegan desde gamewidget.
        */
        if (text == "Salir")
            this.__switch("Intro");
        }

    private void __creditos_accion(string text){
        /*
        Gestiona las acciones que llegan desde creditoswidget.
        */
        if (text == "Salir")
            this.__switch("Intro");
        }

    private void __do_key_press_event(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla presionada.
        */
        weak Gtk.Widget widget = this.get_child();
        if (widget == this.gamewidget)
            this.gamewidget.press(event);
        else if (widget == this.creditoswidget)
            this.creditoswidget.press(event);
        else
            if (event.keyval == 65307)
                this.__confirmar_salir();
        }

    private void __do_key_release_event(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla que deja de estar presionada.
        */
        weak Gtk.Widget widget = this.get_child();
        if (widget == this.gamewidget)
            this.gamewidget.release(event);
        }

    private void __confirmar_salir(){
        /*
        Abre Dialogo para confirmar salida de la aplicación.
        */
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
