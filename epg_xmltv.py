#
# epg_xmltv.py
#
# This is the Freevo Electronic Program Guide module for XMLTV.
#
# $Id$

import sys
import time, os, string
import cPickle as pickle

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# Use the alternate strptime module which seems to handle time zones
import strptime

# The XMLTV handler from openpvr.sourceforge.net
import xmltv

# The EPG data types. They need to be in an external module in order for
# pickling to work properly when run from inside this module and from the
# tv.py module.
import epg_types

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
def get_guide():
    global cached_guide

    # Can we use the cached version (if same as the file)?
    if (cached_guide == None or
        (os.path.isfile(config.XMLTV_FILE) and 
         cached_guide.timestamp != os.path.getmtime(config.XMLTV_FILE))):

        # No, is there a pickled version ("file cache") in a file?
        pname = config.XMLTV_FILE + '.pickled'
        got_cached_guide = FALSE
        if (os.path.isfile(config.XMLTV_FILE) and
            os.path.isfile(pname) and (os.path.getmtime(pname) >
                                       os.path.getmtime(config.XMLTV_FILE))):
            if DEBUG: print 'XMLTV, reading cached file (%s)' % pname
            cached_guide = pickle.load(open(pname, 'r'))

            epg_ver = None
            try:
                epg_ver = cached_guide.EPG_VERSION
            except AttributeError:
                print 'EPG does not have a version number, must be reloaded'

            if epg_ver != epg_types.EPG_VERSION:
                print (('EPG version number %s is stale (new is %s), must ' +
                        'be reloaded') % (epg_ver, epg_types.EPG_VERSION))
            else:
                if DEBUG:
                    print 'XMLTV, got cached guide (version %s).' % epg_ver
                got_cached_guide = TRUE

        if not got_cached_guide:
            # Need to reload the guide
            if DEBUG:
                print 'XMLTV, trying to read raw file (%s)' % config.XMLTV_FILE
                
            cached_guide = load_guide()

            # Dump a pickled version for later reads
            pickle.dump(cached_guide, open(pname, 'w'))

    if not cached_guide:
        # An error occurred, return an empty guide
        cached_guide = epg_types.TvGuide()
        
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
            xmltv_channels = xmltv.read_channels(open(config.XMLTV_FILE))
        
        # Was the guide read successfully?
        if not xmltv_channels:
            return None     # No
        
        for chan in xmltv_channels:
            id = chan['id'].encode('Latin-1')
            c = epg_types.TvChannel()
            c.id = id
            c.displayname = id.split()[1]   # XXX Educated guess
            c.tunerid = id.split()[0]       # XXX Educated guess
            guide.AddChannel(c)

    xmltv_programs = None
    if gotfile:
        xmltv_programs = xmltv.read_programmes(open(config.XMLTV_FILE))
    
    # Was the guide read successfully?
    if not xmltv_programs:
        return guide    # Return the guide, it has the channels at least...

    for p in xmltv_programs:
        prog = epg_types.TvProgram()
        prog.channel_id = p['channel'].encode('Latin-1')
        prog.title = p['title'][0][0].encode('Latin-1')
        if p.has_key('desc'):
            prog.desc = p['desc'][0][0].encode('Latin-1')
        try:
            prog.start = timestr2secs_utc(p['start'])
            prog.stop = timestr2secs_utc(p['stop'])
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

    # Is it the '+1' format?
    if tz[0] == '+' or tz[0] == '-':
        secs = time.mktime(strptime.strptime(tval, xmltv.date_format_notz))
        adj_neg = int(tz) >= 0
        adj_secs = int(tz[1:3])*3600+ int(tz[3:5])*60
        if adj_neg:
            #print 'timestr2secs_utc(%s): secs = %s - %s' % (str, secs, adj_secs)
            secs -= adj_secs
        else:
            #print 'timestr2secs_utc(%s): secs = %s + %s' % (str, secs, adj_secs)
            secs += adj_secs
    else:
        # No, use the regular conversion
        secs = time.mktime(strptime.strptime(str, xmltv.date_format_tz))
        #print 'timestr2secs_utc(%s): secs = %s' % (str, secs)

    return secs


if __name__ == '__main__':
    # Remove a pickled file (if any) if we're trying to list all channels
    if not config.TV_CHANNELS:
        if os.path.isfile('/tmp/TV.xml.pickled'):
            os.remove('/tmp/TV.xml.pickled')

    print
    print 'Getting the TV Guide, this can take a couple of minutes...'
    print
    guide = get_guide()

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

