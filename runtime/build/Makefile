#if 0 /*
# -----------------------------------------------------------------------
# Makefile - compile the libraries and apps.
#
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/02/19 05:46:59  krister
# Added mplayer patch for CDDA problems. Remove if/when accepted into mplayer.
#
# Revision 1.7  2003/02/18 04:54:05  krister
# runtime builder updates.
#
# Revision 1.6  2003/02/14 05:10:14  krister
# Updated for a fresh mplayer version
#
# Revision 1.5  2003/02/05 20:02:16  krister
# Runtime fixes for the preloads. Disable locale stuff in mplayer.
#
# Revision 1.4  2003/01/30 02:48:47  krister
# Added more MPlayer fixes/patches.
#
# Revision 1.3  2003/01/29 05:35:45  krister
# Updated MPlayer
#
# Revision 1.2  2003/01/28 03:45:35  krister
# Work in progress...
#
# Revision 1.1  2003/01/24 07:20:21  krister
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


TARGETS = mplayer_fonts mplayer aumix

.PHONY: all copy clean


# Build all libs and apps
all: Archive $(TARGETS)


# Copy the generated files to the parent directory
copy: aumix_copy

# Remove all copied libraries, programs etc
# The build directory is not touched
clean:
	-rm -rf $(TARGETS)

Archive:
	mkdir -p Archive


################################################################################
#
# Python 2.2.2
#
################################################################################
python_build:
	@echo Building python



################################################################################
#
# Expat 1.95.5
#
################################################################################
expat_build:
	@echo Building expat


################################################################################
#
# freetype 2.1.3
#
################################################################################
freetype_build:
	@echo Building freetype


################################################################################
#
# zlib 1.1.4
#
################################################################################
zlib_build:
	@echo Building zlib


################################################################################
#
# libpng 1.2.5
#
################################################################################
libpng_build:
	@echo Building libpng


################################################################################
#
# libjpeg v6b
#
################################################################################
libjpeg_build:
	@echo Building libjpeg


################################################################################
#
# Alsa Library 0.9.0rc6
#
################################################################################
alsalib_build:
	@echo Building alsalib


################################################################################
#
# SDL 1.2.5, patched
#
################################################################################
sdl_build:
	@echo Building SDL


################################################################################
#
# SDL_image CVS 2002-08-05 snapshot
#
################################################################################
sdlimage_build:
	@echo Building SDL_image


################################################################################
#
# SDL_ttf2 CVS 2003-01-10 snapshot + patch
#
################################################################################
sdlttf_build:
	@echo Building SDL_ttf2


################################################################################
#
# SDL_mixer 1.2
#
################################################################################
sdlmixer_build:
	@echo Building SDL_mixer


################################################################################
#
# SMPEG 0.4.4
#
################################################################################
smpeg_build:
	@echo Building SMPEG


################################################################################
#
# Ogg Vorbis libao 0.8.3
#
################################################################################
libao_build:
	@echo Building libao


################################################################################
#
# Ogg Vorbis libogg 1.0
#
################################################################################
libogg_build:
	@echo Building libogg


################################################################################
#
# Ogg Vorbis libvorbis 1.0
#
################################################################################
libvorbis_build:
	@echo Building libvorbis


################################################################################
#
# libvorbisfile
#
################################################################################
libvorbisfile_build:
	@echo Building libvorbisfile


################################################################################
#
# libvorbisenc
#
################################################################################
libvorbisenc_build:
	@echo Building libvorbisenc


################################################################################
#
# libusb 0.1.7
#
################################################################################
libusb_build:
	@echo Building libusb


################################################################################
#
# libexif 0.5.9
#
################################################################################
libexif_build:
	@echo Building libexif


################################################################################
#
# libgphoto2 2.1.1
#
################################################################################
libgphoto2_build:
	@echo Building libgphoto2


################################################################################
#
# mplayer/mencoder
#
################################################################################
MPLAYER_DATE = "2003-02-13 22:30 CST"
FFMPEG_DATE = "2003-02-13 22:30 CST"
MPLAYER_CVS = cvs -z3 -d:pserver:anonymous@mplayerhq.hu:/cvsroot/mplayer co -D $(MPLAYER_DATE) main
FFMPEG_CVS = cvs -d:pserver:anonymous@cvs.ffmpeg.sourceforge.net:/cvsroot/ffmpeg co -D $(FFMPEG_DATE) ffmpeg
MPLAYER_CONF = 	--enable-tv-v4l --enable-mga --enable-xmga \
		--enable-runtime-cpudetection --enable-largefiles --disable-lirc \
		--disable-svga --disable-arts --disable-directfb --disable-xvid \
		--disable-divx4linux --disable-gif --disable-gl --disable-setlocale --disable-i18n \
		--datadir=./runtime/apps/mplayer --confdir=./runtime/apps/mplayer

# Build mplayer
# Patch mplayer_dvdprot.diff: Adds -nodvdprotection-override flag
# Patch mplayer_freevobanner.diff: Adds a Freevo notice
mplayer: Archive/mplayer-CVS200302132230.tgz
	@echo Building mplayer/mencoder
	tar xvzf $<
	(cd mplayer ; patch -p1 < ../../src/mplayer_dvdprot.diff ; \
	patch -p1 < ../../src/mplayer_freevobanner.diff ; \
	patch -p0 < ../../src/mplayer_cdda_seeking.diff ; \
	./configure $(MPLAYER_CONF) ; make)

Archive/mplayer-CVS200302132230.tgz:
	(export CVS_PASSFILE cvspass ; $(MPLAYER_CVS) ; \
	$(FFMPEG_CVS) ; mv ffmpeg/libavcodec main ; \
	rm -rf ffmpeg ; mv main mplayer ; tar cvzf $@ mplayer ; rm -rf mplayer)



################################################################################
#
# mplayer fonts
#
################################################################################
mplayer_fonts: Archive/font-arial-iso-8859-1.tar.bz2
	-mkdir mplayer_fonts
	(bzcat Archive/font-arial-iso-8859-1.tar.bz2 | tar -C mplayer_fonts -xvf -)

Archive/font-arial-iso-8859-1.tar.bz2:
	wget -O $@ http://www1.mplayerhq.hu/MPlayer/releases/fonts/font-arial-iso-8859-1.tar.bz2


################################################################################
#
# aumix
#
################################################################################
AUMIX_CONF = --without-ncurses --without-gpm --without-sysmouse --without-gtk \
		--without-gtk1 --disable-nls --with-alsa

.PHONY: aumix aumix_copy

aumix: aumix-2.8

aumix-2.8: Archive/aumix-2.8.tar.bz2 
	@echo Building $@
	tar xvjf $<
	(cd aumix-2.8 ; ./configure $(AUMIX_CONF); make)

Archive/aumix-2.8.tar.bz2:
	wget -O $@ http://www.jpj.net/~trevor/aumix/aumix-2.8.tar.bz2

aumix_copy: aumix-2.8
	cp -f $</src/aumix ../apps
