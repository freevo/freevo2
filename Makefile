#if 0 /*
# -----------------------------------------------------------------------
# Makefile - Main Freevo makefile
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.16  2003/01/30 02:47:26  krister
# Updated clean target
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif

CC = gcc
CFLAGS = -O2 -Wall 

# Just look everywhere for X11 stuff...
XLIBS = -L/usr/X11R6/lib -L/usr/X11/lib -L/usr/lib32 -L/usr/openwin/lib \
        -L/usr/X11R6/lib64 -lX11
XINC = -I/usr/X11R6/include -I/usr/X11/include -I/usr/openwin/include

SUBDIRS = fbcon


.PHONY: all subdirs x11 osd_x1 $(SUBDIRS) clean release install

all: subdirs runapp freevo_xwin

runapp: runapp.c
	$(CC) $(CFLAGS) -o runapp runapp.c -DRUNAPP_LOGDIR=\"/var/log/freevo\"

freevo_xwin: freevo_xwin.c
	$(CC) $(CFLAGS) -o freevo_xwin freevo_xwin.c $(XINC) $(XLIBS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	-rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc *.o log_main_out 
	-rm -f log_main_err log.txt runapp freevo_xwin mplayer_std*.log
	cd fbcon ; $(MAKE) clean

# Remove all compiled python files
distclean:
	find . -name "*.pyc*" -exec rm -f {} \;
	$(MAKE) -C fbcon distclean

release: clean
	cd ..; tar czvf freevo-`cat freevo/VERSION`-`date +%Y%m%d`.tar.gz \
	  --exclude CVS freevo


# XXX Real simple install procedure for now, but freevo is so small it doesn't really
# XXX matter
install: all
	-mv /usr/local/freevo /usr/local/freevo_old_`date +%Y%m%d_%H%M%S`
	-rm -rf /usr/local/freevo
	-mkdir /usr/local/freevo

	-mkdir -p /var/log/freevo
	chmod ugo+rwx /var/log/freevo

	-mkdir -p /var/cache/freevo
	chmod ugo+rwx /var/cache/freevo

	-mkdir -p /var/cache/xmltv/logos
	chmod -R ugo+rwx /var/cache/xmltv

	cp -r * /usr/local/freevo
