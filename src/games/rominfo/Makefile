#
# I have included comments for the benefit of makefile newbies :)
#

CC=@gcc
LD=@gcc
MD=mkdir

SRC=src

OBJ=obj
OBJDIRS=$(OBJ) $(OBJ)/mame $(OBJ)/mame/msdos
OBJS=$(OBJ)/mame/msdos/msdos.o $(OBJ)/mame/unzip.o $(OBJ)/rominfo.o

EXE=rominfo

LIBS=-lz

#
# Build the obj tree then build the EXE
#

all: maketree $(EXE)

#
# Creating obj directory tree
#

maketree: $(sort $(OBJDIRS))

$(sort $(OBJDIRS)):
	$(MD) $@

#
# Linking the object files to make the EXE
#

$(EXE): $(OBJS)
	@echo Linking $@...
	$(LD) $(OBJS) $(LIBS) -o $@


#
# Building of each module from MAME (and another for ROMBuild)
#

$(OBJ)/mame/msdos/msdos.o: $(SRC)/mame/msdos/msdos.c
	@echo Compiling $@...
	$(CC) $< -c -o $@

$(OBJ)/mame/unzip.o: $(SRC)/mame/unzip.c $(SRC)/mame/unzip.h $(SRC)/mame/osd_cpu.h
	@echo Compiling $@...
	$(CC) $< -c -o $@

$(OBJ)/rominfo.o: $(SRC)/rominfo.c $(SRC)/rominfo.h
	@echo Compiling $@...
	$(CC) $< -c -o $@
