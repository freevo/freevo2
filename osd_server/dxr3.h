#ifndef _FREEVO_DXR3_H_
#define _FREEVO_DXR3_H_

#include "portable.h"

extern int dxr3_open (int width, int height);
extern void dxr3_close (void);
extern void dxr3_update (uint8 *pFB);

#endif /* _FREEVO_DXR3_H_ */
