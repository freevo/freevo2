# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# osd.py - Low level graphics routines
# -----------------------------------------------------------------------
# $Id$
#
# Notes: do not use the OSD object inside a thread
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.168  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# Revision 1.167  2004/07/24 12:23:09  dischi
# replaced osd.py with a dummy
#
# Revision 1.166  2004/07/22 21:21:46  dischi
# small fixes to fit the new gui code
#
# Revision 1.165  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.164  2004/07/08 12:44:40  rshortt
# Add directfb as a display option.
#
# Revision 1.163  2004/06/29 18:29:20  dischi
# auto repair broken thumbnails
#
# Revision 1.162  2004/06/13 18:40:37  dischi
# fix crash
#
# Revision 1.161  2004/06/10 10:01:31  dischi
# cleanup
#
# Revision 1.160  2004/06/09 19:50:17  dischi
# change thumbnail caching format to be much faster: do not use pickle and
# also reduce the image size from max 300x300 to 255x255
#
# Revision 1.159  2004/06/06 16:13:27  dischi
# handle missing surfarray (Python Numeric)
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


# Python modules
import time
import os
import stat
import Image
import re
import traceback
import threading, thread
from types import *
from fcntl import ioctl
import cStringIO

# Freevo modules
import config
import util


# Module variable that contains an initialized OSD() object
_singleton = None

def get_singleton():
    global _singleton

    # don't start osd for helpers
    if config.HELPER:
        return

    import gui
    # One-time init
    if _singleton == None:
        _singleton = gui.get_renderer()
        
    return _singleton


def stop():
    """
    stop the osd because only one program can use the
    device, e.g. for DXR3 and dfbmga output,
    """
    get_singleton().stopdisplay()
    

def restart():
    """
    restart a stopped osd
    """
    get_singleton().restartdisplay()
    get_singleton().update()
    

