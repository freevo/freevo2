# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/tv.py - A module to make some tasks related to TV easier.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2004/10/29 18:12:49  dischi
# move comingup to tv_utils
#
# Revision 1.11  2004/10/23 14:31:59  rshortt
# Move some EPG functionality into channels.py.
#
# Revision 1.10  2004/08/14 01:21:47  rshortt
# Remove get_guide, fix get_chan_displayname, and use the chanlist/epg from the cache.
#
# Revision 1.9  2004/08/08 19:48:31  rshortt
# Make this work again (for now).
#
# Revision 1.8  2004/08/08 19:04:25  rshortt
# Adding get_guide() and caching here temporarily until we have a working
# replacement since various parts of Freevo need it and I need it to fix
# them else I'll lose my sanity. :)
#
# Revision 1.7  2004/08/05 17:40:26  dischi
# deactivate some code for now
#
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
import time, os, string, traceback

import util, config
import sysconfig

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



def comingup(items=None, ScheduledRecordings=None):
    import tv.record_client as ri
    import time
    import codecs

    result = u''

    cachefile = '%s/upsoon' % sysconfig.CACHEDIR
    if not ScheduledRecordings:
        if (os.path.exists(cachefile) and \
            (abs(time.time() - os.path.getmtime(cachefile)) < 600)):
            cache = codecs.open(cachefile,'r', sysconfig.ENCODING)
            for a in cache.readlines():
                result = result + a
            cache.close()
            return result

        (status, recordings) = ri.getScheduledRecordings()
    else:
        (status, recordings) = ScheduledRecordings

    if not status:
        result = _('The recordserver is down')
        return result

    progs = recordings.getProgramList()

    f = lambda a, b: cmp(a.start, b.start)
    progl = progs.values()
    progl.sort(f)

    today = []
    tomorrow = []
    later = []

    for what in progl:
        if time.localtime(what.start)[2] == time.localtime()[2]:
            today.append(what)
        if time.localtime(what.start)[2] == (time.localtime()[2] + 1):
            tomorrow.append(what)
        if time.localtime(what.start)[2] > (time.localtime()[2] + 1):
            later.append(what)

    if len(today) > 0:
        result = result + _('Today') + u':\n'
        for m in today:
            sub_title = ''
            if hasattr(m,'sub_title') and m.sub_title:
                sub_title = u' "' + Unicode(m.sub_title) + u'" '
            result = result + u"- %s%s at %s\n" % \
                     ( Unicode(m.title), Unicode(sub_title),
                       Unicode(time.strftime('%I:%M%p',time.localtime(m.start))) )

    if len(tomorrow) > 0:
        result = result + _('Tomorrow') + u':\n'
        for m in tomorrow:
            sub_title = ''
            if hasattr(m,'sub_title') and m.sub_title:
                sub_title = ' "' + m.sub_title + '" '
            result = result + u"- %s%s at %s\n" % \
                     ( Unicode(m.title), Unicode(sub_title),
                       Unicode(time.strftime('%I:%M%p',time.localtime(m.start))) )

    if len(later) > 0:
        result = result + _('This Week') + u':\n'
        for m in later:
            sub_title = ''
            if hasattr(m,'sub_title') and m.sub_title:
                sub_title = ' "' + m.sub_title + '" '
            result = result + u"- %s%s at %s\n" % \
                     ( Unicode(m.title), Unicode(sub_title),
                       Unicode(time.strftime('%I:%M%p',time.localtime(m.start))) )

    if not result:
        result = _('No recordings are scheduled')

    if os.path.isfile(cachefile):
        os.unlink(cachefile)
    cache = codecs.open(cachefile,'w', sysconfig.ENCODING)
    cache.write(result)
    cache.close()

    return result


