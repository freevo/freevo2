# -*- coding: iso-8859-1 -*-
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
# Revision 1.3  2004/08/09 21:19:46  dischi
# make tv guide working again (but very buggy)
#
# Revision 1.2  2004/08/05 17:16:05  dischi
# misc enhancements
#
# Revision 1.20  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.19  2004/07/01 22:49:49  rshortt
# Unicode fix.
#
# Revision 1.18  2004/06/22 01:07:49  rshortt
# Move stuff into __init__() and fix a bug for twisted's serialization.
#
# Revision 1.17  2004/03/05 20:49:11  rshortt
# Add support for searching by movies only.  This uses the date field in xmltv
# which is what tv_imdb uses and is really acurate.  I added a date property
# to TvProgram for this and updated findMatches in the record_client and
# recordserver.
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
import copy
import time, os, string
import config


# Cache variables for last GetPrograms()
cache_last_start = None
cache_last_stop = None
cache_last_chanids = None
cache_last_result = None
cache_last_time = 0



class TvProgram:

    def __init__(self, title=''):
        self.channel_id = ''
        self.title      = title
        self.desc       = ''
        self.sub_title  = ''
        self.start      = 0.0
        self.stop       = 0.0
        self.ratings    = {}
        self.advisories = []
        self.categories = []
        self.date       = None
        self.pos        = None
        
        # Due to problems with Twisted's marmalade this should not be changed
        # to a boolean type. 
        self.scheduled  = 0


    def __unicode__(self):
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel_id) + \
                   self.title + u' (%s)' % self.pos


    def __str__(self):
        return String(self.__unicode__())

    
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
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.start)))
        if attr == 'stop':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.stop)))
        if attr == 'date':
            return Unicode(time.strftime(config.TV_DATEFORMAT, time.localtime(self.start)))
        if attr == 'time':
            return self.getattr('start') + u' - ' + self.getattr('stop')
        if hasattr(self, attr):
            return getattr(self,attr)
        return ''



class TvChannel:
    def __init__(self):
        self.id          = ''
        self.displayname = ''
        self.tunerid     = ''
        self.logo        = ''
        self.programs    = []
        self.times       = None
        self.index       = {}
        self.index_start = 0
        self.index_end   = 0

        
    def sort(self):
        # Sort the programs so that the earliest is first in the list
        f = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(f)
        

    def __unicode__(self):
        s = u'CHANNEL ID   %-20s' % self.id
        
        if self.programs:
            s += u'\n'
            for program in self.programs:
                s += u'   ' + unicode(program) + u'\n'
        else:
            s += u'     NO DATA\n'
        return s


    def __str__(self):
        return String(self.__unicode__())
    

    def get_key(self, t):
        return int('%04d%02d%02d' % time.localtime(t)[:3])

        
    def create_index(self):
        """
        create index for faster access
        """
        last  = -1
        index = -1

        last_key = None

        for p in self.programs:
            index += 1
            key = self.get_key(p.start)
            if not self.index_start:
                self.index_start = key
            self.index_end = key
            if not self.index.has_key(key):
                if last_key:
                    while len(self.index[last_key]) < 48:
                        self.index[last_key].append(last)
                self.index[key] = []
            pos = time.localtime(p.start)[3:5]
            pos = pos[0] * 2 + ((pos[1] + 29) / 30)
            p.pos = pos
            
            if len(self.index[key]) >= pos + 1:
                last = index
                continue
            while len(self.index[key]) < pos:
                self.index[key].append(last)
            self.index[key].append(index)
            last = index
            last_key = key
        while len(self.index[key]) < 48:
            self.index[key].append(index)
            

    def get_pos(self, start, stop):
        """
        get internal positions for programs between start and stop
        """
        key = self.get_key(start)
        if key < self.index_start:
            key = self.index_start
            pos = 0
        else:
            pos   = time.localtime(start)[3:5]
            pos   = max(pos[0] * 2 + (pos[1] / 30), 0)

        start = self.index[key][pos]
        
        key = self.get_key(stop)
        if key > self.index_end:
            key = self.index_end
            pos = 47
        else:
            pos  = time.localtime(stop)[3:5]
            pos  = max(pos[0] * 2 + ((pos[1] + 29) / 30), 0)

        if pos == 48:
            # next day
            key = self.get_key(stop+60*30)
            if key > self.index_end:
                key = self.index_end
                pos = 47
            else:
                pos = 0

        stop = self.index[key][pos] + 1
        return start, stop

        
    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        if stop:
            start, stop = self.get_pos(start, stop)
            return self.programs[start:stop]
        else:
            start_p, stop_p = self.get_pos(start, start)
            f = lambda p, a=start, b=start: not (p.start > b or p.stop < a)
            try:
                return filter(f, self.programs[start_p:stop_p])[0]
            except Exception, e:
                return TvProgram(_('This channel has no data loaded'))


class TvGuide:
    def __init__(self):
        # These two types map to the same channel objects
        self.chan_dict   = {}   # Channels mapped using the id
        self.chan_list   = []   # Channels, ordered
        self.EPG_VERSION = config.EPG_VERSION
        self.timestamp   = 0.0


    def AddChannel(self, channel):
        if not self.chan_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.chan_dict[channel.id] = channel
            self.chan_list.append(channel)

        
    def AddProgram(self, program):
        # The channel must be present, or the program is
        # silently dropped
        if self.chan_dict.has_key(program.channel_id):
            p = self.chan_dict[program.channel_id].programs
            if len(p) and p[-1].start < program.stop and p[-1].stop > program.start:
                # the tv guide is corrupt, the last entry has a stop time higher than
                # the next start time. Correct that by reducing the stop time of
                # the last entry
                if config.DEBUG > 1:
                    print 'wrong stop time: %s' % \
                          String(self.chan_dict[program.channel_id].programs[-1])
                self.chan_dict[program.channel_id].programs[-1].stop = program.start
                
            if len(p) and p[-1].start == p[-1].stop:
                # Oops, something is broken here
                self.chan_dict[program.channel_id].programs = p[:-1]

            if len(p) and p[-1].stop + 60 < program.start:
                no_data = TvProgram(_('This channel has no data loaded'))
                no_data.start = p[-1].stop
                no_data.stop  = program.start
                no_data.index = len(self.chan_dict[program.channel_id].programs)
                self.chan_dict[program.channel_id].programs.append(no_data)

            elif not len(p):
                no_data = TvProgram(_('This channel has no data loaded'))
                no_data.stop  = program.start
                no_data.index = len(self.chan_dict[program.channel_id].programs)
                self.chan_dict[program.channel_id].programs.append(no_data)
            program.index = len(self.chan_dict[program.channel_id].programs)
            self.chan_dict[program.channel_id].programs.append(program)


            
    def sort(self):
        # Sort all channel programs in time order
        for chan in self.chan_list:
            chan.sort()
        

    def __unicode__(self):
        s = u'XML TV Guide\n'
        for chan in self.chan_list:
            s += String(chan)
        return s


    def __str__(self):
        return String(self.__unicode__())

    
    def create_index(self):
        """
        create an index for faster access
        """
        for chan in self.chan_list:
            chan.create_index()
            
    def get(self, id):
        """
        return channel with given id
        """
        for chan in self.chan_list:
            if chan.id == id:
                return chan
        return None
    
