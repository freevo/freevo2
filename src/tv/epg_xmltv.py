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
# Revision 1.31  2003/09/05 20:10:36  dischi
# use util.encode to encode strings
#
# Revision 1.30  2003/09/05 03:32:15  rshortt
# Updating to use the tv. namespace.
#
# Revision 1.29  2003/09/03 21:07:50  dischi
# Make sure the user can write the file. It may happen that the user has
# no permission at all (try except is protecting us here), but maybe he
# has write access to the directory, but not the file itself. So remove
# it first and than write. Please check other parts of Freevo for that
# problem!
#
# Revision 1.28  2003/08/28 18:11:36  dischi
# use util.py pickle function now and remove the uid from filename
#
# Revision 1.27  2003/08/24 19:08:38  mikeruelle
# populate the rating and categories entries for TvProgram objects.
#
# Revision 1.26  2003/08/24 18:15:59  outlyer
# Use the "best" Python pickle available. Starting in Python 2.3 this is
# a defined constant, so we'll use the constant; older versions of Python
# will continue to use the binary format.
#
# Revision 1.25  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.8  2003/02/14 16:45:16  outlyer
# Ugly hack to work around missing stop times. This is a slight improvement
# over my patch from yesterday, because it "guesses" the stop time of the shows.
#
# Logic:
#
# Since the only shows missing stop dates are those which appear to end at
# midnight, we insert a stop date of midnight for those shows missing a stop
# date.
#
# This is not perfect. If you have a better solution, I'll be the first one to
# put it in. Hopefully, this'll be fixed in XMLTV at some point and this hack
# won't be necessary.
#
# Revision 1.7  2003/02/13 01:48:02  outlyer
# A workaround for the issue which has arisen with zap2it TV listings wherein
# the stop date has to be guessed by XMLTV and sometimes isn't guessed properly.
# This is an imperfect workaround, but it allows the guide to work.
#
# I should stress imperfect, because there is a nested exception which is so
# ugly, it hurts to look at it. I don't know the internals of the xmltv.py
# library well enough to do a proper fix but I will try. As I said, at least
#  the guide works now.
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

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# Use the alternate strptime module which seems to handle time zones
#
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


# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

EPG_TIME_EXC = 'Time conversion error'


cached_guide = None

def myversion():
    version = 'XMLTV Parser 1.2.4\n'
    version += 'Module Author: Aubin Paul\n'
    version += 'Uses xmltv Python parser by James Oakley\n'
    return version


# Get a TV guide from memory cache, file cache or raw XMLTV file.
# Tries to return at least the channels from the config file if there
# is no other data
def get_guide(popup=None):
    global cached_guide

    # Can we use the cached version (if same as the file)?
    if (cached_guide == None or
        (os.path.isfile(config.XMLTV_FILE) and 
         cached_guide.timestamp != os.path.getmtime(config.XMLTV_FILE))):

        # No, is there a pickled version ("file cache") in a file?
        pname = '%s/TV.xml.pickled' % config.FREEVO_CACHEDIR
        
        got_cached_guide = FALSE
        if (os.path.isfile(config.XMLTV_FILE) and
            os.path.isfile(pname) and (os.path.getmtime(pname) >
                                       os.path.getmtime(config.XMLTV_FILE))):
            if DEBUG: print 'XMLTV, reading cached file (%s)' % pname

            if popup:
                popup.show()

            cached_guide = util.read_pickle(pname)

            if popup:
                popup.destroy()

            epg_ver = None
            try:
                epg_ver = cached_guide.EPG_VERSION
            except AttributeError:
                print 'EPG does not have a version number, must be reloaded'
                print dir(cached_guide)

            if epg_ver != epg_types.EPG_VERSION:
                print (('EPG version number %s is stale (new is %s), must ' +
                        'be reloaded') % (epg_ver, epg_types.EPG_VERSION))

            elif cached_guide.timestamp != os.path.getmtime(config.XMLTV_FILE):
                # Hmmm, weird, there is a pickled file newer than the TV.xml
                # file, but the timestamp in it does not match the TV.xml
                # timestamp. We need to reload!
                print 'EPG: Pickled file timestamp mismatch, reloading!'
                
            else:
                if DEBUG:
                    print 'XMLTV, got cached guide (version %s).' % epg_ver
                got_cached_guide = TRUE

        if not got_cached_guide:
            # Need to reload the guide

            if popup:
                popup.show()
                
            if DEBUG:
                print 'XMLTV, trying to read raw file (%s)' % config.XMLTV_FILE
            try:    
                cached_guide = load_guide()
	    except:
	    	# Don't violently crash on a incomplete or empty TV.xml please.
	    	cached_guide = None
                print "Couldn't load the TV Guide, got an exception!"
                print
                traceback.print_exc()
            else:
                # Dump a pickled version for later reads
                util.save_pickle(cached_guide, pname)

    if not cached_guide:
        # An error occurred, return an empty guide
        cached_guide = epg_types.TvGuide()
        
    if popup:
        popup.destroy()

    return cached_guide


# Load a guide from the raw XMLTV file using the xmltv.py support lib.
#
# Returns a TvGuide or None if an error occurred
def load_guide():
    # Create a new guide
    guide = epg_types.TvGuide()

    # Is there a file to read from?
    if os.path.isfile(config.XMLTV_FILE):
        gotfile = 1

        if 0:
            # XXX Hack to fix a bug where qp_xml barfs on 8-bit chars.

            # Read the current file
            print 'XMLTV: XXX Hack to fix a bug where qp_xml barfs on 8-bit chars.'
            fd = open(config.XMLTV_FILE)
            data_8bit = fd.read()
            fd.close()

            # Translate to 7-bit data, replacing 8-bit chars with spaces
            table = ''.join(map(lambda v:chr(v), (range(0,127) + [32] * 128)))
            data_7bit = data_8bit.translate(table)

            # Write to the file
            try:
                if os.path.isfile(config.XMLTV_FILE):
                    os.unlink(config.XMLTV_FILE)
                fd = open(config.XMLTV_FILE, 'w')
                fd.write(data_7bit)
                fd.close()
            except IOError:
                print 'unable to save %s' % config.XMLTV_FILE
        
        guide.timestamp = os.path.getmtime(config.XMLTV_FILE)
    else:
        if DEBUG: print 'XMLTV file (%s) missing!' % config.XMLTV_FILE
        gotfile = 0

    # Add the channels that are in the config list, or all if the
    # list is empty
    if config.TV_CHANNELS:
        if DEBUG: print 'epg_xmltv.py: Only adding channels in list'
        for data in config.TV_CHANNELS:
            (id, disp, tunerid) = data[:3]
            c = epg_types.TvChannel()
            c.id = id
            c.displayname = disp
            c.tunerid = tunerid

            # Handle the optional time-dependent station info
            c.times = []
            if len(data) > 3:
                for (days, start_time, stop_time) in data[3:]:
                    c.times.append((days, int(start_time), int(stop_time)))
            guide.AddChannel(c)
    else: # Add all channels in the XMLTV file
        if DEBUG: print 'epg_xmltv.py: Adding all channels'
        xmltv_channels = None
        if gotfile:
            # Don't read the channel info unless we have to, takes a long time!
            xmltv_channels = xmltv.read_channels(util.gzopen(config.XMLTV_FILE))
        
        # Was the guide read successfully?
        if not xmltv_channels:
            return None     # No
        
        for chan in xmltv_channels:
            id = util.encode(chan['id'], 'Latin-1')
            c = epg_types.TvChannel()
            c.id = id
            if ' ' in id:
                # Assume the format is "TUNERID CHANNELNAME"
                c.displayname = id.split()[1]   # XXX Educated guess
                c.tunerid = id.split()[0]       # XXX Educated guess
            else:
                # Let the user figure it out
                c.displayname = '%s REPLACE WITH CHANNEL NAME' % id
                c.tunerid = '%s REPLACE WITH TUNERID' % id
            guide.AddChannel(c)

    xmltv_programs = None
    if gotfile:
        xmltv_programs = xmltv.read_programmes(util.gzopen(config.XMLTV_FILE))
    
    # Was the guide read successfully?
    if not xmltv_programs:
        return guide    # Return the guide, it has the channels at least...

    for p in xmltv_programs:
        prog = epg_types.TvProgram()
        prog.channel_id = util.encode(p['channel'], 'Latin-1')
        prog.title = util.encode(p['title'][0][0], 'Latin-1')
        if p.has_key('rating'):
            try:
                for darating in p['rating']:
                    prog.ratings[util.encode(darating['system'], 'Latin-1')] = util.encode(darating['value'], 'Latin-1')
            except KeyError:
                pass
        if p.has_key('category'):
             prog.categories = [ util.encode(cat[0], 'Latin-1') for cat in p['category'] ]
        if p.has_key('desc'):
            prog.desc = util.format_text(util.encode(p['desc'][0][0], 'Latin-1'))
        if p.has_key('sub-title'):
            prog.sub_title = util.encode(p['sub-title'][0][0], 'Latin-1')
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

    guide.Sort()  # Sort the programs in time order
    
    return guide


#    
# Convert a timestring to UTC (=GMT) seconds.
#
# The format is either one of these two:
# '20020702100000 CDT'
# '200209080000 +0100'
def timestr2secs_utc(str):
    # This is either something like 'EDT', or '+1'
    try:
        tval, tz = str.split()
    except ValueError:
        # The time value couldn't be decoded
        raise EPG_TIME_EXC

    if tz == 'CET':
        tz='+2'
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

        secs = time.mktime(strptime.strptime(str, xmltv.date_format))

    return secs


def find_favorites():

    import string
    import tvgrep
    import re

    SEASONPASS='/var/cache/freevo/recording/watchlist'
    if os.path.isfile(SEASONPASS):
        m = open(SEASONPASS,'r')
        for show in m.readlines():
            show = string.replace(show.strip(),' ','\ ')
            ARG = '.*' + show + '*.'
            REGEXP = re.compile(ARG,re.IGNORECASE)
            for a in guide.GetPrograms():
                for b in a.programs:
                    if REGEXP.match(b.title):
                        print tvgrep.make_schedule(b)

if __name__ == '__main__':
    sys.stdout = sys.__stdout__
    # Remove a pickled file (if any) if we're trying to list all channels
    if not config.TV_CHANNELS:
        if os.path.isfile('%s/TV.xml.pickled' % config.FREEVO_CACHEDIR):
            os.remove('%s/TV.xml.pickled' % config.FREEVO_CACHEDIR)

    print
    print 'Getting the TV Guide, this can take a couple of minutes...'
    print
    guide = get_guide()

    #print "Finding favourites"
    #find_favorites()
        
    # No args means just pickle the guide, for use with cron-jobs
    # after getting a new guide.
    if len(sys.argv) == 1:
        sys.exit(0)

    if sys.argv[1] == 'config':
        # Print a list hopefully suitable for using as the config.TV_CHANNELS
        for chan in guide.chan_list:
            id = chan.id
            disp = chan.displayname
            num = chan.tunerid
            print "    ('%s', '%s', '%s')," % (id, disp, num)
    else:
        # Just dump some data
        print '\nXML TV Guide Listing:'
        print guide

        print '\nChannel list:'

        # Print all programs that are currently playing
        now = time.time()
        progs = guide.GetPrograms(now, now)
        for prog in progs:
            print prog

