# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/tv.py - A module to make some tasks related to TV easier.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.5  2004/06/23 21:10:20  dischi
# make nicer filename
#
# Revision 1.4  2004/06/22 01:03:25  rshortt
# getProgFilename() now returns the entire filename (path) including
# TV_RECORD_DIR and TV_RECORDFILE_SUFFIX.
#
# Revision 1.3  2004/06/20 13:56:54  dischi
# remove -_ at the end of the filename
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


import sys, string, re
import time, os, string

import util, config, tv.epg_xmltv

DEBUG = 0


def progname2filename(progname):
    '''Translate a program name to something that can be used as a filename.'''

    # Letters that can be used in the filename
    ok = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-:'

    s = ''
    for letter in progname:
        if letter in ok:
            s += letter
        else:
            if s and s[-1] != '_':
                s += '_'

    return s


def getKey(prog=None):
    if not prog:
        return 'ERROR: no prog'

    return '%s:%s' % (prog.channel_id, prog.start)

  
def progRunning(prog):
    now = time.time()
    if prog.start <= now and prog.stop >= now:
        return True
    return False


def getProgFilename(prog):
    filename_array = { 'progname': String(prog.title),
                       'title'   : String(prog.sub_title) }

    filemask = config.TV_RECORDFILE_MASK % filename_array
    filemask = time.strftime(filemask, time.localtime(prog.start))
    filename = os.path.join(config.TV_RECORD_DIR, 
                            progname2filename(filemask).rstrip(' -_:') + 
                            config.TV_RECORDFILE_SUFFIX)
    return filename


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


def get_chan_displayname(channel_id):

    for vals in config.TV_CHANNELS:
        tv_channel_id, tv_display_name, tv_tuner_id = vals[:3]
        if tv_channel_id == channel_id:
            return tv_display_name

    guide = tv.epg_xmltv.get_guide()
    c = guide.chan_dict.get(channel_id)
    if c:
        return c.displayname
    # this shouldn't happen, but just in case
    return 'Unknown'


def when_listings_expire():
    guide = tv.epg_xmltv.get_guide()
    last = 0
    left = 0

    for ch in guide.chan_list:
        for prog in ch.programs:
            if prog.start > last: last = prog.start

    if last > 0:
        now = time.time()
        if last > now:
            left = int(last - now)
            # convert to hours
            left /= 3600

    return left

