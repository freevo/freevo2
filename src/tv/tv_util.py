#if 0 /*
# -----------------------------------------------------------------------
# tv_util.py - 
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/05/11 22:40:49  rshortt
# Helpers for tv and recording apps.
#
# Revision 1.1  2003/04/26 13:01:09  rshortt
# *** empty log message ***
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

import sys, string
import time, os, string

# Various utilities
import util

# RegExp
import re

DEBUG = 0

TRUE = 1
FALSE = 0


def getKey(prog=None):
    if not prog:
        return 'ERROR: no prog'

    return '%s:%s' % (prog.channel_id, prog.start)

  
def progRunning(prog=None):
    if not prog:
        return 'ERROR: no prog'

    now = time.time()
    if prog.start <= now and prog.stop >= now:
        return TRUE
    return FALSE


def getProgFilename(prog=None):
    if not prog:
        return 'ERROR: no prog'

    return '%s--%s' % (prog.title, time.strftime('%Y-%m-%d-%H%M', time.localtime(prog.start)))


def minToTOD(min):
    min = int(min)

    hour = min/60
    rem = min - (hour*60)

    ap = 'AM'
    if hour > 12:
        hour = hour - 12
        ap = 'PM'

    if hour == 0:
        hour = 12

    if rem == 0:
        rem = '00'

    return '%s:%s %s' % (hour, rem, ap)

def descfsize(size):
    if size < 1024:
        return "%d bytes" % size
    elif size < 1048576:
        size = size / 1024
        return "%s KB" % size
    elif size < 1073741824:
        size = size / 1048576.0
        return "%.1f MB" % size
    else:
        size = size / 1073741824.0
        return "%.3f GB" % size

