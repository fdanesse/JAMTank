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

    //private Group group;
    private Protagonista jugador;

    // Eventos.
    private bool izquierda = false;
    private bool derecha = false;
    private bool arriba = false;
    private bool abajo = false;

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
        this.jugador = new Protagonista(path, this.virtual_screen);

        //this.group = new Group();
        //this.group.agregar(this.jugador);
        }

    public void press(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla presionada.
        */
        // Izquierda o derecha.
        if (event.keyval == 97){
            this.derecha = false;
            this.izquierda = true;
            }
        else if (event.keyval == 100){
            this.izquierda = false;
            this.derecha = true;
            }
        // Arriba o abajo
        if (event.keyval == 119){
            this.abajo = false;
            this.arriba = true;
            }
        else if (event.keyval == 115){
            this.arriba = false;
            this.abajo = true;
            }
        }

    public void release(Gdk.EventKey event){
        /*
        Gestiona los eventos de tecla que deja de estar presionada.
        */
        if (event.keyval == 97){
            this.izquierda = false;
            }
        else if (event.keyval == 100){
            this.derecha = false;
            }
        else if (event.keyval == 119){
            this.arriba = false;
            }
        else if (event.keyval == 115){
            this.abajo = false;
            }
        }

    public void resize(int w, int h){
        /*
        Reescalado de la ventana principal de SDL.
        */
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
        this.jugador.draw(this.virtual_screen);
        //this.group.draw(this.virtual_screen);
        //spriteManager.Render(screen);
        // Escalando y dibujando en la ventana real de SDL.
        SDL.Surface result = escalar(this.virtual_screen, this.REAL_WIDTH,
            this.REAL_HEIGHT);
        result.blit(this.real_rect, this.real_screen, this.real_rect);
        this.real_screen.flip();
        }

    private void process_events () {
        this.jugador.update(this.izquierda, this.derecha, this.arriba, this.abajo);
        SDL.Event.pump();
        }
}
