#
# epg_types.py
#
# This file contains the types for the Freevo Electronic Program Guide module.
#
# $Id$

import sys
import time, os, string
import config

# The file format version number. It must be updated when incompatible
# changes are made to the file format.
EPG_VERSION = 2

# Set to 1 for debug output
DEBUG = config.DEBUG

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
    times = None


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
        self.EPG_VERSION = EPG_VERSION

        
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
            start = 0
        if stop == None:
            stop = 2147483647   # Year 2038

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
            c.times = chan.times
            # Copy the programs that are inside the indicated time bracket
            f = lambda p, a=start, b=stop: not (p.start > b or p.stop < a)
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
        
