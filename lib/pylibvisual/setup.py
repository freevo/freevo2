# -----------------------------------------------------------------------
# setup.py - Install file for libvisual in Freevo
# -----------------------------------------------------------------------
# $Id:
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log:
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

import glob, os, sys
from distutils.core import setup, Extension

# sources
sources = [ 'libvisual.c' ]

# includes
includes = [ '/usr/include/' ]

# libraries
library_dirs=['/usr/lib/']

for i in ('/usr', '/usr/local'):
    if os.path.isdir(os.path.join(i, 'include/libvisual')) and \
           os.path.isdir(os.path.join(i, 'lib/libvisual')):
        print 'found libvisual with prefix', i
        includes.append(os.path.join(i, 'include/libvisual'))
        library_dirs.append(os.path.join(i, 'lib'))
        library_dirs.append(os.path.join(i, 'lib/libvisual'))
        break
else:
    print 'libvisual not found, unable to build pylibvisual'
    sys.exit(1)
    
CFLAGS = ['-O2','-Wall']

include_dirs = []
library_dirs = []
libraries    = ['visual']

visual_ext = Extension('libvisual',
                     include_dirs       = includes,
                     sources            = sources,
                     library_dirs       = library_dirs,
                     extra_compile_args = CFLAGS,
                     libraries          = libraries )


# Setup #########################################################
setup ( name = 'libvisual',
        version = '0.2-alpha',
        description = 'libvisual bindings for Freevo',
        ext_modules = [visual_ext],
        )
