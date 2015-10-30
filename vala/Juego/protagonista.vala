using SDL;
using SDLImage;


public class Protagonista : GLib.Object {

    private SDL.Surface original_imagen;
    private SDL.Surface imagen;
    private SDL.Rect image_rect;
    private SDL.Rect pos_rect;
    private SDL.Rect ventana_rect;
    private const int16 velocidad = 10;
    private const int rotacion = 5;
    private double angulo = 0;
    private int16 dx = 0;
    private int16 dy = 0;

    public Protagonista(string file, SDL.Surface screen) {
        this.original_imagen = SDLImage.load(file);
        this.original_imagen = escalar(this.original_imagen, 50, 50);
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
            this.__adelante();
            this.__derecha();
            }
        else if (arriba & izquierda){
            this.__adelante();
            this.__izquierda();
            }
        else if (abajo & derecha){
            this.__atras();
            this.__izquierda();
            }
        else if (abajo & izquierda){
            this.__atras();
            this.__derecha();
            }

        // moverse sin girar
        else if (arriba){
            this.__adelante();
            }
        else if (abajo){
            this.__atras();
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
        this.angulo -= (double)(0.7 * rotacion);
        if (this.angulo <= -360)
            this.angulo += 360;
        this.imagen = SDLGraphics.RotoZoom.rotozoom (this.original_imagen,
            this.angulo, 1.0, 32);
        this.imagen.get_cliprect(out this.image_rect);
        }

    private void __izquierda() {
        this.angulo += (double)(0.7 * rotacion);
        if (this.angulo >= 360)
            this.angulo -= 360;
        this.imagen = SDLGraphics.RotoZoom.rotozoom (this.original_imagen,
            this.angulo, 1.0, 32);
        this.imagen.get_cliprect(out this.image_rect);
        }

    private void __adelante() {
        this.__get_vector();
        this.pos_rect.x += (int16)(this.dx);
        this.pos_rect.y += (int16)(this.dy);
        }

    private void __atras() {
        this.__get_vector();
        this.pos_rect.x += (int16)(this.dx * -1);
        this.pos_rect.y += (int16)(this.dy * -1);
        }

    private void __get_vector(){
        float cos;
        float sin;
        double rad = this.angulo * GLib.Math.PI / 180.0;
        GLib.Math.sincosf((float)rad, out sin, out cos);
        this.dx = (int16)(cos * (float)velocidad);
        this.dy = (int16)(sin * (float)velocidad) * -1; // *-1 porque los angulos van al revés en SDL.
        }

    public void draw(SDL.Surface surface) {
        SDL.Rect surface_rect;
        surface.get_cliprect(out surface_rect);
        this.pos_rect.w = this.image_rect.w;
        this.pos_rect.h = this.image_rect.h;
        this.imagen.blit(this.image_rect, surface, this.pos_rect);
        }
}
