#if 0 /*
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
# Revision 1.50  2004/06/22 01:10:21  rshortt
# Add ratings and advisories.
#
# Revision 1.49  2004/03/16 01:04:18  rshortt
# Changes to stop two processes tripping over the creation of the epg pickle file.
#
# Revision 1.48  2004/03/13 22:28:41  dischi
# better handling of bad programs
#
# Revision 1.47  2004/03/05 20:49:11  rshortt
# Add support for searching by movies only.  This uses the date field in xmltv
# which is what tv_imdb uses and is really acurate.  I added a date property
# to TvProgram for this and updated findMatches in the record_client and
# recordserver.
#
# Revision 1.46  2004/02/23 21:41:10  dischi
# start some unicode fixes, still not working every time
#
# Revision 1.45  2004/02/22 06:22:16  gsbarbieri
# Handle info in unicode (don't need to convert to string anymore).
# People envolved to Record & Favorites, please test it and ensure it works.
#
# Revision 1.44  2004/02/19 04:57:57  gsbarbieri
# Support i18n.
#
# Revision 1.43  2004/02/09 20:14:06  dischi
# add verbose flag
#
# Revision 1.42  2004/02/06 20:54:26  dischi
# fix for undefined timezone
#
# Revision 1.41  2004/02/05 19:26:42  dischi
# fix unicode handling
#
# Revision 1.40  2003/12/31 16:08:08  rshortt
# Use a fifth field in TV_CHANNELS to specify an optional VideoGroup
# (VIDEO_GROUPS index).  Also fix a frequency bug in channels.py.
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
import time
import os
import traceback
import calendar
import shutil

import config
import util

# Use the alternate strptime module which seems to handle time zones
# XXX Remove when we are ready to require Python 2.3
if float(sys.version[0:3]) < 2.3:
    import strptime
else:
    import _strptime as strptime

# The XMLTV handler from openpvr.sourceforge.net
import tv.xmltv as xmltv

# The EPG data types. They need to be in an external module in order for
# pickling to work properly when run from inside this module and from the
# tv.py module.
import tv.epg_types as epg_types

EPG_TIME_EXC = _('Time conversion error')


cached_guide = None


def get_guide(popup=None, verbose=True, XMLTV_FILE=None):
    """
    Get a TV guide from memory cache, file cache or raw XMLTV file.
    Tries to return at least the channels from the config file if there
    is no other data
    """
    global cached_guide

    if not XMLTV_FILE:
        XMLTV_FILE = config.XMLTV_FILE

    # Can we use the cached version (if same as the file)?
    if (cached_guide == None or
        (os.path.isfile(XMLTV_FILE) and 
         cached_guide.timestamp != os.path.getmtime(XMLTV_FILE))):

        # No, is there a pickled version ("file cache") in a file?
        pname = '%s/TV.xml.pickled' % config.FREEVO_CACHEDIR
        
        got_cached_guide = False
        if (os.path.isfile(XMLTV_FILE) and
            os.path.isfile(pname) and (os.path.getmtime(pname) >
                                       os.path.getmtime(XMLTV_FILE))):
            if verbose:
                _debug_('XMLTV, reading cached file (%s)' % pname)

            if popup:
                popup.show()

            cached_guide = util.read_pickle(pname)

            if popup:
                popup.destroy()

            epg_ver = None
            try:
                epg_ver = cached_guide.EPG_VERSION
            except AttributeError:
                if verbose:
                    _debug_('EPG does not have a version number, must be reloaded')
                    print dir(cached_guide)

            if epg_ver != epg_types.EPG_VERSION:
                if verbose:
                    _debug_('EPG version missmatch, must be reloaded')

            elif cached_guide.timestamp != os.path.getmtime(XMLTV_FILE):
                # Hmmm, weird, there is a pickled file newer than the TV.xml
                # file, but the timestamp in it does not match the TV.xml
                # timestamp. We need to reload!
                if verbose:
                    _debug_('EPG: Pickled file timestamp mismatch, reloading!')
                
            else:
                if verbose:
                    _debug_('XMLTV, got cached guide (version %s).' % epg_ver)
                got_cached_guide = True

        if not got_cached_guide:
            # Need to reload the guide

            if popup:
                popup.show()
                
            if verbose:
                _debug_('XMLTV, trying to read raw file (%s)' % XMLTV_FILE)
            try:    
                cached_guide = load_guide(verbose, XMLTV_FILE)
	    except:
	    	# Don't violently crash on a incomplete or empty TV.xml please.
	    	cached_guide = None
                print
                print String(_("Couldn't load the TV Guide, got an exception!"))
                print
                traceback.print_exc()
            else:
                # Replace config.XMLTV_FILE before we save the pickle in order
                # to avoid timestamp confision.
                if XMLTV_FILE != config.XMLTV_FILE:
                    shutil.copyfile(XMLTV_FILE, config.XMLTV_FILE)
                    os.unlink(XMLTV_FILE)
                    cached_guide.timestamp = os.path.getmtime(config.XMLTV_FILE)

                # Dump a pickled version for later reads
                util.save_pickle(cached_guide, pname)

    if not cached_guide:
        # An error occurred, return an empty guide
        cached_guide = epg_types.TvGuide()
        
    if popup:
        popup.destroy()

    return cached_guide


def load_guide(verbose=True, XMLTV_FILE=None):
    """
    Load a guide from the raw XMLTV file using the xmltv.py support lib.
    Returns a TvGuide or None if an error occurred
    """
    if not XMLTV_FILE:
        XMLTV_FILE = config.XMLTV_FILE

    # Create a new guide
    guide = epg_types.TvGuide()

    # Is there a file to read from?
    if os.path.isfile(XMLTV_FILE):
        gotfile = 1
        guide.timestamp = os.path.getmtime(XMLTV_FILE)
    else:
        _debug_('XMLTV file (%s) missing!' % XMLTV_FILE)
        gotfile = 0

    # Add the channels that are in the config list, or all if the
    # list is empty
    if config.TV_CHANNELS:
        if verbose:
            _debug_('epg_xmltv.py: Only adding channels in list')

        for data in config.TV_CHANNELS:
            (id, disp, tunerid) = data[:3]
            c = epg_types.TvChannel()
            c.id = id
            c.displayname = disp
            c.tunerid = tunerid

            # Handle the optional time-dependent station info
            c.times = []
            if len(data) > 3 and len(data[3:4]) == 3:
                for (days, start_time, stop_time) in data[3:4]:
                    c.times.append((days, int(start_time), int(stop_time)))
            guide.AddChannel(c)


    else: # Add all channels in the XMLTV file
        if verbose:
            _debug_('epg_xmltv.py: Adding all channels')
        xmltv_channels = None
        if gotfile:
            # Don't read the channel info unless we have to, takes a long time!
            xmltv_channels = xmltv.read_channels(util.gzopen(XMLTV_FILE))
        
        # Was the guide read successfully?
        if not xmltv_channels:
            return None     # No
        
        for chan in xmltv_channels:
            id = chan['id'].encode(config.LOCALE, 'ignore')
            c = epg_types.TvChannel()
            c.id = id
            if ' ' in id:
                # Assume the format is "TUNERID CHANNELNAME"
                c.displayname = id.split()[1]   # XXX Educated guess
                c.tunerid = id.split()[0]       # XXX Educated guess
            else:
                displayname = chan['display-name'][0][0]
                if ' ' in displayname:
                    c.displayname = displayname.split()[1]
                    c.tunerid = displayname.split()[0]
                else:
                    c.displayname = displayname
                    c.tunerid = _('REPLACE WITH TUNERID FOR %s') % displayname

            guide.AddChannel(c)

    xmltv_programs = None
    if gotfile:
        if verbose:
            _debug_('reading xmltv data')
        f = util.gzopen(XMLTV_FILE)
        xmltv_programs = xmltv.read_programmes(f)
        f.close()
        
    # Was the guide read successfully?
    if not xmltv_programs:
        return guide    # Return the guide, it has the channels at least...


    needed_ids = []
    for chan in guide.chan_dict:
        needed_ids.append(chan)

    if verbose:
        _debug_('creating guide for %s' % needed_ids)

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
                prog.desc = Unicode(util.format_text(p['desc'][0][0]))
            if p.has_key('sub-title'):
                prog.sub_title = p['sub-title'][0][0]
            try:
                prog.start = timestr2secs_utc(p['start'])
                try:
                    prog.stop = timestr2secs_utc(p['stop'])
                except:
                    # Fudging end time
                    prog.stop = timestr2secs_utc(p['start'][0:8] + '235900' + p['start'][14:18])
            except EPG_TIME_EXC:
                continue
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
