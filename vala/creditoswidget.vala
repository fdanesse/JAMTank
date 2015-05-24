

public class CreditosWidget : Gtk.Grid{

    public signal void accion(string text);

    public CreditosWidget(){

        this.set_property("column_homogeneous", true);
        this.set_property("row_homogeneous", true);

        this.attach(new Gtk.Label("Creditos"), 0, 0, 1, 1);

        this.show_all();
        }

    public void press(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla presionada.
        */
        if (event.keyval == 65307)
            this.__salir();
        }

    private void __salir(){
        this.accion("Salir");
        }
}
