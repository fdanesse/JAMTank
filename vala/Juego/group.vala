using SDL;
using Gee;


public class Group : GLib.Object {

    private Gee.ArrayList<Sprite> sprites;

    public Group() {
        this.sprites = new Gee.ArrayList<Sprite>(direct_equal);
        }

    public void agregar(Sprite sprite) {
        this.sprites.add(sprite);
        }

    public void quitar(Sprite sprite) {
        //this.sprites.add(sprite);
        }

    //public void update() {
    //    Iterator<Sprite> iter = this.sprites.iterator();
    //    while(iter.next())
    //        iter.get().update();
    //    }

    public void draw(SDL.Surface surface) {
        Gee.Iterator<Sprite> iter = this.sprites.iterator();
        while(iter.next())
            iter.get().draw(surface);
        }
}
