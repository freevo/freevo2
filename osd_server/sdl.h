#ifndef _FREEVO_SDL_H_
#define _FREEVO_SDL_H_

#include "portable.h"

// Function Prototypes
int sdl_open (int, int);
void sdl_close (void);
void sdl_update (uint8 *);
void sdl_pollevents (void);

#endif /* _FREEVO_SDL_H_ */
