#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/__init__.py - Some Utilities
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/11/22 20:34:08  dischi
# use new vfs
#
# Revision 1.4  2003/11/02 10:50:40  dischi
# remove debug
#
# Revision 1.3  2003/11/02 09:24:35  dischi
# Check for libs and make it possible to install runtime from within
# freevo
#
# Revision 1.2  2003/10/18 13:04:42  dischi
# add distutils
#
# Revision 1.1  2003/10/11 11:20:11  dischi
# move util.py into a directory and split it into two files
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

import sys

# import the stuff from misc and fileops to be compatible
# with util in only one file

if sys.argv[0].find('setup.py') == -1 and sys.argv[0].find('install.py') == -1:
    import vfs
    import __builtin__
    __builtin__.__dict__['vfs'] = vfs
    
    from misc import *
    from fileops import *

