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
# Revision 1.17  2003/04/22 01:33:35  rshortt
# Bugfixes.
#
# Revision 1.16  2003/04/21 19:31:37  rshortt
# Add mplayer and ffmpeg.
#
# Revision 1.15  2003/04/20 13:53:38  rshortt
# Added a build of DirectFB.
#
# Revision 1.14  2003/04/20 13:06:36  rshortt
# Added a DXR3 build. (build_dxr3)
#
# Revision 1.13  2003/04/19 20:08:30  rshortt
# Better COPY_BASE
#
# Revision 1.12  2003/04/19 19:54:42  rshortt
# Modifications for a runtime build system.  Still WIP but almost done.
#
# Revision 1.11  2003/03/04 05:44:36  krister
# Added fchksum
#
# Revision 1.10  2003/02/21 04:36:43  krister
# Bugfix for missing network libs.
#
# Revision 1.9  2003/02/19 08:08:29  krister
# Applied Aubins new pylirc code after testing it (seems to work with keyboard at least), and adding the pylircmodule to the runtime build environment (not required for keyboard operation).
#
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

include package_list.mk

COPY_BASE=`pwd`

EXT=
PACKAGE=
PACKAGE_GET=
TAR1="tar zxvf"
TAR2="tar jxvf"

PREFIX=$(COPY_BASE)/build

CFGFLAGS="--prefix=$(PREFIX)"

PYBIN=$(PREFIX)/bin/python
LIRCLIB=/opt/lirc/lib
LIRCINC=/opt/lirc/include

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
	lame_copy jpegtran_copy copy_libdeps
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
	-rm -rf lib apps/* dll/* tmp preloads


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
	-rm -rf tmp
	-mkdir -p lib
	-mkdir -p apps
	cp -a $(PREFIX)/lib/python2.2 lib
	find . -name "*.pyo" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
	rm -rf lib/python2.2/config
	rm -rf lib/python2.2/lib-tk
	rm -rf lib/python2.2/lib-old
	rm -rf lib/python2.2/test
	-mkdir -p tmp
	cp -a lib/python2.2/site-packages/{CDDB.py,DiscID.py,Numeric,Numeric.pth} tmp
	cp -a lib/python2.2/site-packages/{PIL,PIL.pth,_xmlplus,aomodule.so} tmp
	cp -a lib/python2.2/site-packages/{cdrom.so,mx,ogg,pygame} tmp
	cp -a lib/python2.2/site-packages/{pylircmodule.so,fchksum.so} tmp
	rm -rf lib/python2.2/site-packages
	mv tmp lib/python2.2/site-packages
	cp -a $(PREFIX)/bin/python2.2 apps/freevo_python


################################################################################
#
# MPlayer/Mencoder
#
################################################################################
mplayer_copy:
	@echo Copying mplayer/mencoder
	-mkdir -p apps/mplayer
	cp $(PREFIX)/MPlayer/bin/{mplayer,mencoder} ./apps/mplayer/
	# cp $(PREFIX)/MPlayer/bin/README ./apps/mplayer/README.mplayer
	# cp $(PREFIX)/MPlayer/bin/etc/{codecs.conf,input.conf} ./apps/mplayer/


################################################################################
#
# MPlayer fonts
#
################################################################################
mplayer_fonts_copy:
	@echo Copying mplayer fonts
	-mkdir -p apps/mplayer/font
	cp $(PREFIX)/MPlayer/font/* apps/mplayer/font


################################################################################
#
# cdparanoia
#
################################################################################
cdparanoia_copy:
	@echo Copying cdparanoia
	cp -a $(PREFIX)/bin/cdparanoia apps/


################################################################################
#
# lame
#
################################################################################
lame_copy:
	@echo Copying lame
	cp -a $(PREFIX)/bin/lame apps/


################################################################################
#
# jpegtran. comes from the libjpeg v6b library.
#
################################################################################
jpegtran_copy:
	@echo Copying jpegtran
	cp -a $(PREFIX)/bin/jpegtran apps/


build_all_pkg: build_packageconfig build_libusb build_python build_jpeg build_png build_zlib build_ffmpeg build_dxr3 build_directfb build_sdl build_alsa build_aumix build_cddb build_cdparanoia build_egenix build_expat build_freetype build_lame build_libao build_libexif build_libgphoto build_libogg build_libvorbis build_pyogg build_pyvorbis build_pyao build_pyfchksum build_pyimaging build_pylirc build_pynumeric build_pyxml build_pyxmms build_sdlimage build_sdlttf build_smpeg build_sdlmixer build_pygame build_swig build_pygphoto build_vorbistools build_mp1e build_mplayer get_mplayer_fonts



build_python: PACKAGE=$(PYTHON)
build_python: PACKAGE_GET=$(PYTHON_GET)
build_python: EXT=tgz
build_python: TAR=$(TAR1)
build_python: BUILDCMDS=
build_python: CFG=$(CFGFLAGS)
build_python:  
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_expat: PACKAGE=$(EXPAT)
build_expat: PACKAGE_GET=$(EXPAT_GET)
build_expat: EXT=tar.gz
build_expat: TAR=$(TAR1)
build_expat: BUILDCMDS=
build_expat: CFG=$(CFGFLAGS)
build_expat: 
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_mp1e: PACKAGE=$(MP1E)
build_mp1e: PACKAGE_GET=$(MP1E_GET)
build_mp1e: EXT=tar.gz
build_mp1e: TAR=$(TAR1)
build_mp1e: BUILDCMDS=
build_mp1e: CFG=$(CFGFLAGS)
build_mp1e: 
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyxml: PACKAGE=$(PYXML)
build_pyxml: PACKAGE_GET=$(PYXML_GET)
build_pyxml: EXT=tar.gz
build_pyxml: TAR=$(TAR1)
build_pyxml: BUILDCMDS="$(PYBIN) setup.py build; $(PYBIN) setup.py install"
build_pyxml: CFG=$(CFGFLAGS)
build_pyxml:  
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_alsa: PACKAGE=$(ALSA)
build_alsa: PACKAGE_GET=$(ALSA_GET)
build_alsa: EXT=tar.bz2
build_alsa: TAR=$(TAR2)
build_alsa: BUILDCMDS=
build_alsa: CFG=$(CFGFLAGS)
build_alsa: 
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_aumix: PACKAGE=$(AUMIX)
build_aumix: PACKAGE_GET=$(AUMIX_GET)
build_aumix: EXT=tar.bz2
build_aumix: TAR=$(TAR2)
build_aumix: BUILDCMDS=
build_aumix: CFG="$(CFGFLAGS) --without-ncurses --without-gpm --without-sysmouse --without-gtk --without-gtk1 --disable-nls --with-alsa"
build_aumix: 
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                aumix-2.8 $(CFG) $(BUILDCMDS)


build_cddb: PACKAGE=$(CDDB)
build_cddb: PACKAGE_GET=$(CDDB_GET)
build_cddb: EXT=tar.gz
build_cddb: TAR=$(TAR1)
build_cddb: BUILDCMDS="$(PYBIN) setup.py build; $(PYBIN) setup.py install"
build_cddb: CFG=$(CFGFLAGS)
build_cddb:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                CDDB-1.3 $(CFG) $(BUILDCMDS)


build_cdparanoia: PACKAGE=$(CDPARANOIA)
build_cdparanoia: PACKAGE_GET=$(CDPARANOIA_GET)
build_cdparanoia: EXT=src.tgz
build_cdparanoia: TAR=$(TAR1)
build_cdparanoia: BUILDCMDS=
build_cdparanoia: CFG=$(CFGFLAGS)
build_cdparanoia:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_egenix: PACKAGE=$(EGENIX)
build_egenix: PACKAGE_GET=$(EGENIX_GET)
build_egenix: EXT=tar.gz
build_egenix: TAR=$(TAR1)
build_egenix: BUILDCMDS="$(PYBIN) setup.py build; $(PYBIN) setup.py install"
build_egenix: CFG=$(CFGFLAGS)
build_egenix:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_freetype: PACKAGE=$(FREETYPE)
build_freetype: PACKAGE_GET=$(FREETYPE_GET)
build_freetype: EXT=tar.gz
build_freetype: TAR=$(TAR1)
build_freetype: BUILDCMDS=
build_freetype: CFG=$(CFGFLAGS)
build_freetype:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_jpeg: PACKAGE=$(JPEG)
build_jpeg: PACKAGE_GET=$(JPEG_GET)
build_jpeg: EXT=tar.gz
build_jpeg: TAR=$(TAR1)
build_jpeg: BUILDCMDS=
build_jpeg: CFG="$(CFGFLAGS) --enable-shared"
build_jpeg:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                jpeg-6b $(CFG) $(BUILDCMDS)


build_lame: PACKAGE=$(LAME)
build_lame: PACKAGE_GET=$(LAME_GET)
build_lame: EXT=tar.gz
build_lame: TAR=$(TAR1)
build_lame: BUILDCMDS=
build_lame: CFG=$(CFGFLAGS)
build_lame:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_libao: PACKAGE=$(LIBAO)
build_libao: PACKAGE_GET=$(LIBAO_GET)
build_libao: EXT=tar.gz
build_libao: TAR=$(TAR1)
build_libao: BUILDCMDS=
build_libao: CFG=$(CFGFLAGS)
build_libao:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_libexif: PACKAGE=$(LIBEXIF)
build_libexif: PACKAGE_GET=$(LIBEXIF_GET)
build_libexif: EXT=tar.gz
build_libexif: TAR=$(TAR1)
build_libexif: BUILDCMDS=
build_libexif: CFG=$(CFGFLAGS)
build_libexif:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_libgphoto: PACKAGE=$(LIBGPHOTO)
build_libgphoto: PACKAGE_GET=$(LIBGPHOTO_GET)
build_libgphoto: EXT=tar.gz
build_libgphoto: TAR=$(TAR1)
build_libgphoto: BUILDCMDS=
build_libgphoto: CFG=$(CFGFLAGS)
build_libgphoto:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_libogg: PACKAGE=$(LIBOGG)
build_libogg: PACKAGE_GET=$(LIBOGG_GET)
build_libogg: EXT=tar.gz
build_libogg: TAR=$(TAR1)
build_libogg: BUILDCMDS=
build_libogg: CFG=$(CFGFLAGS)
build_libogg:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_libusb: PACKAGE=$(LIBUSB)
build_libusb: PACKAGE_GET=$(LIBUSB_GET)
build_libusb: EXT=tar.gz
build_libusb: TAR=$(TAR1)
build_libusb: BUILDCMDS=
build_libusb: CFG=$(CFGFLAGS)
build_libusb:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_libvorbis: PACKAGE=$(LIBVORBIS)
build_libvorbis: PACKAGE_GET=$(LIBVORBIS_GET)
build_libvorbis: EXT=tar.gz
build_libvorbis: TAR=$(TAR1)
build_libvorbis: BUILDCMDS=
build_libvorbis: CFG=$(CFGFLAGS)
build_libvorbis:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_packageconfig: PACKAGE=$(PKGCONFIG)
build_packageconfig: PACKAGE_GET=$(PKGCONFIG_GET)
build_packageconfig: EXT=tar.gz
build_packageconfig: TAR=$(TAR1)
build_packageconfig: BUILDCMDS=
build_packageconfig: CFG=$(CFGFLAGS)
build_packageconfig:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_png: PACKAGE=$(PNG)
build_png: PACKAGE_GET=$(PNG_GET)
build_png: EXT=tar.gz
build_png: TAR=$(TAR1)
build_png: BUILDCMDS="cp scripts/makefile.linux Makefile; make prefix=$(PREFIX); make install prefix=$(PREFIX)"
build_png: CFG=$(CFGFLAGS)
build_png:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyao: PACKAGE=$(PYAO)
build_pyao: PACKAGE_GET=$(PYAO_GET)
build_pyao: EXT=tar.gz
build_pyao: TAR=$(TAR1)
build_pyao: BUILDCMDS="$(PYBIN) config_unix.py; $(PYBIN) setup.py build; $(PYBIN) setup.py install" 
build_pyao: CFG=$(CFGFLAGS)
build_pyao:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyfchksum: PACKAGE=$(PYFCHKSUM)
build_pyfchksum: PACKAGE_GET=$(PYFCHKSUM_GET)
build_pyfchksum: EXT=tar.gz
build_pyfchksum: TAR=$(TAR1)
build_pyfchksum: BUILDCMDS="$(PYBIN) setup.py build; $(PYBIN) setup.py install" 
build_pyfchksum: CFG=$(CFGFLAGS)
build_pyfchksum:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pygame: PACKAGE=$(PYGAME)
build_pygame: PACKAGE_GET=$(PYGAME_GET)
build_pygame: EXT=tar.gz
build_pygame: TAR=$(TAR1)
build_pygame: BUILDCMDS=
build_pygame: BUILDCMDS="$(PYBIN) setup.py build; $(PYBIN) setup.py install" 
build_pygame: CFG=$(CFGFLAGS)
build_pygame:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyimaging: PACKAGE=$(PYIMAGING)
build_pyimaging: PACKAGE_GET=$(PYIMAGING_GET)
build_pyimaging: EXT=tar.gz
build_pyimaging: TAR=$(TAR1)
build_pyimaging: BUILDCMDS="./configure --prefix=$(PREFIX); make; cd ..; $(PYBIN) setup.py build; $(PYBIN) setup.py install;"
build_pyimaging: CFG=$(CFGFLAGS)
build_pyimaging:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE)/libImaging $(CFG) $(BUILDCMDS)


build_pylirc: PACKAGE=$(PYLIRC)
build_pylirc: PACKAGE_GET=$(PYLIRC_GET)
build_pylirc: EXT=tar.gz
build_pylirc: TAR=$(TAR1)
build_pylirc: BUILDCMDS="ln -s $(LIRCINC)/lirc .; $(PYBIN) setup.py install; gcc -shared build/temp.linux-i686-2.2/pylircmodule.o -I$(LIRCINC) -L$(LIRCLIB) -llirc_client -o build/lib.linux-i686-2.2/pylircmodule.so; $(PYBIN) setup.py install"
build_pylirc: CFG=$(CFGFLAGS)
build_pylirc:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pynumeric: PACKAGE=$(PYNUMERIC)
build_pynumeric: PACKAGE_GET=$(PYNUMERIC_GET)
build_pynumeric: EXT=tar.gz
build_pynumeric: TAR=$(TAR1)
build_pynumeric: BUILDCMDS="$(PYBIN) setup.py build; $(PYBIN) setup.py install" 
build_pynumeric: CFG=$(CFGFLAGS)
build_pynumeric:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyogg: PACKAGE=$(PYOGG)
build_pyogg: PACKAGE_GET=$(PYOGG_GET)
build_pyogg: EXT=tar.gz
build_pyogg: TAR=$(TAR1)
build_pyogg: BUILDCMDS="$(PYBIN) config_unix.py; $(PYBIN) setup.py build; $(PYBIN) setup.py install" 
build_pyogg: CFG=$(CFGFLAGS)
build_pyogg:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyvorbis: PACKAGE=$(PYVORBIS)
build_pyvorbis: PACKAGE_GET=$(PYVORBIS_GET)
build_pyvorbis: EXT=tar.gz
build_pyvorbis: TAR=$(TAR1)
build_pyvorbis: BUILDCMDS="$(PYBIN) config_unix.py; $(PYBIN) setup.py build; $(PYBIN) setup.py install" 
build_pyvorbis: CFG=$(CFGFLAGS)
build_pyvorbis:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_pyxmms: PACKAGE=$(PYXMMS)
build_pyxmms: PACKAGE_GET=$(PYXMMS_GET)
build_pyxmms: EXT=tar.gz
build_pyxmms: TAR=$(TAR1)
build_pyxmms: BUILDCMDS="echo XMMS support is broken."
build_pyxmms: CFG=$(CFGFLAGS)
build_pyxmms:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_sdl: PACKAGE=$(SDL)
build_sdl: PACKAGE_GET=$(SDL_GET)
build_sdl: EXT=tar.gz
build_sdl: TAR=$(TAR1)
build_sdl: BUILDCMDS=
build_sdl: CFG="$(CFGFLAGS) --enable-video-dxr3 --enable-video-directfb"
build_sdl:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_sdlimage: PACKAGE=$(SDLIMAGE)
build_sdlimage: PACKAGE_GET=$(SDLIMAGE_GET)
build_sdlimage: EXT=tgz
build_sdlimage: TAR=$(TAR1)
build_sdlimage: BUILDCMDS=
build_sdlimage: CFG=$(CFGFLAGS)
build_sdlimage:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_sdlmixer: PACKAGE=$(SDLMIXER)
build_sdlmixer: PACKAGE_GET=$(SDLMIXER_GET)
build_sdlmixer: EXT=tar.gz
build_sdlmixer: TAR=$(TAR1)
build_sdlmixer: BUILDCMDS=
build_sdlmixer: CFG=$(CFGFLAGS)
build_sdlmixer:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_sdlttf: PACKAGE=$(SDLTTF)
build_sdlttf: PACKAGE_GET=$(SDLTTF_GET)
build_sdlttf: EXT=tar.gz
build_sdlttf: TAR=$(TAR1)
build_sdlttf: BUILDCMDS=
build_sdlttf: CFG=$(CFGFLAGS)
build_sdlttf:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_smpeg: PACKAGE=$(SMPEG)
build_smpeg: PACKAGE_GET=$(SMPEG_GET)
build_smpeg: EXT=tar.gz
build_smpeg: TAR=$(TAR1)
build_smpeg: BUILDCMDS=
build_smpeg: CFG=$(CFGFLAGS)
build_smpeg:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_swig: PACKAGE=$(SWIG)
build_swig: PACKAGE_GET=$(SWIG_GET)
build_swig: EXT=tar.gz
build_swig: TAR=$(TAR1)
build_swig: BUILDCMDS=
build_swig: CFG="$(CFGFLAGS) --with-python=$(PREFIX)/bin/python"
build_swig:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                SWIG-1.3.17 $(CFG) $(BUILDCMDS)


build_pygphoto: PACKAGE=$(PYGPHOTO)
build_pygphoto: PACKAGE_GET=$(PYGPHOTO_GET)
build_pygphoto: EXT=tar.gz
build_pygphoto: TAR=$(TAR1)
build_pygphoto: BUILDCMDS="make COPY_BASE=$(PREFIX); cp pygphoto.so $(PREFIX)/lib/python2.2/site-packages/"
build_pygphoto: CFG=$(CFGFLAGS)
build_pygphoto:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_vorbistools: PACKAGE=$(VORBISTOOLS)
build_vorbistools: PACKAGE_GET=$(VORBISTOOLS_GET)
build_vorbistools: EXT=tar.gz
build_vorbistools: TAR=$(TAR1)
build_vorbistools: BUILDCMDS=
build_vorbistools: CFG=$(CFGFLAGS)
build_vorbistools:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_dxr3: PACKAGE=$(DXR3)
build_dxr3: PACKAGE_GET=$(DXR3_GET)
build_dxr3: EXT=tar.gz
build_dxr3: TAR=$(TAR1)
build_dxr3: BUILDCMDS=
build_dxr3: CFG="$(CFGFLAGS)"
build_dxr3:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_zlib: PACKAGE=$(ZLIB)
build_zlib: PACKAGE_GET=$(ZLIB_GET)
build_zlib: EXT=tar.gz
build_zlib: TAR=$(TAR1)
build_zlib: BUILDCMDS=
build_zlib: CFG="$(CFGFLAGS) --shared"
build_zlib:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_directfb: PACKAGE=$(DIRECTFB)
build_directfb: PACKAGE_GET=$(DIRECTFB_GET)
build_directfb: EXT=tar.gz
build_directfb: TAR=$(TAR1)
build_directfb: BUILDCMDS=
build_directfb: CFG="$(CFGFLAGS)"
build_directfb:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_ffmpeg: PACKAGE=$(FFMPEG)
build_ffmpeg: PACKAGE_GET=$(FFMPEG_GET)
build_ffmpeg: EXT=tar.gz
build_ffmpeg: TAR=$(TAR1)
build_ffmpeg: BUILDCMDS=
build_ffmpeg: CFG="$(CFGFLAGS)"
build_ffmpeg:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


build_mplayer: PACKAGE=$(MPLAYER)
build_mplayer: PACKAGE_GET=$(MPLAYER_GET)
build_mplayer: EXT=tar.gz
build_mplayer: TAR=$(TAR1)
build_mplayer: BUILDCMDS=
build_mplayer: CFG="--prefix=$(PREFIX)/MPlayer --enable-tv-v4l --enable-mga --enable-xmga --enable-runtime-cpudetection --enable-largefiles --disable-lirc --disable-svga --disable-arts --enable-directfb --enable-dxr3 --disable-xvid --disable-divx4linux --disable-gif --disable-gl --datadir=./apps/mplayer --confdir=./apps/mplayer"
build_mplayer:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                $(PACKAGE) $(CFG) $(BUILDCMDS)


get_mplayer_fonts: PACKAGE=$(MFONTS)
get_mplayer_fonts: PACKAGE_GET=$(MFONTS_GET)
get_mplayer_fonts: EXT=tar.bz2
get_mplayer_fonts: TAR=$(TAR2)
get_mplayer_fonts: BUILDCMDS="mkdir -p ../build/MPlayer; mv font-arial-18-iso-8859-1 ../build/MPlayer/font; rm ../build/MPlayer/font/runme"
get_mplayer_fonts: CFG="$(CFGFLAGS)"
get_mplayer_fonts:
	@ . build_functions ;\
	  get_package $(PACKAGE) $(PACKAGE_GET) $(EXT) ;\
	  build_package $(COPY_BASE) $(TAR) $(EXT) $(PACKAGE) \
	                . $(CFG) $(BUILDCMDS)
