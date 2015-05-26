// valac --pkg gee-1.0 --pkg sdl --pkg sdl-image --pkg sdl-gfx -X -lSDL_gfx -X -lSDL_image -o juego
// juego.vala sprite.vala globales.vala

using SDL;
using SDLImage;
using SDLGraphics;
using Gee;


public class Juego : GLib.Object {

    private const uint32 video_flags = SDL.SurfaceFlag.DOUBLEBUF |
        SDL.SurfaceFlag.HWACCEL | SDL.SurfaceFlag.HWSURFACE;

    //Superficie virtual de dibujo a 640x480.
    private const int VIRTUAL_WIDTH = 640;
    private const int VIRTUAL_HEIGHT = 480;
    private SDL.Surface virtual_screen;
    private SDL.Rect virtual_rect;

    //Ventana real de SDL que escala el dibujo dinámicamente.
    private int REAL_WIDTH = 640;
    private int REAL_HEIGHT = 480;
    private weak SDL.Screen real_screen;
    private SDL.Rect real_rect;

    private const int SCREEN_BPP = 32;

    private SDL.Surface fondo;
    public bool running = true;
    public bool paused = false;

    private Group group;
    private Sprite jugador;

    public Juego () {
        // Ventana real de SDL escalable dinámicamente.
        this.real_screen = SDL.Screen.set_video_mode (REAL_WIDTH,
            REAL_HEIGHT, SCREEN_BPP, video_flags);
        this.real_screen.get_cliprect(out this.real_rect);
        SDL.WindowManager.set_caption("Juego vala", "");

        // Fondo del escenario.
        string path = "/home/flavio/Documentos/JAMTank/vala/Juego/Mapas/fondo1.png";
        this.fondo = SDLImage.load(path);
        this.fondo = escalar(this.fondo, VIRTUAL_WIDTH, VIRTUAL_HEIGHT);

        // Superficie Virtual de dibujo.
        this.virtual_screen = escalar(this.fondo, VIRTUAL_WIDTH, VIRTUAL_HEIGHT);
        this.virtual_screen.get_cliprect(out this.virtual_rect);

        // Protagonista.
        path = "/home/flavio/Documentos/JAMTank/vala/Juego/Tanques/tanque-4.png";
        this.jugador = new Sprite(path, this.virtual_screen);

        this.group = new Group();
        this.group.agregar(this.jugador);
        }

    public void resize(int w, int h){
        this.REAL_WIDTH = w;
        this.REAL_HEIGHT = h;
        this.real_screen = SDL.Screen.set_video_mode (REAL_WIDTH,
            REAL_HEIGHT, SCREEN_BPP, video_flags);
        this.real_screen.get_cliprect(out this.real_rect);
        }

    public bool run () {
        if (this.paused == true){
            return this.running;
            }
        while (Gtk.events_pending()){
            Gtk.main_iteration();
            }
        //this.real_screen.fill(null, this.real_screen.format.map_rgb(0, 0, 0));
        this.process_events();
        //this.update();
        this.draw();
        return this.running;
        }

    private void draw () {
        // Dibujando en superficie virtual de 640x480
        this.fondo.blit(this.virtual_rect, this.virtual_screen, this.virtual_rect);
        this.group.draw(this.virtual_screen);
        //spriteManager.Render(screen);
        // Escalando y dibujando en la ventana real de SDL.
        SDL.Surface result = escalar(this.virtual_screen, this.REAL_WIDTH,
            this.REAL_HEIGHT);
        result.blit(this.real_rect, this.real_screen, this.real_rect);
        this.real_screen.flip();
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
