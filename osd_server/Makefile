#
# Makefile - OSD stuff
#
# $Id$

CFLAGS = -O2 -Wall
FREETYPE_CFLAGS = `freetype-config --cflags`
LIBS = -lm -lpng -lz `freetype-config --libs` -ljpeg

# Uncomment the following line to enable fullscren/vidmode support
#X11_FULLSCREEN = 1
#xSDL_FULLSCREEN = 1

ifdef X11_FULLSCREEN
	XLIBS = -L/usr/X11R6/lib -lX11 -lXext -lXxf86vm
	DFLAGS = -DOSD_X11_FULLSCREEN -DOSD_X11
else
	XLIBS = -L/usr/X11R6/lib -lX11
	DFLAGS = -DOSD_X11
endif

ifdef xSDL_FULLSCREEN 
	SDLFLAGS = -DSDL_FULLSCREEN
endif

SDLLIBS = -lSDL -lpthread

all: osds_fb vtrelease

vtrelease:
	gcc $(CFLAGS) -o vtrelease vtrelease.c

osds_fb: main.c ft.c ft.h fb.c fb.h readpng.c readpng.h readjpeg.c readjpeg.h
	gcc -DOSD_FB $(CFLAGS) $(FREETYPE_CFLAGS) main.c ft.c fb.c readpng.c readjpeg.c -o osds_fb $(LIBS)

osds_x11: main.c ft.c ft.h x11.c x11.h readpng.c readpng.h readjpeg.c readjpeg.h
	gcc $(DFLAGS) $(CFLAGS) $(FREETYPE_CFLAGS)  -o osds_x11 main.c ft.c x11.c readpng.c readjpeg.c \
	$(XLIBS) $(LIBS)

osds_sdl: main.c ft.c ft.h sdl.c sdl.h readpng.c readpng.h readjpeg.c readjpeg.h
	gcc -DOSD_SDL $(CFLAGS) $(FREETYPE_CFLAGS) $(SDLFLAGS) -o osds_sdl main.c ft.c sdl.c \
	readpng.c readjpeg.c $(SDLLIBS) $(LIBS)

osds_dxr3: main.c ft.c ft.h dxr3.c dxr3.h readpng.c readpng.h readjpeg.c readjpeg.h 
	gcc -DOSD_DXR3 $(CFLAGS) $(FREETYPE_CFLAGS) -o osds_dxr3 main.c ft.c dxr3.c readpng.c readjpeg.c \
	$(LIBS) -lfame -pg

x11test: x11.c x11.h readpng.c readpng.h readjpeg.c readjpeg.h
	gcc -Wall -g -DTEST x11.c readpng.c readjpeg.c -o x11test $(XLIBS) $(LIBS)

sdltest: sdl.c sdl.h readpng.c readpng.h
	gcc $(CFLAGS) $(FREETYPE_CFLAGS) $(DFLAGS) -DTEST sdl.c readpng.c -o sdltest $(SDLLIBS) $(LIBS)

fttest: ft.c
	gcc $(CFLAGS) -g  $(FREETYPE_CFLAGS)  ft.c -o fttest -DTEST 

pngtest: readpng.c readpng.h
	gcc -DPNGTEST $(CFLAGS) -Wall readpng.c -o pngtest $(LIBS)

clean:
	-rm -f *.o *.pyc osds_fb osds_x11 osds_dxr3 x11test pngtest fttest sdltest osds_sdl vtrelease
