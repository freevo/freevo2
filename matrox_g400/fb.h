#ifndef _FREEVO_FB_H_
#define _FREEVO_FB_H_

#include "portable.h"

extern int fb_open (void);
extern int fb_close (void);
extern void fb_clearscreen (uint32 color);
extern void fb_setpixel (uint16 x, uint16 y, uint32 color);
extern uint8 *fb_mem;

#endif /* _FREEVO_FB_H_ */
