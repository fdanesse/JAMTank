using SDL;
using SDLGraphics;


public SDL.Surface escalar(SDL.Surface imagen, float w, float h){
    SDL.Surface retorno;
    SDL.Rect rect;
    imagen.get_cliprect(out rect);
    float ww = w / (float)rect.w;
    float hh = h / (float)rect.h;
    retorno = SDLGraphics.RotoZoom.zoom(imagen, ww, hh, 32);
    //GLib.stdout.printf("%f-%f\n", ww, hh);
    //GLib.stdout.flush();
    return retorno;
    }
