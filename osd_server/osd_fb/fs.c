/*
 * Generic font rendering, based on fonts converted from the X11 BDF
 * format.
 *
 * Based on code from xawtv:
 * (c) 2001 Gerd Knorr <kraxel@bytesex.org>
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#include "fs.h"

#ifndef TEST
#include "osd.h"
#endif

#include "helvB18-L1.h"


static const unsigned fs_masktab[] = {
    (1 << 7), (1 << 6), (1 << 5), (1 << 4),
    (1 << 3), (1 << 2), (1 << 1), (1 << 0),
};


#ifdef TEST

#define BITMAP_WIDTH 300
#define BITMAP_HEIGHT 30

static char bitmap[BITMAP_WIDTH][BITMAP_HEIGHT];

static void
osd_setpixel (uint16 x, uint16 y, uint32 color)
{
   int i, j;
   static int init = 0;


   if (!init) {
      for (i = 0; i < BITMAP_WIDTH; i++) {
         for (j = 0; j < BITMAP_HEIGHT; j++) {
            bitmap[i][j] = 'U';
         }
      }

      init = 1;
         
   }

   if ((x >= BITMAP_WIDTH) || (y >= BITMAP_HEIGHT)) {
      return;
   }
      
   if (color == 0) {
      bitmap[x][y] = '.';
   } else {
      bitmap[x][y] = 'X';
   }
   
}


int
main (int ac, char *av[])
{
   font_t *f;
   int i, j, w;
   char str[] = "abhijkp";
   char *p_str = str;
   

   if (ac == 2) {
      p_str = av[1];
   }

   f = fs_open (NULL);

   w = fs_puts (f, 0, 0, 0xffffff, 0, p_str);

   for (i = 0; i < BITMAP_HEIGHT; i++) {
      for (j = 0; j < w; j++) {
         printf ("%c", bitmap[j][i]);
      }
      printf ("\n");
   }

   exit (0);

}
#endif /* TEST */


font_t *
fs_open (char *pattern)
{
   return &fontdata;
}


void fs_render_fb (int start_x, int start_y,
                   fontchar_t *pFontchar, 
                   uint32 fgcol, uint32 bgcol)
{
    int row, bit, bytes_per_row;
    uint8 *pBitmap;
    
    
    /* Number of bytes between each row in the char bitmap */
    bytes_per_row = ((pFontchar->width + 7) >> 3);

    /* Pointer to the character bitmap */
    pBitmap = pFontchar->pBitmap;
    
    for (row = 0; row < pFontchar->height; row++) {

       for (bit = 0; bit < pFontchar->width; bit++) {

           if (pBitmap[bit >> 3] & fs_masktab[bit & 7]) {
              osd_setpixel (start_x + bit, start_y + row, fgcol);
           } 

       }

	pBitmap += bytes_per_row;     
    }

}


int
fs_puts (font_t *f, int x, int y, uint32 fgcol, uint32 bgcol,
         unsigned char *str)
{
   int i, j, k, c;
   int cell_top, cell_left, org_x, baseline;


   cell_left = x;
   baseline = y + f->height + f->y;

#ifdef TEST
   printf ("Font height = %d, x = %d, y = %d, baseline = %d\n\n",
           f->height, f->x, f->y, baseline);
#endif

   for (i = 0; str[i] != '\0'; i++) {
      c = str[i];
      
      if (f->pFontchars[c] == NULL) {
         continue;
      }
      
      for (j = 0; j < f->height; j++) {
         for (k = 0; k < f->pFontchars[c]->dwidth; k++) {
               osd_setpixel (cell_left + k, y + j, bgcol);
         }
      }

      /* draw char */
      cell_top = baseline - f->pFontchars[c]->height -
         f->pFontchars[c]->y;

      org_x = cell_left + f->pFontchars[c]->x;

#ifdef TEST
      printf ("Char %3d=%c, width = %2d, height = %2d, x = %2d, y = %2d, top = %2d\n",
              c, c, f->pFontchars[c]->dwidth, f->pFontchars[c]->height,
              f->pFontchars[c]->x, f->pFontchars[c]->y, cell_top);
#endif
      
      fs_render_fb (org_x, cell_top, f->pFontchars[c],
                    fgcol, bgcol);
      
      cell_left += f->pFontchars[c]->dwidth;
      
    }

    return (cell_left);
}
