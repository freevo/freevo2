/*
    Copyright (C) 2002 Jeremy Madea <jeremymadea@mindspring.com>

    This file is part of jpgtn.

    Jpgtn is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

    Jpgtn is based on two programs: tnpic (distributed with zgv) and gtnpic.
    The original "gtnpic" program was Copyright (C) 1997      Willie Daniel. 
    The original "tnpic"  program was Copyright (C) 1993-1996 Russell Marks.
    Both tnpic and gtnpic were distributed under the GNU Public License. 
*/

#include <stdio.h>
#include <stdlib.h>
#include <setjmp.h>
#include <jpeglib.h>
#include "readjpeg.h"


struct my_error_mgr {
    struct jpeg_error_mgr pub;  /* "public" fields      */
    jmp_buf setjmp_buffer;      /* for return to caller */
};
typedef struct my_error_mgr * my_error_ptr;


static void my_error_exit(j_common_ptr cinfo)
{
    my_error_ptr myerr=(my_error_ptr) cinfo->err;
    char buf[JMSG_LENGTH_MAX];

    
    printf ("error, %s:%d\n", __FILE__, __LINE__);
    
    (*cinfo->err->format_message)(cinfo,buf);
    longjmp(myerr->setjmp_buffer, 1);
}


int read_jpeg (char *file_name, uint8 **ppBitmap,
               uint16 *pWidth, uint16 *pHeight)
{
    FILE *infile;
    struct jpeg_decompress_struct cinfo;
    struct my_error_mgr jerr;
    int row_stride;
    unsigned char *image;
    unsigned char *pal;
    int f;
    unsigned char *ptr;
    int width, height;
    int i;
    uint8 r, g, b, col;
    uint8 *pTmp;

    
    image = NULL;

    if (((pal) = (unsigned char *)calloc(1,768))==NULL) {
       printf ("error, %s:%d\n", __FILE__, __LINE__);
        return(ERROR);
    }

    if (NULL == (infile = fopen (file_name, "r"))) {
       printf ("error, %s:%d\n", __FILE__, __LINE__);
        return(ERROR);
    }

    cinfo.err = jpeg_std_error(&jerr.pub);
    jerr.pub.error_exit = my_error_exit;

    if (setjmp(jerr.setjmp_buffer)) {
       printf ("error, %s:%d\n", __FILE__, __LINE__);
        jpeg_destroy_decompress(&cinfo);
        fclose(infile);
        free(pal);
        return(ERROR);
    }

    /* Now we can initialize the JPEG decompression object. */
    jpeg_create_decompress(&cinfo);

    jpeg_stdio_src(&cinfo,infile);

    jpeg_read_header(&cinfo,TRUE);

    /* setup parameters for decompression */
    cinfo.dct_method=JDCT_ISLOW;
    cinfo.quantize_colors=TRUE;
    cinfo.desired_number_of_colors=256;
    cinfo.two_pass_quantize=TRUE;

    /* Fix to greys if greyscale. (required to read greyscale JPEGs) */
    if (cinfo.jpeg_color_space == JCS_GRAYSCALE) {

        cinfo.out_color_space = JCS_GRAYSCALE;
        cinfo.desired_number_of_colors = 256;
        cinfo.quantize_colors = FALSE;
        cinfo.two_pass_quantize = FALSE;

        for(f=0;f<256;f++) { 
            pal[f]=pal[256+f]=pal[512+f]=f;
        }
    }

    width = cinfo.image_width;
    height = cinfo.image_height;
    image = (unsigned char *)calloc(1,width*height);

    if (image==NULL) {
       printf ("error, %s:%d\n", __FILE__, __LINE__);
        printf("Out of memory\n");
        longjmp(jerr.setjmp_buffer,1);
    }

    jpeg_start_decompress(&cinfo);

    /* read the palette (if greyscale, this has already been done) */
    if (cinfo.jpeg_color_space != JCS_GRAYSCALE) {

        for (f=0; f<cinfo.actual_number_of_colors; f++) {
            pal[    f]=cinfo.colormap[0][f];
            pal[256+f]=cinfo.colormap[1][f];
            pal[512+f]=cinfo.colormap[2][f];
        }
    }

    ptr = image; 
    row_stride = width;

    /* read the image */
    while (cinfo.output_scanline < height) {
        jpeg_read_scanlines (&cinfo, &ptr, 1);
        ptr += row_stride;
    }

    jpeg_finish_decompress (&cinfo);
    jpeg_destroy_decompress (&cinfo);
    fclose (infile);

    /* The image is copied to a malloc()'ed buffer that is free()'d by the
     * caller */
    pTmp = (uint8 *) malloc (width*4 * height);
    
    for (i = 0; i < (width*height); i++) {
       col = image[i];
       r = pal[col];
       g = pal[col+256];
       b = pal[col+512];
       pTmp[i*4 + 0] = b;
       pTmp[i*4 + 1] = g;
       pTmp[i*4 + 2] = r;
       pTmp[i*4 + 3] = 0;
    }

    free (pal);
    free (image);
    
    /* Output parameters */
    *ppBitmap = pTmp;
    *pWidth = width;
    *pHeight = height;
    
    return (OK);
}
