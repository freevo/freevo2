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

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


class TvProgram:

    channel_id = ''
    title = ''
    desc = ''
    start = 0.0
    stop = 0.0


    def __str__(self):
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)   # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])

        s = '%s to %s  %3s %s' % (begins, ends, self.channel_id, self.title)
        return s


class TvChannel:
    id = ''
    displayname = ''
    tunerid = ''
    logo = ''   # URL or file   Not used yet
    programs = None


    def __init__(self):
        self.programs = []

        
    def Sort(self):
        # Sort the programs so that the earliest is first in the list
        f = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(f)
        

    def __str__(self):
        s = 'CHANNEL ID   %-20s' % self.id

        if self.programs:
            s += '\n'
            for program in self.programs:
                s += '   ' + str(program) + '\n'
        else:
            s += '     NO DATA\n'

        return s
    
        
class TvGuide:
    chan_dict = None
    chan_list = None
    timestamp = 0.0


    def __init__(self):
        # These two types map to the same channel objects
        self.chan_dict = {}   # Channels mapped using the id
        self.chan_list = []   # Channels, ordered

        
    def AddChannel(self, channel):
        if not self.chan_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.chan_dict[channel.id] = channel
            self.chan_list += [channel]

        
    def AddProgram(self, program):
        # The channel must be present, or the program is
        # silently dropped
        if self.chan_dict.has_key(program.channel_id):
            self.chan_dict[program.channel_id].programs += [program]


    # Get all programs that occur at least partially between
    # the start and stop timeframe.
    # If start is None, get all programs from the start.
    # If stop is None, get all programs until the end.
    # The chanids can be used to select only certain channel id's,
    # all channels are returned otherwise
    #
    # The return value is a list of channels (TvChannel)
    def GetPrograms(self, start = None, stop = None, chanids = None):
        if start == None:
            start = 0.0
        if stop == None:
            stop = 2**31-1   # Year 2038

        channels = []
        for chan in self.chan_list:
            if chanids and (not chan.id in chanids):
                continue

            # Copy the channel info
            c = TvChannel()
            c.id = chan.id
            c.displayname = chan.displayname
            c.tunerid = chan.tunerid
            c.logo = chan.logo
            # Copy the programs that are inside the indicated time bracket
            f = lambda p: not (p.start > stop or p.stop < start)
            c.programs = filter(f, chan.programs)

            channels.append(c)

        return channels
            
            
    def Sort(self):
        # Sort all channel programs in time order
        for chan in self.chan_list:
            chan.Sort()
        

    def __str__(self):
        s = 'XML TV Guide\n'

        for chan in self.chan_list:
            s += str(chan)

        return s
        

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
   	cached_guide = TvGuide()
        
    return cached_guide


# Load a guide from the raw XMLTV file using the xmltv.py support lib.
#
# Returns a TvGuide or None if an error occurred
def load_guide():
    # Create a new guide
    guide = TvGuide()
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
            c = TvChannel()
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
            c = TvChannel()
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
        prog = TvProgram()
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
