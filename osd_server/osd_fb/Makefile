CFLAGS = -O2 -g

all: osd_x11 osd_fb fstest

osd_fb: main.c fs.c fs.h fb.c fb.h
	gcc -DOSD_FB $(CFLAGS) -Wall main.c fs.c fb.c  -o osd_fb -lm

osd_x11: main.c fs.c fs.h x11.c x11.h
	gcc -DOSD_X11 $(CFLAGS) -Wall main.c fs.c x11.c -o osd_x11 -lm -L/usr/X11/lib -lX11

x11test: x11.c x11.h
	gcc $(CFLAGS) -Wall -DTEST x11.c -o x11test -lm -L/usr/X11/lib -lX11

fstest: fs.c
	gcc $(CFLAGS) -Wall fs.c -o fstest -DTEST

clean:
	-rm -f *.o osd_fb fstest osd_x11 x11test
