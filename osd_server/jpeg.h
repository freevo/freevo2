/*
 * jpeg.h - reads a JPEG bitmap to memory from a file.
 *
 * $Id$
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <jpeglib.h>

#include "portable.h"


/* Reads a JPEG file into a memory area that is allocated by this function.
 * The data is written as 32-bit RGBA, with A set to 0 for no transparency.
 */
uint8 *jpeg_readbitmap (FILE *fp, uint16 *pWidth, uint16 *pHeight);
