#if 0 /*
# -----------------------------------------------------------------------
# tv_util.py - 
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/09/08 19:44:44  dischi
# exception handling, just in case...
#
# Revision 1.6  2003/09/05 02:48:12  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.5  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.4  2003/07/24 00:01:19  rshortt
# Extending the idlebar.tv plugin with the help (and idea) of Mike Ruelle.
# Now you may add args=(number,) to the plugin.activate for this plugin and
# it will warn you that number of hours before your xmltv data is invalid and
# present a more sever warning when your xmltv data is expired.
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

import sys, string, re
import time, os, string

import util, config, tv.epg_xmltv

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

