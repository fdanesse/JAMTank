

public class GameWidget : Gtk.Grid{

    public signal void accion(string text);

    private VideoVisor visor = new VideoVisor();

    public GameWidget(){

        this.set_property("column_homogeneous", true);
        this.set_property("row_homogeneous", true);

        this.attach(this.visor, 0, 0, 1, 1);

        this.show_all();
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
        ConfirmarSalir dialog = new ConfirmarSalir(
            this.get_toplevel() as Gtk.Window, "Alerta",
            "¿ Abandonar el Juego ?");
        int resp = dialog.run();
        dialog.destroy();
        if (resp == -5)
            this.__salir();
        }

    private void __salir(){
        this.accion("Salir");
        }
}
