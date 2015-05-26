
using SDL;
using SDLImage;


public class Protagonista : GLib.Object {

    private SDL.Surface imagen;
    private SDL.Rect image_rect;
    private SDL.Rect pos_rect;
    private SDL.Rect ventana_rect;
    private const int16 velocidad = 10;

    public Protagonista(string file, SDL.Surface screen) {
        this.imagen = SDLImage.load(file);
        this.imagen = escalar(this.imagen, 50, 50);
        this.imagen.get_cliprect(out this.image_rect);
        screen.get_cliprect(out this.ventana_rect);
        this.pos_rect.x = this.ventana_rect.w / 2 - this.image_rect.w / 2;
        this.pos_rect.y = this.ventana_rect.h / 2 - this.image_rect.h / 2;
        this.pos_rect.w = this.image_rect.w;
        this.pos_rect.h = this.image_rect.h;
        }

    public void update(bool izquierda, bool derecha, bool arriba, bool abajo){
        // girar en movimiento
        if (arriba & derecha){
            this.__arriba();
            this.__derecha();
            }
        else if (arriba & izquierda){
            this.__arriba();
            this.__izquierda();
            }
        else if (abajo & derecha){
            this.__abajo();
            this.__izquierda();
            }
        else if (abajo & izquierda){
            this.__abajo();
            this.__derecha();
            }

        // moverse sin girar
        else if (arriba){
            this.__arriba();
            }
        else if (abajo){
            this.__abajo();
            }

        // girar sin moverse
        else if (derecha){
            this.__derecha();
            }
        else if (izquierda){
            this.__izquierda();
            }
        }

    private void __derecha() {
        if (this.ventana_rect.w - this.pos_rect.w >= this.pos_rect.x + velocidad)
            this.pos_rect.x = this.pos_rect.x + velocidad;
        }

    private void __izquierda() {
        if (this.pos_rect.x - velocidad >= 0)
            this.pos_rect.x = this.pos_rect.x - velocidad;
        }

    private void __arriba() {
        if (this.pos_rect.y - velocidad >= 0)
            this.pos_rect.y = this.pos_rect.y - velocidad;
        }

    private void __abajo() {
        if (this.ventana_rect.h - this.pos_rect.h >= this.pos_rect.y + velocidad)
            this.pos_rect.y = this.pos_rect.y + velocidad;
        }

    public void draw(SDL.Surface surface) {
        SDL.Rect surface_rect;
        surface.get_cliprect(out surface_rect);
        this.imagen.blit(this.image_rect, surface, this.pos_rect);
        }
}
