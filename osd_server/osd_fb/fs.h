#ifndef _FREEVO_FS_H
#define _FREEVO_FS_H

#include "portable.h"

/*
 * bbox    = width, height, x, y
 * ascent  = bbox.height - bbox.y
 * descent = -bbox.y
 * left    = bbox.x
 * right   = bbox.width + bbox.x
 */

typedef struct {
   /* width = DWIDTH from BDF */
   int32 dwidth;
   int32 width, height, x, y;
   uint8 *pBitmap;
} fontchar_t;


typedef struct {
   int32 width, height, x, y;
   fontchar_t *pFontchars[256];
} font_t;


int fs_puts (font_t *f, int x, int y, uint32 fgcol, uint32 bgcol,
             unsigned char *str);
font_t *fs_open (char *pattern);

#endif
