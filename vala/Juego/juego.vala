// valac --pkg gee-1.0 --pkg sdl --pkg sdl-image --pkg sdl-gfx -X -lSDL_gfx -X -lSDL_image -o juego
// juego.vala sprite.vala globales.vala

using SDL;
using SDLImage;
using SDLGraphics;
using Gee;


public class Juego : GLib.Object {

    private const int SCREEN_WIDTH = 640;
    private const int SCREEN_HEIGHT = 480;
    private const int SCREEN_BPP = 32;

    private weak SDL.Screen screen;
    private SDL.Rect ventana_rect;

    private SDL.Surface fondo;
    public bool running = true;
    public bool paused = false;

    private Group group;
    private Sprite jugador;

    public Juego () {
        // Ventana
        uint32 video_flags = SDL.SurfaceFlag.DOUBLEBUF |
            SDL.SurfaceFlag.HWACCEL | SDL.SurfaceFlag.HWSURFACE;
        this.screen = SDL.Screen.set_video_mode (SCREEN_WIDTH, SCREEN_HEIGHT,
            SCREEN_BPP, video_flags);
        this.screen.get_cliprect(out this.ventana_rect);
        SDL.WindowManager.set_caption("Juego vala", "");

        // Fondo
        this.fondo = SDLImage.load("/home/flavio/Documentos/JAMTank/vala/Juego/Mapas/fondo1.png");
        this.fondo = escalar(this.fondo, this.ventana_rect.w, this.ventana_rect.h);

        // Sprites
        this.jugador = new Sprite("/home/flavio/Documentos/JAMTank/vala/Juego/Tanques/tanque-4.png", this.screen);

        this.group = new Group();
        this.group.agregar(this.jugador);
        }

    public bool run () {
        if (this.paused == true){
            return this.running;
            }
        while (Gtk.events_pending()){
            Gtk.main_iteration();
            }
        this.screen.fill(null, this.screen.format.map_rgb(0, 0, 0));
        this.process_events();
        //this.update();
        this.draw();
        return this.running;
        }

    private void draw () {
        this.fondo.blit(this.ventana_rect, this.screen, this.ventana_rect);
        this.group.draw(this.screen);
        //spriteManager.Render(screen);
        this.screen.flip();
        }

    private void process_events () {
        SDL.Event event;
        while (SDL.Event.poll (out event) == 1) {
            switch (event.type) {
                case SDL.EventType.QUIT:
                    this.paused = false;
                    this.running = false;
                    break;
                case SDL.EventType.KEYDOWN:
                    //if(event.key.keysym.sym == SDL.KeySymbol.ESCAPE)
                    //    this.running = false;
                    if(event.key.keysym.sym == SDL.KeySymbol.a)
                        this.jugador.izquierda();
                    if(event.key.keysym.sym == SDL.KeySymbol.d)
                        this.jugador.derecha();
                    if(event.key.keysym.sym == SDL.KeySymbol.w)
                        this.jugador.arriba();
                    if(event.key.keysym.sym == SDL.KeySymbol.s)
                        this.jugador.abajo();
                    //if(event.key.keysym.sym == SDL.KeySymbol.SPACE)
                    //    this.estado = false;
                    break;
                }
            }
        SDL.Event.pump();
        }
}
