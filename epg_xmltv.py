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
DEBUG = 1

TRUE = 1
FALSE = 0


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

    # Yes, but can we use the cached version (if same as the file)?
    if (cached_guide == None or
          cached_guide.timestamp != os.path.getmtime(config.XMLTV_FILE)):

        # No, is there a pickled version ("file cache") in a file?
        pname = config.XMLTV_FILE + '.pickled'
        if os.path.isfile(pname) and (os.path.getmtime(pname) >
                                      os.path.getmtime(config.XMLTV_FILE)):
            if DEBUG: print 'XMLTV, reading cached file (%s)' % pname
            cached_guide = pickle.load(open(pname, 'r'))
        else:
            # No, need to reload it
            if DEBUG: print 'XMLTV, reading raw file (%s)' % config.XMLTV_FILE
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
    guide.timestamp = os.path.getmtime(config.XMLTV_FILE)

    # Is there a file to read from?
    gotfile = 1
    if not os.path.isfile(config.XMLTV_FILE):
        if DEBUG: print 'XMLTV file (%s) missing!' % config.XMLTV_FILE
        gotfile = 0

    # Add the channels that are in the config list, or all if the
    # list is empty
    if config.TV_CHANNELS:
        for (id, disp, tunerid) in config.TV_CHANNELS:
            c = epg_types.TvChannel()
            c.id = id
            c.displayname = disp
            c.tunerid = tunerid
            guide.AddChannel(c)
    else: # Add all channels in the XMLTV file
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
        prog.start = time.mktime(strptime.strptime(p['start'], xmltv.date_format))
        prog.stop = time.mktime(strptime.strptime(p['stop'], xmltv.date_format))
        guide.AddProgram(prog)

    guide.Sort()  # Sort the programs in time order
    
    return guide
    
    
if __name__ == '__main__':
    guide = get_guide()

    print '\nXML TV Guide Listing:'
    print guide

    print '\nChannel list:'
    
    # Print a list hopefully suitable for using as the config.TV_CHANNELS
    for chan in guide.chan_list:
        id = chan.id
        disp = chan.displayname
        num = chan.tunerid
        print "    ('%s', '%s', '%s')," % (id, disp, num)

    # Print all programs that are currently playing
    now = time.time()
    progs = guide.GetPrograms(now, now)
    for prog in progs:
        print prog
