#include <png.h>
#include <stdlib.h>

#include "readpng.h"
#include "portable.h"


/* Returns OK or ERROR */
int read_png (char *file_name, uint8 **ppBitmap,
              uint16 *pWidth, uint16 *pHeight) 
{
   png_structp png_ptr;
   png_infop info_ptr;
   png_uint_32 width, height;
   int bit_depth, color_type;
   FILE *fp;
   int channels;
   int rowbytes;
   uint8 *pTmp;
   double screen_gamma;
   int intent;
   int interlace_type;
   
   
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

   /* The call to png_read_info() gives us all of the information from the
    * PNG file before the first IDAT (image data chunk).  REQUIRED
    */
   png_read_info (png_ptr, info_ptr);

   png_get_IHDR (png_ptr, info_ptr, &width, &height, &bit_depth, &color_type,
                 &interlace_type, NULL, NULL);

   printf ("Got colortype %d\n", color_type);

   /* tell libpng to strip 16 bit/color files down to 8 bits/color */
   if (bit_depth == 16) {
      png_set_strip_16 (png_ptr);
   }

   /* Change opacity to transparency */
   png_set_invert_alpha (png_ptr);

   /* Extract multiple pixels with bit depths of 1, 2, and 4 from a single
    * byte into separate bytes (useful for paletted and grayscale images).
    */
   if (bit_depth < 8) {
      png_set_packing (png_ptr);
   }

   if ((color_type == PNG_COLOR_TYPE_PALETTE) && (bit_depth <= 8)) {
      png_set_expand (png_ptr);
   }

   if ((color_type == PNG_COLOR_TYPE_GRAY) && (bit_depth < 8)) {
      png_set_expand (png_ptr);
   }

   if (png_get_valid (png_ptr, info_ptr, PNG_INFO_tRNS)) {
      png_set_expand (png_ptr);
   }
   
   /* Expand grayscale images to the full 8 bits from 1, 2, or 4 bits/pixel */
   if ((color_type == PNG_COLOR_TYPE_GRAY) && (bit_depth < 8)) {
      png_set_gray_1_2_4_to_8 (png_ptr);
   }

   /* Expand paletted or RGB images with transparency to full alpha channels
    * so the data will be available as RGBA quartets.
    */
   if (png_get_valid (png_ptr, info_ptr, PNG_INFO_tRNS)) {
      png_set_tRNS_to_alpha (png_ptr);
   }
   
   png_set_bgr(png_ptr);
   
    screen_gamma = 2.2;  /* A good guess for a PC monitors in a dimly
                           lit room */

   /* Tell libpng to handle the gamma conversion for you.  The final call
    * is a good guess for PC generated images, but it should be configurable
    * by the user at run time by the user.  It is strongly suggested that
    * your application support gamma correction.
    */

   if (png_get_sRGB (png_ptr, info_ptr, &intent)) {
      png_set_gamma (png_ptr, screen_gamma, 0.45455);
   } else {
      double image_gamma;
      
      if (png_get_gAMA (png_ptr, info_ptr, &image_gamma))
         png_set_gamma (png_ptr, screen_gamma, image_gamma);
      else
         png_set_gamma (png_ptr, screen_gamma, 0.45455);
   }
   
   /* swap the RGBA or GA data to ARGB or AG (or BGRA to ABGR) */
   /*  png_set_swap_alpha (png_ptr); */

   /* Add filler (or alpha) byte (before/after each RGB triplet) */
   png_set_filler (png_ptr, 0x00, PNG_FILLER_AFTER);
   
   if ((color_type == PNG_COLOR_TYPE_GRAY) ||
       (color_type == PNG_COLOR_TYPE_GRAY_ALPHA)) {
      png_set_gray_to_rgb (png_ptr);
   }

   /* Optional call to gamma correct and add the background to the palette
    * and update info structure.  REQUIRED if you are expecting libpng to
    * update the palette for you (ie you selected such a transform above).
    */
   png_read_update_info (png_ptr, info_ptr);
   
   channels = png_get_channels (png_ptr, info_ptr);
   rowbytes = png_get_rowbytes (png_ptr, info_ptr);
   width = png_get_image_width (png_ptr, info_ptr);
   height = png_get_image_height (png_ptr, info_ptr);
   bit_depth = png_get_bit_depth (png_ptr, info_ptr);
   color_type = png_get_color_type (png_ptr, info_ptr);
   
   /* XXX Add checking that we really have got a 32-bit ARGB image! */
   /* color_type == PNG_COLOR_TYPE_RGBA
    * bit_depth = 8
    * channels = 4
    */
   printf ("Got colortype %d\n", color_type);
   printf ("%dx%d %d bits %d channels %d rowbytes\n", (int) width, (int) height,
           bit_depth, channels, rowbytes);

   /* Allocate the memory to hold the image using the fields of info_ptr. */
   /* The image is copied to a malloc()'ed buffer that is free()'d by the
    * caller */
   pTmp = (uint8 *) malloc (width*4 * height);
   
   {
      int row;

      
      png_bytep row_pointers[height];
      
      for (row = 0; row < height; row++) {
         row_pointers[row] = &(pTmp[row * width*4]);
      }
      
      /* Read the entire image in one go */
      png_read_image(png_ptr, row_pointers);
      
      /* read rest of file, and get additional chunks in info_ptr - REQUIRED */
      png_read_end (png_ptr, info_ptr);

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
   uint32 *pBitmap, val;
   uint16 w, h;
   int r, c;
   
   
   read_png (av[1], (uint8 **) &pBitmap, &w, &h);

   for (r = 0; r < h; r++) {
      for (c = 0; c < w; c++) {
         val = pBitmap[r*w+c];
         printf ("%3d %3d  0x%08x\n", c, r, val);
      }
   }

   return (0);
   
}
#endif /* PNGTEST */

