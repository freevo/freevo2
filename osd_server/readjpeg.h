#ifndef _INC_READJPEG_H_
#define _INC_READJPEG_H_

#include "portable.h"

/* Returns OK or ERROR */
extern int read_jpeg (char *file_name, uint8 **ppBitmap,
                      uint16 *pWidth, uint16 *pHeight);

#endif /* _INC_READJPEG_H_ */
