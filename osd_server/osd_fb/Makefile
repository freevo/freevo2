CFLAGS = -O2 -g

all: osd_x11 osd_fb fstest x11test pngtest

osd_fb: main.c fs.c fs.h fb.c fb.h
	gcc -DOSD_FB $(CFLAGS) -Wall main.c fs.c fb.c  -o osd_fb -lm

osd_x11: main.c fs.c fs.h x11.c x11.h
	gcc -DOSD_X11 $(CFLAGS) -Wall main.c fs.c x11.c -o osd_x11 -lm -L/usr/X11/lib -lX11

x11test: x11.c x11.h readpng.c readpng.h
	gcc -g -Wall -DTEST x11.c readpng.c -o x11test -lm -L/usr/X11/lib -lX11 -lpng -lz

jpegtest: jpeg.c jpeg.h
	gcc $(CFLAGS) -Wall -DJPEGTEST jpeg.c -o jpegtest -lm -ljpeg

pngtest: readpng.c
	gcc -g -Wall -DPNGTEST readpng.c -o pngtest -lm -lpng -lz

fstest: fs.c
	gcc $(CFLAGS) -Wall fs.c -o fstest -DTEST

clean:
	-rm -f *.o osd_fb fstest osd_x11 x11test
