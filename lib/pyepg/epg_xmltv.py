# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# epg_xmltv.py - Freevo Electronic Program Guide module for XMLTV
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/26 12:45:56  dischi
# first draft of pyepg (not integrated in Freevo)
#
# Revision 1.53  2004/07/11 12:25:44  dischi
# fix bad German titles
#
# Revision 1.52  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.51  2004/06/23 20:22:19  dischi
# fix popup crash
#
# Revision 1.50  2004/06/22 01:10:21  rshortt
# Add ratings and advisories.
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


import sys
import time
import os
import traceback
import calendar
import shutil

import _strptime as strptime

# The XMLTV handler from openpvr.sourceforge.net
import xmltv as xmltv

# The EPG data types. They need to be in an external module in order for
# pickling to work properly when run from inside this module and from the
# tv.py module.
import epg_types as epg_types

EPG_TIME_EXC = _('Time conversion error')


cached_guide = None

def list_channels(XMLTV_FILE, TV_CHANNELS=None, verbose=True):
    if TV_CHANNELS:
        return TV_CHANNELS
    if not os.path.isfile(XMLTV_FILE):
        return []

    if verbose:
        print 'epg_xmltv.py: Adding all channels'
    xmltv_channels = None

    f = open(XMLTV_FILE)
    xmltv_channels = xmltv.read_channels(f)
    f.close()
        
    # Was the guide read successfully?
    if not xmltv_channels:
        return []

    TV_CHANNELS = []
    for chan in xmltv_channels:

        id   = chan['id'].encode('latin-1', 'ignore')
        c    = epg_types.TvChannel()
        c.id = id
        if ' ' in id:
            # Assume the format is "TUNERID CHANNELNAME"
            c.displayname = id.split()[1]   # XXX Educated guess
            c.tunerid     = id.split()[0]   # XXX Educated guess
        else:
            displayname = chan['display-name'][0][0]
            if ' ' in displayname:
                c.displayname = displayname.split()[1]
                c.tunerid     = displayname.split()[0]
            else:
                c.displayname = displayname
                c.tunerid     = _('REPLACE WITH TUNERID FOR %s') % displayname
        TV_CHANNELS.append((c.displayname, c.id, c.tunerid))
    return TV_CHANNELS


    
def load_guide(XMLTV_FILE, TV_CHANNELS=None, verbose=True):
    """
    Load a guide from the raw XMLTV file using the xmltv.py support lib.
    Returns a TvGuide or None if an error occurred
    """
    # Create a new guide
    guide = epg_types.TvGuide()

    # Is there a file to read from?
    if os.path.isfile(XMLTV_FILE):
        gotfile = 1
        guide.timestamp = os.path.getmtime(XMLTV_FILE)
    else:
        print 'XMLTV file (%s) missing!' % XMLTV_FILE
        gotfile = 0

    if not TV_CHANNELS:
        # get channel listing
        TV_CHANNELS = list_channels(XMLTV_FILE, verbose=True)
        
    if not TV_CHANNELS:
        # still no listing?
        return None
    
    # Add the channels that are in the config list, or all if the
    # list is empty
    if verbose:
        print 'epg_xmltv.py: Only adding channels in list'

    for data in TV_CHANNELS:
        (id, disp, tunerid) = data[:3]
        c = epg_types.TvChannel()
        c.id          = id
        c.displayname = disp
        c.tunerid     = tunerid
        
        # Handle the optional time-dependent station info
        c.times = []
        if len(data) > 3 and len(data[3:4]) == 3:
            for (days, start_time, stop_time) in data[3:4]:
                c.times.append((days, int(start_time), int(stop_time)))
        guide.AddChannel(c)


    xmltv_programs = None
    if gotfile:
        if verbose:
            print 'reading xmltv data'
        f = open(XMLTV_FILE)
        xmltv_programs = xmltv.read_programmes(f)
        f.close()
        
    # Was the guide read successfully?
    if not xmltv_programs:
        return guide    # Return the guide, it has the channels at least...


    needed_ids = []
    for chan in guide.chan_dict:
        needed_ids.append(chan)

    if verbose:
        print 'creating guide for %s' % needed_ids

    for p in xmltv_programs:
        if not p['channel'] in needed_ids:
            continue
        try:
            prog = epg_types.TvProgram()
            prog.channel_id = p['channel']
            prog.title = Unicode(p['title'][0][0])
            if p.has_key('date'):
                prog.date = Unicode(p['date'][0][0])
            if p.has_key('category'):
                prog.categories = [ cat[0] for cat in p['category'] ]
            if p.has_key('rating'):
                for r in p['rating']:
                    if r.get('system') == 'advisory':
                        prog.advisories.append(String(r.get('value')))
                        continue
                    prog.ratings[String(r.get('system'))] = String(r.get('value'))
            if p.has_key('desc'):
                # prog.desc = Unicode(util.format_text(p['desc'][0][0]))
                pass
            if p.has_key('sub-title'):
                prog.sub_title = p['sub-title'][0][0]
            try:
                prog.start = timestr2secs_utc(p['start'])
                try:
                    prog.stop = timestr2secs_utc(p['stop'])
                except:
                    # Fudging end time
                    prog.stop = timestr2secs_utc(p['start'][0:8] + '235900' + \
                                                 p['start'][14:18])
            except EPG_TIME_EXC:
                continue
            # fix bad German titles to make favorites working
            if prog.title.endswith('. Teil'):
                prog.title = prog.title[:-6]
                if prog.title.rfind(' ') > 0:
                    try:
                        part = int(prog.title[prog.title.rfind(' ')+1:])
                        prog.title = prog.title[:prog.title.rfind(' ')].rstrip()
                        if prog.sub_title:
                            prog.sub_title = u'Teil %s: %s' % (part, prog.sub_title)
                        else:
                            prog.sub_title = u'Teil %s' % part
                    except Exception, e:
                        print e

            guide.AddProgram(prog)
        except:
            traceback.print_exc()
            print 'Error in tv guide, skipping'
            
    guide.Sort()
    return guide


def timestr2secs_utc(timestr):
    """
    Convert a timestring to UTC (=GMT) seconds.

    The format is either one of these two:
    '20020702100000 CDT'
    '200209080000 +0100'
    """
    # This is either something like 'EDT', or '+1'
    try:
        tval, tz = timestr.split()
    except ValueError:
        tval = timestr
        tz   = str(-time.timezone/3600)

    if tz == 'CET':
        tz='+1'

    # Is it the '+1' format?
    if tz[0] == '+' or tz[0] == '-':
        tmTuple = ( int(tval[0:4]), int(tval[4:6]), int(tval[6:8]), 
                    int(tval[8:10]), int(tval[10:12]), 0, -1, -1, -1 )
        secs = calendar.timegm( tmTuple )

        adj_neg = int(tz) >= 0
        try:
            min = int(tz[3:5])
        except ValueError:
            # sometimes the mins are missing :-(
            min = 0
        adj_secs = int(tz[1:3])*3600+ min*60

        if adj_neg:
            secs -= adj_secs
        else:
            secs += adj_secs
    else:
        # No, use the regular conversion

        ## WARNING! BUG HERE!
        # The line below is incorrect; the strptime.strptime function doesn't
        # handle time zones. There is no obvious function that does. Therefore
        # this bug is left in for someone else to solve.

        try:
            secs = time.mktime(strptime.strptime(timestr, xmltv.date_format))
        except ValueError:
            timestr = timestr.replace('EST', '')
            secs    = time.mktime(strptime.strptime(timestr, xmltv.date_format))
    return secs
