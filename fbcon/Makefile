#
# Makefile - framebuffer stuff
#
# $Id$

CFLAGS = -O2 -Wall

.PHONY: all clean distclean matroxset


all: vtrelease matroxset

matroxset:
	make -C matroxset 

vtrelease:
	gcc $(CFLAGS) -o vtrelease vtrelease.c

clean:
	-rm -f *.o *.pyc vtrelease
	make -C matroxset clean

# Clean everything but the binaries which are included in the release
distclean:
	-rm -f *.o *.pyc 
	make -C matroxset distclean
