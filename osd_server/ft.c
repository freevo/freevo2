/* Functions to draw text using the Freetype2 library */

#include <stdio.h>

#include <ft2build.h>
#include FT_FREETYPE_H

#include "portable.h"

#ifdef TEST
static void
osd_setpixel (uint16 x, uint16 y, uint32 color)
{
   /* XXX Later... */
}

#else
#include "osd.h"
#endif

static void
draw_bitmap (FT_Bitmap *pBM, int left, int top, uint32 fgcol)
{
   int x, y;
   uint8 val, fgtransp, tb;
   uint32 col, fgalpha;
   

   /*  printf ("bitmap: %dx%d\n", pBM->width, pBM->rows); */
           
   fgtransp = fgcol >> 24;
   fgalpha = 256 - fgtransp;
   fgcol &= 0x00ffffff;
   
   for (y = 0; y < pBM->rows; y++) {
      for (x = 0; x < pBM->width; x++) {

         val = pBM->buffer[y*pBM->pitch+x];

         /* Set the foreground color */
         if (val) {
            tb = 255 - (((uint32) val * fgalpha) >> 8);
            col = (tb << 24) | fgcol;
            osd_setpixel (left+x, top+y, col);
         }
      }
   }
         
}



int
ft_puts (char *pFontFilename, int ptsize, int x, int y,
         uint32 fgcol, unsigned char *str)
{
   static FT_Library  library;
   FT_Face      face;      /* handle to face object */
   int error;
   int i;
   int pen_x = x, pen_y = y;
   FT_GlyphSlot slot;
   static int init = 0;
   

   if (!init) {
      error = FT_Init_FreeType (&library);
      
      if (error) {
         fprintf (stderr, "Couldn't initialize the library\n");
         exit (1);
      }

      init = 1;
   }

   error = FT_New_Face (library, pFontFilename, 0, &face );
   if (error == FT_Err_Unknown_File_Format) {
      fprintf (stderr, "%s: unknown format\n", pFontFilename);
      exit (1);
   } else if (error) {
      fprintf (stderr, "%s: couldn't open file\n", pFontFilename);
      exit (1);
   }

#ifdef TEST
   printf ("opened font %s\n", pFontFilename);
   printf ("num glyphs = %d\n", (int) face->num_glyphs);
   printf ("flags = 0x%x\n", (int) face->face_flags);
   printf ("units_per_EM = %d\n", (int) face->units_per_EM);
   printf ("num_fixed_sizes = %d\n", (int) face->num_fixed_sizes);
#endif
   
   error = FT_Set_Char_Size (face,    /* handle to face object           */
                             0,       /* char_width in 1/64th of points  */
                             ptsize*64,   /* char_height in 1/64th of points */
                             100,     /* horizontal device resolution    */
                             100);   /* vertical device resolution      */

   if (error) {
      fprintf (stderr, "Couldn't FT_Set_Char_Size()\n");
      exit (1);
   }

   for (i = 0; i < strlen (str); i++ ) {
      FT_UInt  glyph_index;
      
         
      // retrieve glyph index from character code
      glyph_index = FT_Get_Char_Index (face, str[i]);

      if (!glyph_index) {
         fprintf (stderr, "Warning, %d has no glyph\n", str[i]);
      }
      
      // load glyph image into the slot (erase previous one)
      error = FT_Load_Glyph (face, glyph_index, FT_LOAD_DEFAULT);

      if (error) continue;  // ignore errors
         
      // convert to an anti-aliased bitmap
      error = FT_Render_Glyph (face->glyph, ft_render_mode_normal);
      
      if (error) continue;  // ignore errors

      slot = face->glyph;
      
      // now, draw to our target surface
      draw_bitmap (&slot->bitmap,
                   pen_x + slot->bitmap_left,
                   pen_y - slot->bitmap_top + ptsize + ptsize / 5, fgcol);
                         
      // increment pen position 
      pen_x += slot->advance.x >> 6;
      
   }
   
   /*
    * Note that bitmap_left is the horizontal distance from
    * the current pen position to the left-most border of the
    * glyph bitmap, while bitmap_top is the vertical distance
    * from the pen position (on the baseline) to the top-most
    * border of the glyph bitmap. It is positive to indicate
    * an upwards distance.
    */

   FT_Done_Face (face);

   return (pen_x - x);
}

  
#ifdef TEST

int
main (int ac, char *av[])
{
   char *pFont = av[1];


   if (ac != 2) {
      fprintf (stderr, "Usage: %s <fontname.ttf>\n", av[0]);
      exit (1);
   }

   ft_puts (pFont, 64, 0, 0, 0, "TESTing...");

   exit (0);
   
}
#endif
