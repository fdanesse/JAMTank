
public class ConfirmarSalir : Gtk.Dialog{

    public ConfirmarSalir(Gtk.Window parent, string title, string text){

        this.set("title", title);
        this.set_modal(true);
        this.set_transient_for(parent);
        this.set("border_width", 15);
        this.set_decorated(false);
        this.set_resizable(false);

        Gtk.Label label = new Gtk.Label(text);

        Gtk.Box Box = this.get_content_area ();
        Box.pack_start(label, true, true, 0);
        Box.show_all();

        this.add_button ("Salir", Gtk.ResponseType.OK);
        this.add_button ("Cancelar", Gtk.ResponseType.CANCEL);
    }
}
