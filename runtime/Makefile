#if 0 /*
# -----------------------------------------------------------------------
# Makefile - builds the runtime (libraries and apps)
#
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/02/18 04:54:05  krister
# runtime builder updates.
#
# Revision 1.7  2003/02/18 04:15:27  krister
# Added jpegtran to the runtime build.
#
# Revision 1.6  2003/02/07 05:06:32  krister
# Added execute flag for pygphoto.so
#
# Revision 1.5  2003/02/05 15:22:52  krister
# Updated build stuff, Changelog
#
# Revision 1.4  2003/02/05 06:10:46  krister
# Changed the start scripts and childapp.py to use startprog to start all programs.
#
# Revision 1.3  2003/01/28 03:45:35  krister
# Work in progress...
#
# Revision 1.2  2003/01/24 07:30:56  krister
# Create missing folders.
#
# Revision 1.1  2003/01/24 07:19:48  krister
# New runtime
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


.PHONY: copy build clean src copy_libdeps


# There is no default target, you gotta know what you're doing :-)
all:
	@echo Please see the Makefile source and the Wiki for more info!


# Copy the libraries, programs etc to this directory
# There is no dependency checking, the libs are just copied
# It is probably a good idea to do a build first, unless you know
# all libs are up-to-date.
# Python programs in lib/ have their execute flag removed since
# RPM building chokes on them.
copy: 	python_copy mplayer_copy mplayer_fonts_copy cdparanoia_copy \
	lame_copy pygphoto_copy jpegtran_copy build_copy copy_libdeps
	find lib -name "*.so" -exec strip {} \;
	find dll -name "*.so*" -exec strip {} \;
	find apps -perm +111 -type f -exec strip {} \;
	find lib -name "*.py" -perm +0111 -exec chmod ugo-x \{\} \;


# Build all the libraries etc
build:
	$(MAKE) -C build all


# Copy apps etc from the build dir
build_copy:
	$(MAKE) -C build copy


# Remove all copied libraries, programs etc
# The build directory is not touched
clean: 
	-rm -rf lib apps/* dll/*


# A python app that checks all libs and apps to find dynamic
# link lib dependencies. All deps are copied to the dll folder.
# The dynamic link loader ld-linux is renamed to freevo-run for
# easy killing in the main startscript 'freevo'
copy_libdeps:
	-mkdir -p dll
	python copy_libdeps.py
	mv dll/ld-linux.so.2 dll/freevo_loader


################################################################################
#
# Python 2.2.2
#
################################################################################
# This will copy a number of the other packages as well since they're installed
# in python's site-packages folder.
python_copy:
	@echo Copying python
	-rm -rf lib
	-mkdir -p lib
	-mkdir -p apps
	cp -a /usr/local/lib/python2.2 lib
	find . -name "*.pyo" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
	rm -rf lib/python2.2/config
	rm -rf lib/python2.2/lib-tk
	rm -rf lib/python2.2/lib-old
	rm -rf lib/python2.2/test
	mkdir tmp
	cp -a lib/python2.2/site-packages/{CDDB.py,DiscID.py,Numeric,Numeric.pth} tmp
	cp -a lib/python2.2/site-packages/{PIL,PIL.pth,_xmlplus,_xmms.so,aomodule.so} tmp
	cp -a lib/python2.2/site-packages/{cdrom.so,mx,ogg,psyco,pygame,xmms.py} tmp
	rm -rf lib/python2.2/site-packages
	mv tmp lib/python2.2/site-packages
	cp -a /usr/local/bin/python2.2 apps/freevo_python


################################################################################
#
# MPlayer/Mencoder
#
################################################################################
mplayer_copy:
	@echo Copying mplayer/mencoder
	-mkdir -p apps/mplayer
	cp build/mplayer/{mplayer,mencoder} ./apps/mplayer/
	cp build/mplayer/README ./apps/mplayer/README.mplayer
	cp build/mplayer/etc/{codecs.conf,input.conf} ./apps/mplayer/


################################################################################
#
# MPlayer fonts
#
################################################################################
mplayer_fonts_copy:
	@echo Copying mplayer fonts
	-mkdir -p apps/mplayer/font
	cp build/mplayer_fonts/font-arial-18-iso-8859-1/* apps/mplayer/font
	rm apps/mplayer/font/runme


################################################################################
#
# cdparanoia
#
################################################################################
cdparanoia_copy:
	@echo Copying cdparanoia
	cp -a /usr/local/bin/cdparanoia apps/


################################################################################
#
# lame
#
################################################################################
lame_copy:
	@echo Copying lame
	cp -a /usr/local/bin/lame apps/


################################################################################
#
# pygphoto. Depends on libgphoto2
#
################################################################################
pygphoto_copy:
	@echo Copying pygphoto
	cp -a src/pygphoto.so lib/python2.2/site-packages/
	chmod ugo+x lib/python2.2/site-packages/pygphoto.so


################################################################################
#
# jpegtran. comes from the libjpeg v6b library.
#
################################################################################
jpegtran_copy:
	@echo Copying jpegtran
	cp -a /usr/local/bin/jpegtran apps/
