# Makefile for FreevoTTX


# This is the path to the compiled libzvbi sources.
# You don't need to "make install", only "make".
# You need the CVS version until v0.2.3 is released!
LIBZVBI_SOURCES=vbi

# You also need libpng and Imlib2 installed!


LIBZVBI_A=$(LIBZVBI_SOURCES)/src/.libs/libzvbi.a
LIBZVBI_H=$(LIBZVBI_SOURCES)/src/libzvbi.h


FreevoTTX: FreevoTTX.c Makefile libzvbi.a libzvbi.h
	gcc -O3 -lImlib2 -lpng -lpthread -o FreevoTTX FreevoTTX.c libzvbi.a

libzvbi.a: $(LIBZVBI_A)
	cp $(LIBZVBI_A) .

libzvbi.h: $(LIBZVBI_H)
	cp $(LIBZVBI_H) .

