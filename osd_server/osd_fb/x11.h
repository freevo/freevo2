#ifndef _FREEVO_X11_H_
#define _FREEVO_X11_H_

#include "portable.h"

extern int x11_open (int width, int height);
extern int x11_close (void);
extern void x11_clearscreen (uint32 color);
extern void x11_setpixel (int x, int y, uint32 color);
extern void x11_flush (void);

#endif /* _FREEVO_X11_H_ */
