#ifndef _INC_READPNG_H_
#define _INC_READPNG_H_

#include <png.h>

#include "portable.h"

/* Backwards compatibility */
#ifndef png_jmpbuf
#  define png_jmpbuf(png_ptr) ((png_ptr)->jmpbuf)
#endif

/* Returns OK or ERROR */
extern int read_png (char *file_name, uint8 **ppBitmap,
                     uint16 *pWidth, uint16 *pHeight);

#endif /* _INC_READPNG_H_ */
