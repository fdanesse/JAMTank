
using SDL;
using SDLImage;


public class Sprite : GLib.Object {

    private SDL.Surface imagen;
    private SDL.Rect image_rect;
    private SDL.Rect pos_rect;
    private SDL.Rect ventana_rect;
    private const int16 velocidad = 5;

    public Sprite(string file, SDL.Screen screen) {
        this.imagen = SDLImage.load(file);
        this.imagen = escalar(this.imagen, 50, 43);
        this.imagen.get_cliprect(out this.image_rect);
        screen.get_cliprect(out this.ventana_rect);
        this.pos_rect.x = this.ventana_rect.w / 2 - this.image_rect.w / 2;
        this.pos_rect.y = this.ventana_rect.h / 2 - this.image_rect.h / 2;
        this.pos_rect.w = this.image_rect.w;
        this.pos_rect.h = this.image_rect.h;
        }

    public void derecha() {
        if (this.ventana_rect.w - this.pos_rect.w >= this.pos_rect.x + 5)
            this.pos_rect.x = this.pos_rect.x + 5;
        }

    public void izquierda() {
        if (this.pos_rect.x - 5 >= 0)
            this.pos_rect.x = this.pos_rect.x - 5;
        }

    public void arriba() {
        if (this.pos_rect.y - 5 >= 0)
            this.pos_rect.y = this.pos_rect.y - 5;
        }

    public void abajo() {
        if (this.ventana_rect.h - this.pos_rect.h >= this.pos_rect.y + 5)
            this.pos_rect.y = this.pos_rect.y + 5;
        }

    public void draw(SDL.Surface surface) {
        SDL.Rect surface_rect;
        surface.get_cliprect(out surface_rect);
        this.imagen.blit(this.image_rect, surface, this.pos_rect);
        }
}
