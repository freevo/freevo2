#include <stdio.h>
#include <X11/Xlib.h> 
#include <X11/Xutil.h> 
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>

#include "x11.h"

static Display *dpy;
static Window w;
static GC gc;
static XVisualInfo visinf;
static int xres, yres;
static XImage *pImage;
static uint8 *pFrameBuffer;
static int swap = 0;            /* RGB => BGR */

static void hidecursor (void);


int
x11_open (int width, int height)
{
   XSetWindowAttributes attr;
   

   xres = width;
   yres = height;
   
   dpy = XOpenDisplay (0);

   assert (dpy);

   printf ("Screen %d\n", DefaultScreen(dpy));

   /* Try to get a 24-bit visual */
   if (!XMatchVisualInfo (dpy, DefaultScreen(dpy), 24, TrueColor, &visinf)) {
      fprintf (stderr, "Cannot get a 24-bit color window!\n");
      
      /* Try to get a 32-bit visual */
      if (!XMatchVisualInfo (dpy, DefaultScreen(dpy), 32, TrueColor, &visinf)) {
         fprintf (stderr, "Cannot get a 32-bit window, exiting!\n");
         exit (1);
      }
   }

   /* If we get here we have either a 24- or 32-bit visual */
   printf ("Matched visual info, id = 0x%02x, depth = %d\n",
           (uint32) visinf.visualid, visinf.depth);
   
   attr.backing_store = Always;
   attr.background_pixel = 0xffffff;
   w = XCreateWindow (dpy, DefaultRootWindow(dpy), 0, 0, 
                      xres, yres, 0, 24, InputOutput,
                      visinf.visual,
                      CWBackingStore | CWBackPixel,
                      &attr);

   XSelectInput (dpy, w, StructureNotifyMask | KeyPressMask |
                 ExposureMask);

   hidecursor ();
   
   XMapWindow (dpy, w);

   gc = XCreateGC (dpy, w, 0, 0);

   while (1) {                  /* XXX Add a timeout counter */
      XEvent e;

      
      XNextEvent (dpy, &e);
      
      if (e.type == MapNotify)
         break;
   }

   /* X11 emulated framebuffer memory */
   pFrameBuffer = (uint8 *) malloc (width * height * 4);

   memset (pFrameBuffer, 0x80, width * height * 4);
   
   pImage = XCreateImage (dpy, visinf.visual, 24, ZPixmap, 0,
                          pFrameBuffer, width, height, 8, width*4);

   printf ("XImage: bitmap_bit_order=%d, depth=%d, bitmap_pad=%d, "
           "bits_per_pixel=%d, (%08lx, %08lx, %08lx)\n",
           pImage->bitmap_bit_order, pImage->depth, pImage->bitmap_pad,
           pImage->bits_per_pixel,
           pImage->red_mask, pImage->green_mask, pImage->blue_mask);

   if (pImage->red_mask == 0xff) {
      swap = 1;
   }
   
   XPutImage (dpy, w, gc, pImage, 0, 0, 0, 0, width, height);

   XFlush (dpy);

   /* Done */
   return (0);

}


static void
hidecursor (void)
{
  Cursor c;
  Pixmap pmap1, pmap2;
  XColor fg, bg;


  pmap1 = XCreatePixmap (dpy, w, 1, 1, 1);
  pmap2 = XCreatePixmap (dpy, w, 1, 1, 1);

  memset (&fg, 0, sizeof (XColor));
  memset (&bg, 0, sizeof (XColor));
  
  c = XCreatePixmapCursor (dpy, pmap1, pmap2, &fg, &bg, 0, 0);

  XDefineCursor (dpy, w, c);
  
}

      
void
x11_update (uint8 *pFB)
{
   int i;
   uint8 *pRedSrc = (uint8 *) (&pFB[2]);
   uint8 *pGreenSrc = (uint8 *) (&pFB[1]);
   uint8 *pBlueSrc = (uint8 *) (&pFB[0]);
   uint8 *pRedDst = (uint8 *) (&pFrameBuffer[0]);
   uint8 *pGreenDst = (uint8 *) (&pFrameBuffer[1]);
   uint8 *pBlueDst = (uint8 *) (&pFrameBuffer[2]);


   if (!swap) {
      memcpy (pFrameBuffer, pFB, xres*yres*4);
   } else {
      /* RGB => BGR conversion needed */
      for (i = 0; i < xres*yres*4; i += 4) {
         pRedDst[i] = pRedSrc[i];
         pGreenDst[i] = pGreenSrc[i];
         pBlueDst[i] = pBlueSrc[i];
      }
   }

   XPutImage (dpy, w, gc, pImage, 0, 0, 0, 0, xres, yres);
   
   XFlush (dpy);
}


/* Check for and handle all events */
void
x11_pollevents (void)
{
   XEvent e;

      
   while (XCheckWindowEvent (dpy, w, 0xffffffff, &e)) {

      if (e.type == Expose) {
        
        printf ("Got expose: %dx%d at %d;%d\n",
                e.xexpose.width, e.xexpose.height,
                e.xexpose.x, e.xexpose.y);

        XPutImage (dpy, w, gc, pImage, e.xexpose.x, e.xexpose.y,
                   e.xexpose.x, e.xexpose.y,
                   e.xexpose.width, e.xexpose.height);
        XFlush (dpy);
      } else if (e.type == KeyPress) {
        printf ("Got keypress, key = %d\n", e.xkey.keycode);
      }

   }

}


void
x11_close (void)
{
   /* XXX */
   return;
}


#ifdef TEST
int
main (int ac, char *av[])
{
   
   
   printf ("open()\n");
   x11_open (768, 576);

#if 0
   printf ("clearscreen()\n");
   x11_clearscreen (0);
   sleep (1);
   x11_clearscreen (0xffffff);
   sleep (1);

   printf ("setpixel()\n");
   x11_setpixel (10, 10, 0xff0000);
   sleep (1);
   x11_setpixel (xres - 10, 10, 0xff0000);
   sleep (1);
   x11_setpixel (xres - 10, yres - 10, 0xff0000);
   sleep (1);
   x11_setpixel (10, yres - 10, 0xff0000);
   sleep (1);

   for (i = 0; i < width*height; i++) {
      pData[i*3+0] = i % 17;
      pData[i*3+1] = i % 53;
      pData[i*3+2] = i % 256;
   }
   

   for (i = 1; i < ac; i++) {
      printf ("read png %s\n", av[i]);
      read_png (av[i], &pBitmap, &w, &h);

      x11_drawbitmap (10, 10, w, h, pBitmap);

      x11_flush ();

      free (pBitmap);
   }
   
#endif
   
   printf ("\nPress a <CR> to exit!\n");
   
   getchar ();
   
   x11_close ();

   return (0);
   
}
#endif /* TEST */


