/*
 * jpeg.c - reads a JPEG bitmap to memory from a file.
 *
 * $Id$
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <jpeglib.h>

#include "portable.h"


/* Do a 3->4 bytes/pixel copy of a scanline */
static void
copy_scanline (uint8 *pSrc, uint8 *pDst, int numpixels)
{
   int i;


   for (i = 0; i < numpixels; i++) {
      pDst[i*4+0] = pSrc[i*3+0];
      pDst[i*4+1] = pSrc[i*3+1];
      pDst[i*4+2] = pSrc[i*3+2];
      pDst[i*4+3] = 0;
   }
   
}



/* Reads a JPEG file into a memory area that is allocated by this function.
 * The data is written as 32-bit RGBA, with A set to 0 for no transparency.
 */
uint8 *
jpeg_readbitmap (FILE *fp, uint16 *pWidth, uint16 *pHeight)
{
    struct jpeg_decompress_struct cinfo;
    struct jpeg_error_mgr jerr;
    uint8 *pBitmap;
    int i;
    uint8 tmp[2048*3];
    

    cinfo.err = jpeg_std_error (&jerr);
    
    jpeg_create_decompress (&cinfo);
    
    jpeg_stdio_src (&cinfo, fp);
    
    jpeg_read_header (&cinfo, TRUE);
    
    /* Set params */
    cinfo.out_color_space = JCS_RGB;
    
    jpeg_start_decompress (&cinfo);

    /* Output bitmap */
    pBitmap = (uint8 *) malloc (cinfo.output_width * cinfo.output_height * 4);
    *pWidth = cinfo.output_width;
    *pHeight = cinfo.output_height;

    printf ("Reading JPEG bitmap, %dx%d\n", *pWidth, *pHeight);
    
    if (!pBitmap) {
       fprintf (stderr, "malloc() error!\n");
       exit (1);
    }

    /* Read the scanlines into the buffer */
    for (i = 0; i < cinfo.output_height; i++) {

       printf ("Copy scanline %d\n", i+1);
       jpeg_read_scanlines (&cinfo, (JSAMPROW *) &tmp, 1); 

       /* copy_scanline (tmp, &(pBitmap[i * cinfo.output_width * 4]),
          cinfo.output_width); */
       
    }

    /* Done */
    /*  jpeg_finish_decompress(&cinfo); */
    jpeg_destroy_decompress (&cinfo); 
    /*  fclose (fp); XXX FIXME! */

    return (pBitmap);
}
