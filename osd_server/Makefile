#
# Makefile - OSD stuff
#
# $Id$

# The JPEG support will not be finished for a while.

CFLAGS = -O2 -Wall -I/usr/local/include/freetype2 

all: osd_x11 osd_fb 

osd_fb: main.c ft.c ft.h fb.c fb.h readpng.c readpng.h
	gcc -DOSD_FB $(CFLAGS) -Wall main.c ft.c fb.c readpng.c -o osd_fb -lm -lpng -lz -L/usr/local/lib -lfreetype 

osd_x11: main.c ft.c ft.h x11.c x11.h readpng.c readpng.h
	gcc -DOSD_X11 $(CFLAGS) main.c ft.c x11.c -o osd_x11 readpng.c -lm -L/usr/X11/lib -lX11 -lpng -lz -L/usr/local/lib -lfreetype 

x11test: x11.c x11.h readpng.c readpng.h
	gcc $(CFLAGS) -DTEST x11.c readpng.c -o x11test -lm -L/usr/X11/lib -lX11 -lpng -lz

fttest: ft.c
	gcc $(CFLAGS) -g  -L/usr/local/lib -lfreetype -Wall ft.c -o fttest -DTEST 

clean:
	-rm -f *.o *.pyc osd_fb osd_x11 x11test pngtest fttest
