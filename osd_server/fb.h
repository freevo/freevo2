#ifndef _FREEVO_FB_H_
#define _FREEVO_FB_H_

#include "portable.h"

extern int fb_open (void);
extern int fb_close (void);
extern void fb_update (uint8 *pFB);

#endif /* _FREEVO_FB_H_ */
