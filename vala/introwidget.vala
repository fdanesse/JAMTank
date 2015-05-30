
public class IntroWidget : Gtk.Grid{

    public signal void accion(string acc);

    public IntroWidget(){

        this.set_property("column_homogeneous", true);
        this.set_property("row_homogeneous", true);

        Gtk.Button button1 = new Gtk.Button.with_label ("Jugar");
        button1.clicked.connect (() => {
            this.__emit("Jugar");
            });
        this.attach(button1, 0, 0, 1, 1);

        Gtk.Button button2 = new Gtk.Button.with_label ("Creditos");
        button2.clicked.connect (() => {
            this.__emit("Creditos");
            });
        this.attach(button2, 0, 1, 1, 1);

        Gtk.Button button3 = new Gtk.Button.with_label ("Salir");
        button3.clicked.connect (() => {
            this.__emit("Salir");
            });
        this.attach(button3, 0, 2, 1, 1);

        this.show_all();
        }

    private void __emit(string text){
        this.accion(text);
    }
}
