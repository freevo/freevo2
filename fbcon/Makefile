#
# Makefile - framebuffer stuff
#
# $Id$

CFLAGS = -O2 -Wall

.PHONY: all clean distclean matroxset


all: vtrelease matroxset

matroxset:
	$(MAKE) -C matroxset 

vtrelease:
	gcc $(CFLAGS) -o vtrelease vtrelease.c

clean:
	-rm -f *.o *.pyc vtrelease
	$(MAKE) -C matroxset clean

# Clean everything but the binaries which are included in the release
distclean:
	-rm -f *.o *.pyc 
	$(MAKE) -C matroxset distclean
