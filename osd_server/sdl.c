#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>

#include <SDL/SDL.h>
#include "sdl.h"

static SDL_Surface *screen, *image;
static int xres, yres;


int
sdl_open (int width, int height)
{
   int MODEFLAGS;
   xres = width;
   yres = height;
   
   /* Initialize defaults, Video Only */
   if((SDL_Init(SDL_INIT_VIDEO))==-1) {
   	printf("Could not Initializse SDL: %s\n.", SDL_GetError());
   	exit(-1);
   }

   printf ("SDL Initialized\n");


   /*
    *  Setup Visuals.  Freevo x11 tries for a 24 bit visual, not so sure about that
    *  given the performance impact of 24 bit visuals, but...
    *
    *  Use Double Buffering to reduce the 'flicker' seen in other modes.
    *
    */
   MODEFLAGS = SDL_SWSURFACE;

#ifdef xSDL_FULLSCREEN
   MODEFLAGS = MODEFLAGS | SDL_FULLSCREEN;
#endif

   screen = SDL_SetVideoMode(xres, yres, 32, MODEFLAGS);
   if(screen == NULL) {
   	fprintf(stderr, "Couldn't set %dx%dx32 video mode: %s\n", xres, yres, SDL_GetError());
	fprintf(stderr, "Attempting 24 bit mode\n");

	screen = SDL_SetVideoMode(xres, yres, 24, MODEFLAGS);
	if(screen == NULL) {
		fprintf(stderr, "Couldn't set %dx%dx24 video mode: %s\n", xres, yres, SDL_GetError());
		exit(1);
	}
   }

   return (0);
}

void
sdl_update (uint8 *pFB)
{
   int R;
   int G;
   int B;
   int A;

   //
   // Set byte order.  Set the Alpha mask to 0 as we don't want any alpha blending
   //
   if(SDL_BYTEORDER == SDL_LIL_ENDIAN) {
	R = 0x00ff0000;
	G = 0x0000ff00;
	B = 0x000000ff;
	A = 0x00000000;
   } else {
 	R = 0x000000ff;
	G = 0x0000ff00;
	B = 0x00ff0000;
	A = 0x00000000;
   }
	
   image = SDL_CreateRGBSurfaceFrom(pFB, xres, yres, 32, xres*4, R, G, B, A);

   if(SDL_BlitSurface(image, NULL, screen, NULL) < 0) 
   	fprintf(stderr, "BlitSurface Error: %s\n", SDL_GetError());
   
   SDL_Flip(screen);

   SDL_FreeSurface(image);
}

void 
sdl_pollevents(void)
{
    SDL_Event event;

    while(SDL_PollEvent(&event)) 
    {
	// Handle events
	switch(event.type) {
		case SDL_ACTIVEEVENT:
			SDL_UpdateRect(screen, 0, 0, xres, yres);
			break;

		default:
	}
    }
}

void
sdl_close (void)
{
    SDL_Quit();
}

void sdl_clear(void)
{
		SDL_FillRect (screen, NULL, SDL_MapRGB (screen->format, 0, 0, 0));
		SDL_Flip(screen);
}


#ifdef TEST
int
main (int ac, char *av[])
{
   
   
   printf ("open()\n");
   sdl_open (768, 576);

   printf ("\nPress a <CR> to exit!\n");
   
   getchar ();
   
   sdl_close ();

   return (0);
   
}
#endif /* TEST */


