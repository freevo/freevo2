#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# vtrelease.py - release the ttys after pygame crash
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
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


import os
import sys
from fcntl import ioctl

if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'release the vt in case freevo crashed and still locks'
    print 'the framebuffer.'
    print
    print 'this script has no options'
    print
    sys.exit(0)


for i in range(1,7):
    try:
        fd = os.open('/dev/tty%s' % i, os.O_RDONLY | os.O_NONBLOCK)
        # set ioctl (tty, KDSETMODE, KD_TEXT)
        ioctl(fd, 0x4B3A, 0)
        os.close(fd)
    except:
        pass
