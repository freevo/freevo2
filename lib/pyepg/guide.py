# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# guide.py - basic guide class
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/08/10 19:35:45  dischi
# o better index generation
# o split into different files
# o support for other parsers than xmltv
# o internal caching
#
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

import os
import sys
import stat
import cPickle
import pickle

import config

if float(sys.version[0:3]) < 2.3:
    PICKLE_PROTOCOL = 1
else:
    PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL

# Internal version number for caching
EPG_VERSION = 0.1



class TvGuide:
    """
    The complete TV guide with all channels
    """
    def __init__(self, datafile, cachefile, parser, verbose):
        # These two types map to the same channel objects
        self.chan_dict   = {}   # Channels mapped using the id
        self.chan_list   = []   # Channels, ordered

        try:
            if os.stat(cachefile)[stat.ST_MTIME] < os.stat(datafile)[stat.ST_MTIME]:
                raise IOError
            f = open(cachefile)
            try:
                data = cPickle.load(f)
            except:
                data = pickle.load(f)
            f.close()
            if data[0] != EPG_VERSION:
                raise IOError
            _debug_('using epg cachefile %s' % cachefile)
            self.chan_list = data[1]
            for c in self.chan_list:
                self.chan_dict[c.id] = c
            
        except Exception, e:
            exec('import %s' % parser)
            getattr(eval(parser), 'load_guide')(self, datafile, verbose=verbose)
            self.sort()
            self.create_index()

        if cachefile:
            try:
                if os.path.isfile(cachefile):
                    os.unlink(cachefile)
                f = open(cachefile, 'w')
                cPickle.dump((EPG_VERSION, self.chan_list), f, PICKLE_PROTOCOL)
                f.close()
            except IOError:
                print 'unable to save to cachefile %s' % file
            

    def add_channel(self, channel):
        """
        add a channel to the list
        """
        if not self.chan_dict.has_key(channel.id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.chan_dict[channel.id] = channel
            self.chan_list.append(channel)

        
    def add_program(self, program):
        """
        add a program
        the channel must be present, or the program is silently dropped
        """
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

            self.chan_dict[program.channel_id].programs.append(program)


            
    def sort(self):
        """
        Sort all channel programs in time order
        """
        for chan in self.chan_list:
            chan.sort()
        

    def __unicode__(self):
        """
        return as unicode for debug
        """
        s = u'XML TV Guide\n'
        for chan in self.chan_list:
            s += String(chan)
        return s


    def __str__(self):
        """
        return as string for debug
        """
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
        try:
            return self.chan_dict[id]
        except IndexError:
            None
