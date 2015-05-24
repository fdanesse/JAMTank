
public class VideoVisor : Gtk.DrawingArea{

    public signal void run();

    public VideoVisor(){
        //this.set_size_request(640, 480);
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
        GLib.stdout.printf("Video Visor OK\n");
        GLib.stdout.flush();
        }
}


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
