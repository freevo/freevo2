#if 0 /*
# -----------------------------------------------------------------------
# freevo_xwin.c - Used to contain an MPlayer window under X11.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2002/09/18 02:32:47  gsbarbieri
# Fixed compilation warning: added #include <string.h> to fix memset implict declaration
#
# Revision 1.2  2002/08/19 02:11:21  krister
# Make window black at startup.
#
# Revision 1.1  2002/08/14 04:35:34  krister
# Added the new X11 mplayer control app: freevo_xwin.
#
# This standalone application is used to contain an MPlayer window
# under X11. This is so that Freevo can control where that window is
# displayed, and also prevents mplayer from grabbing all keyboard
# events. The X11 windows ID is communicated back to Freevo on
# stdout at startup. The window geometry is given on the commandline.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif

#include <stdio.h>
#include <X11/Xlib.h> 
#include <X11/Xutil.h> 
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "portable.h"

      
static Display *dpy;
static Window w;
static XVisualInfo visinf;
static GC gc;
static int xres, yres, depth;
static void hidecursor (void);


void x11_clearscreen (uint32 color);


int
x11_open (int x, int y, int width, int height)
{
   XSetWindowAttributes attr;
   

   xres = width;
   yres = height;
   
   dpy = XOpenDisplay (0);

   assert (dpy);

   /* Try to get a 24-bit visual */
   if (!XMatchVisualInfo (dpy, DefaultScreen(dpy), 24, TrueColor, &visinf)) {
      fprintf (stderr, "Cannot get a 24-bit color window!\n");
      
      /* Try to get a 32-bit visual */
      if (!XMatchVisualInfo (dpy, DefaultScreen(dpy), 32, TrueColor, &visinf)) {
        fprintf (stderr, "Cannot get a 32-bit color window!\n");
      	/* Try to get a 16-bit visual */
        depth = 16;
        
      	if (!XMatchVisualInfo (dpy, DefaultScreen(dpy), 16, TrueColor, &visinf)) {
          fprintf (stderr, "Cannot get a 16-bit window, exiting!\n");
          exit (1);
        }
      }
   }

#if 0
   /* If we get here we have a 24- or 32-bit or 16-bit visual */
   printf ("Matched visual info, id = 0x%02x, depth = %d\n",
           (uint32) visinf.visualid, visinf.depth);
#endif
   
   attr.backing_store = Always;
   attr.background_pixel = 0xffffff;
   attr.override_redirect = 1;

   if(depth == 16) {
     w = XCreateWindow (dpy, DefaultRootWindow(dpy), xres/4, yres/4,
                        xres, yres, 0, 16, InputOutput,
                        visinf.visual,
                        CWBackingStore | CWBackPixel,
                        &attr);
   } else {
     w = XCreateWindow (dpy, DefaultRootWindow(dpy), x, y,
                        xres, yres, 0, 24, InputOutput,
                        visinf.visual,
                        CWBackingStore | CWBackPixel | CWOverrideRedirect,
                        &attr);
   }

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

   x11_clearscreen (0);
   
   XFlush (dpy);

   /* Done */
   return (0);

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


/* Check for and handle all events */
void
x11_pollevents (void)
{
   XEvent e;

      
   while (XCheckWindowEvent (dpy, w, 0xffffffff, &e)) {

      if (e.type == Expose) {
#if 0
        printf ("Got expose: %dx%d at %d;%d\n",
                e.xexpose.width, e.xexpose.height,
                e.xexpose.x, e.xexpose.y);
#endif
      } else if (e.type == KeyPress) {
#if 0
        printf ("Got keypress, key = %d\n", e.xkey.keycode);
#endif
      }

   }

}


void
x11_moveresize (int x, int y, int width, int height)
{
  XMoveResizeWindow (dpy, w, x, y, width, height);
  XFlush (dpy);
  //  printf ("x11_moveresize() %dx%d at %d;%d\n", width, height, x, y);
     
}


void
x11_close (void)
{
  
   return;
}


int
main (int ac, char *av[])
{

  if (ac != 5) {
    fprintf (stderr, "Usage: %s x y width height\n", av[0]);
    exit (1);
  }
                 
   x11_open (atoi (av[1]), atoi(av[2]), atoi (av[3]), atoi(av[4]));

   printf ("0x%08x\n", (uint32) w);
   fflush (stdout);
   
   //x11_moveresize (0, 0, 1280, 1024);
   
   while (1) {
     sleep (10);
   }
   
   exit (0);







   /* Test code */
   while (1) {
     
     getchar ();
     XUnmapWindow (dpy, w);
     XFlush (dpy);
     getchar ();
     XMapRaised (dpy, w);
     XFlush (dpy);
   }
   sleep (2);

   while (1) {
     x11_moveresize (0, 0, 1280, 1024);
     sleep (1);
     
     x11_moveresize (1280 - 640, 0, 640, 480);
     sleep (1);
     
     x11_moveresize (1280 - 426, 0, 426, 320);
     sleep (1);

   }
   
   x11_close ();

   return (0);
   
}
