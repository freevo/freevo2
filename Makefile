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
# Revision 1.29  2003/02/27 05:53:20  krister
# Avoid merge problems for CVS updates, couldn't do some straight updates!
#
# Revision 1.28  2003/02/25 06:34:08  krister
# Quick fix for the TV recording menu problem. Added makefile target for CVS update.
#
# Revision 1.27  2003/02/24 05:45:50  krister
# Improved cleaning
#
# Revision 1.26  2003/02/24 05:15:35  krister
# Added trace.txt to the clean target.
#
# Revision 1.25  2003/02/15 03:31:21  krister
# Updated for new setup app.
#
# Revision 1.24  2003/02/07 20:49:09  dischi
# safety check
#
# Revision 1.23  2003/02/07 20:35:18  dischi
# moved python_compile to install
#
# Revision 1.22  2003/02/07 06:15:36  krister
# Added a realclean target, removes freevo.conf
#
# Revision 1.21  2003/02/06 09:54:01  krister
# Changed the runtime handling to use runapp to start programs with the supplied dlls
#
# Revision 1.20  2003/02/06 09:52:25  krister
# Changed the runtime handling to use runapp to start programs with the supplied dlls
#
# Revision 1.19  2003/02/05 15:22:51  krister
# Updated build stuff, Changelog
#
# Revision 1.18  2003/02/05 06:08:58  krister
# Delete all .pyc and .pyo when doing a make clean
#
# Revision 1.17  2003/02/04 13:07:16  dischi
# setip_build can now compile python files. This is used by the Makefile
# (make all). The Makefile now also has the directories as variables.
#
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

SUBDIRS  = fbcon
OPTIMIZE = 0

PREFIX   = /usr/local/freevo
LOGDIR   = /var/log/freevo
CACHEDIR = /var/cache/freevo


.PHONY: all subdirs x11 osd_x1 $(SUBDIRS) clean realclean release install cvsup

all: subdirs runapp freevo_xwin

python_compile: runapp
	./runapp python setup_freevo.py --compile=$(OPTIMIZE),$(PREFIX)

runapp: runapp.c
	$(CC) $(CFLAGS) -static -o runapp runapp.c -DRUNAPP_LOGDIR=\"$(LOGDIR)\"
	strip runapp

freevo_xwin: freevo_xwin.c
	$(CC) $(CFLAGS) -o freevo_xwin freevo_xwin.c $(XINC) $(XLIBS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@


cvsup:
	cvs update -C -r LATEST_ALPHA

clean:
	find . -name "*.pyo" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
	-rm -f *.o log_main_out trace.txt
	-rm -f log_main_err log.txt runapp freevo_xwin mplayer_std*.log
	cd fbcon ; $(MAKE) clean

realclean: clean
	find . -name "*.rej" -exec rm {} \;
	find . -name "*.orig" -exec rm {} \;
	find . -name ".#*" -exec rm {} \;
	-rm -f freevo.conf

# Remove all compiled python files, and other stuff
distclean:
	find . -name "*.pyc*" -exec rm -f {} \;
	$(MAKE) -C fbcon distclean

release: clean
	cd ..; tar czvf freevo-`cat freevo/VERSION`-`date +%Y%m%d`.tar.gz \
	  --exclude CVS freevo



install: all python_compile
	test "$(PREFIX)" != "${PWD}" || false
	-rm -rf $(PREFIX)
	-mkdir -p $(PREFIX)

	-mkdir -p $(LOGDIR)
	chmod ugo+rwx $(LOGDIR)

	-mkdir -p $(CACHEDIR)
	chmod ugo+rwx $(CACHEDIR)

	-mkdir -p $(CACHEDIR)/xmltv/logos
	chmod -R ugo+rwx $(CACHEDIR)/xmltv

	cp -r * $(PREFIX)


uninstall:
	-rm -rf $(PREFIX) $(CACHEDIR) $(LOGDIR)
