#
# Linux Frame Buffer Device Configuration
#

CFLAGS =	-Wall -O2 -I.
BISON =		bison -d
FLEX =		flex
RM =		rm -f

All:		fbset


fbset:		fbset.o modes.tab.o lex.yy.o

fbset.o:	fbset.c fbset.h fb.h
modes.tab.o:	modes.tab.c fbset.h fb.h
lex.yy.o:	lex.yy.c fbset.h modes.tab.h

lex.yy.c:	modes.l
		$(FLEX) modes.l

modes.tab.c:	modes.y
		$(BISON) modes.y

clean:
		$(RM) *.o fbset lex.yy.c modes.tab.c modes.tab.h
