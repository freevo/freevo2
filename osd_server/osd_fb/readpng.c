#include <png.h>
#include <stdlib.h>

#include "readpng.h"
#include "portable.h"


/* Returns OK or ERROR */
int read_png (char *file_name, uint32 **ppBitmap,
              uint16 *pWidth, uint16 *pHeight) 
{
   png_structp png_ptr;
   png_infop info_ptr;
   png_uint_32 width, height;
   int bit_depth, color_type;
   FILE *fp;
   int png_transforms;
   int channels;
   int rowbytes;
   png_bytep *row_pointers;
   int i;
   uint32 *pTmp;
   
   
   if ((fp = fopen (file_name, "r")) == NULL)
      return (ERROR);

   /* Create and initialize the png_struct with the desired error handler
    * functions.  If you want to use the default stderr and longjump method,
    * you can supply NULL for the last three parameters.  We also supply the
    * the compiler header file version, so that we know if the application
    * was compiled with a compatible version of the library.  REQUIRED
    */
   png_ptr = png_create_read_struct (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);

   if (png_ptr == NULL) {
      fclose (fp);
      return (ERROR);
   }

   /* Allocate/initialize the memory for image information.  REQUIRED. */
   info_ptr = png_create_info_struct (png_ptr);
   if (info_ptr == NULL) {
      fclose(fp);
      png_destroy_read_struct (&png_ptr, NULL, NULL);
      return (ERROR);
   }
   
   /* Set error handling if you are using the setjmp/longjmp method (this is
    * the normal method of doing things with libpng).  REQUIRED unless you
    * set up your own error handlers in the png_create_read_struct() earlier.
    */
   if (setjmp (png_jmpbuf (png_ptr))) {
      /* Free all of the memory associated with the png_ptr and info_ptr */
      png_destroy_read_struct (&png_ptr, &info_ptr, NULL);
      fclose (fp);
      /* If we get here, we had a problem reading the file */
      return (ERROR);
   }

   /* Set up the input control for standard C streams */
   png_init_io (png_ptr, fp);

   /*
    * Read the entire image into the info structure
    */
   png_transforms = PNG_TRANSFORM_PACKING;
   png_read_png (png_ptr, info_ptr, png_transforms, NULL);

   channels = png_get_channels (png_ptr, info_ptr);
   rowbytes = png_get_rowbytes(png_ptr, info_ptr);
   width = png_get_image_width (png_ptr, info_ptr);
   height = png_get_image_height (png_ptr, info_ptr);
   bit_depth = png_get_bit_depth(png_ptr, info_ptr);
   color_type = png_get_color_type (png_ptr, info_ptr);

   /* XXX Add checking that we have a 32-bit RGBA image! */
   /* color_type == PNG_COLOR_TYPE_RGBA
    * bit_depth = 8
    * channels = 4
    */
   printf ("%dx%d\n", (int) width, (int) height);
   row_pointers = png_get_rows (png_ptr, info_ptr);

   /* Copy image to a malloc()'ed buffer that is free()'d by the
    * caller */
   pTmp = (uint32 *) malloc (width*4*height);

   printf ("Storing at %p\n", pTmp);
   
   for (i = 0; i < height; i++) {
      uint32 *src, *dst;
      
      
      dst = &(pTmp[i*width]);
      src = (uint32 *) row_pointers[i];

      memcpy (dst, src, width*4);
   }
   
   /* clean up after the read, and free any memory allocated - REQUIRED */
   png_destroy_read_struct(&png_ptr, &info_ptr, NULL);

   /* close the file */
   fclose(fp);

   /* Output parameters */
   *ppBitmap = pTmp;
   *pWidth = width;
   *pHeight = height;
   
   /* that's it */
   return (OK);
}


#ifdef PNGTEST
int
main (int ac, char *av[])
{
   uint32 *pBitmap;
   uint16 w, h;
   
   
   read_png (av[1], &pBitmap, &w, &h);

   return (0);
   
}
#endif /* PNGTEST */

