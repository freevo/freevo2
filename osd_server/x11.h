#ifndef _FREEVO_X11_H_
#define _FREEVO_X11_H_

#include "portable.h"

extern int x11_open (int width, int height);
extern void x11_close (void);
extern void x11_update (uint8 *pFB);
extern void x11_pollevents (void);

#endif /* _FREEVO_X11_H_ */
