#include <stdio.h>
#include <X11/Xlib.h> 
#include <X11/Xutil.h> 
#include <unistd.h>
#include <assert.h>

#include "x11.h"

static Display *dpy;
static Window w;
static GC gc;
static XVisualInfo visinf;
static int xres, yres;


#ifdef TEST
int
main (void)
{
   printf ("open()\n");
   x11_open (768, 576);
   sleep (1);

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

   x11_close ();

   return (0);
   
}
#endif /* TEST */


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

   XSelectInput (dpy, w, StructureNotifyMask);

   XMapWindow (dpy, w);

   gc = XCreateGC (dpy, w, 0, 0);

   while (1) {                  /* XXX Add a timeout counter */
      XEvent e;

      
      XNextEvent (dpy, &e);
      
      if (e.type == MapNotify)
         break;
   }

#if 0
{
   srand (0);
   for (i = 0; i < 50000; i++) {
      x0 = rand() % xres;
      y0 = rand() % yres;
      x1 = rand() % xres;
      y1 = rand() % yres;
      XSetForeground (dpy, gc, rand() & 0xffffff);
      XDrawLine (dpy, w, gc, x0, y0, x1, y1);
      XFlush (dpy);
   }
}
#endif

   /* Done */
   return (0);
   
}



int
x11_close (void)
{
   /* XXX */
   return (0);
}



void
x11_setpixel (int x, int y, uint32 color)
{
   XSetForeground (dpy, gc, color);
   XDrawPoint (dpy, w, gc, x, y);
}


void
x11_flush (void)
{
   XFlush (dpy);
}


void
x11_clearscreen (uint32 color)
{
   int i;


   XSetForeground (dpy, gc, color);

   for (i = 0; i < yres; i++) {
      XDrawLine (dpy, w, gc, 0, i, xres-1, i);
   }

}
