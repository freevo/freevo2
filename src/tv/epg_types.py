#if 0 /*
# -----------------------------------------------------------------------
# epg_types.py - This file contains the types for the Freevo Electronic
#                Program Guide module.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/08/16 18:41:10  dischi
# Fix overlapping programs. The German listing sometimes has a program with
# a wrong stop time so that is overlapps the next entries (mostly the wrong
# entry stops at the end of the day)
#
# Revision 1.5  2003/04/24 19:56:40  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.4  2003/03/16 19:29:06  dischi
# add getattr to TvProgram
#
# Revision 1.3  2003/03/08 17:37:56  dischi
# added compare function
#
# Revision 1.2  2003/02/27 02:03:04  outlyer
# Added support for the xmltv 'sub-title' tag which sometimes contains the
# episode title for TV shows. Its not always there, but if it is, we can use
# it, and I'll show it if it's available in the extended menu.
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
import time, os, string
import config

# The file format version number. It must be updated when incompatible
# changes are made to the file format.
EPG_VERSION = 2

TRUE = 1
FALSE = 0


# Cache variables for last GetPrograms()
cache_last_start = None
cache_last_stop = None
cache_last_chanids = None
cache_last_result = None
cache_last_time = 0



class TvProgram:

    channel_id = ''
    title = ''
    desc = ''
    sub_title = ''
    start = 0.0
    stop = 0.0


    def __str__(self):
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)   # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])

        s = '%s to %s  %3s %s' % (begins, ends, self.channel_id, self.title)
        return s


    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not other:
            return 1
        return self.title != other.title or \
               self.start != other.start or \
               self.stop  != other.stop or \
               self.channel_id != other.channel_id


    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'start':
            bt = time.localtime(self.start)   # Beginning time tuple
            return '%02d:%02d' % (bt[3], bt[4])
        if attr == 'stop':
            et = time.localtime(self.stop)   # End time tuple
            return '%02d:%02d' % (et[3], et[4])

        if hasattr(self, attr):
            return str(getattr(self,attr))
        return ''



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
            if len(self.chan_dict[program.channel_id].programs) and \
                   self.chan_dict[program.channel_id].programs[-1].stop > program.start:
                # the tv guide is corrupt, the last entry has a stop time higher than
                # the next start time. Correct that by reducing the stop time of
                # the last entry
                if config.DEBUG > 1:
                    print 'wrong stop time: %s' % \
                          self.chan_dict[program.channel_id].programs[-1]
                self.chan_dict[program.channel_id].programs[-1].stop = program.start
                
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

        # Return a cached version?
        global cache_last_start, cache_last_stop, cache_last_chanids
        global cache_last_time, cache_last_result
        if (cache_last_start == start and cache_last_stop == stop and
            cache_last_chanids == chanids and
            time.time() < cache_last_time):
            if config.DEBUG > 1:
                a = cache_last_time - time.time()
                print 'epg: Returning cached results, valid for %1.1f secs.' % a
            return cache_last_result[:]  # Return a copy
        
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

        # Update cache variables
        cache_last_start = start
        cache_last_stop = stop
        if chanids:
            cache_last_chanids = chanids[:]
        else:
            cache_last_chanids = None
        cache_last_timeout = time.time() + 20
        cache_last_result = channels[:] # Make a copy in case the caller modifies it
        if config.DEBUG > 1:
            print 'epg: Returning new results'
            
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
        
