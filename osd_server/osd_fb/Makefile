#
# Makefile - OSD stuff
#
# $Id$

# The PNG support is under development.
# The JPEG support will not be finished for a while.

CFLAGS = -O2 -Wall

all: osd_x11 osd_fb fstest x11test

osd_fb: main.c fs.c fs.h fb.c fb.h readpng.c readpng.h
	gcc -DOSD_FB $(CFLAGS) -Wall main.c fs.c fb.c readpng.c -o osd_fb -lm -lpng -lz

osd_x11: main.c fs.c fs.h x11.c x11.h readpng.c readpng.h
	gcc -DOSD_X11 $(CFLAGS) main.c fs.c x11.c -o osd_x11 readpng.c -lm -L/usr/X11/lib -lX11 -lpng -lz

x11test: x11.c x11.h readpng.c readpng.h
	gcc $(CFLAGS) -DTEST x11.c readpng.c -o x11test -lm -L/usr/X11/lib -lX11 -lpng -lz

fstest: fs.c
	gcc $(CFLAGS) -Wall fs.c -o fstest -DTEST

clean:
	-rm -f *.o osd_fb fstest osd_x11 x11test pngtest
