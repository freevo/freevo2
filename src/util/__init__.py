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
# Revision 1.22  2004/10/26 19:14:51  dischi
# adjust to new sysconfig file
#
# Revision 1.21  2004/10/06 19:13:07  dischi
# remove util.open3, move run and stdout to misc for now
#
# Revision 1.20  2004/09/07 18:52:51  dischi
# move thumbnail to extra file
#
# Revision 1.19  2004/08/26 15:30:39  dischi
# add weakref
#
# Revision 1.18  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.17  2004/06/13 18:49:39  dischi
# do not take care of install.py
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

import __builtin__
import vfs
__builtin__.__dict__['vfs'] = vfs

from misc import *
from fileops import *
from weakref import *
import objectcache
import fxdparser

# FIXME: remove this bad hack
import sys as _sys
if _sys.argv[0].find('setup.py') == -1:
    import mediainfo

