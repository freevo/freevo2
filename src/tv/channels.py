# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# channels.py - Freevo module to handle channel changing.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
#
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
# -----------------------------------------------------------------------------

# python imports
import os
import time
import traceback
import logging

# the electronic program guide
import pyepg

# freevo imports
import sysconfig
import recordings

log = logging.getLogger('tv')

EPGDB = sysconfig.datafile('epgdb')

_epg = None


def get_epg():
    """
    Return an existing instance of the EPG database.
    """
    global _epg
    if not _epg:
        _epg = pyepg.get_epg(EPGDB)
    return _epg


def when_listings_expire():

    last = 0
    left = 0

    for ch in get_channels().get_all():
        prog = ch.programs[len(ch.programs)-1]
        if prog.start > last: last = prog.start

    if last > 0:
        now = time.time()
        if last > now:
            left = int(last - now)
            # convert to hours
            left /= 3600

    return left


class Program:
    """
    A tv program item for the tv guide and other parts of the tv submenu.
    """
    def __init__(self, title, start, stop, subtitle='', description='',
                 id=None, channel = None, parent=None):
        self.title = title
        self.name  = self.title
        self.start = start
        self.stop  = stop

        self.channel     = channel
        self.id          = id
        self.subtitle    = subtitle
        self.description = description

        key = '%s%s%s' % (channel.chan_id, start, stop)
        if recordings.recordings.has_key(key):
            self.scheduled = recordings.recordings[key]
        else:
            self.scheduled = False

        # TODO: add category support (from epgdb)
        self.categories = ''
        # TODO: add ratings support (from epgdb)
        self.ratings = ''


class Channel:
    """
    Information about one specific channel, also containing
    epg informations.
    """
    def __init__(self, id, display_name, access_id):
        self.chan_id   = id
        self.access_id = access_id
        self.programs  = []
        self.logo      = ''

        # XXX Change this to config.TV_CHANNEL_DISPLAY_FORMAT or something as
        # XXX many people won't want to see the access_id.
        # XXX What should we use, name or title, or both?
        self.name = self.title = display_name


    def sort_programs(self):
        f = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(f)


    def __get_dummy_programs(self, start, stop):
        """
        Return some default Program with intervals no longer than a
        set default.
        """
        default_prog_interval = 30 * 60
        dummies = []
        d_start = start
        d_stop  = 0

        sec_after_last = start % default_prog_interval
        sec_until_next = default_prog_interval - sec_after_last

        while(d_stop < stop):
            d_stop = d_start + sec_until_next
            if d_stop > stop:
                d_stop = stop

            dummies.append(Program(u'NO DATA', d_start, d_stop,
                                   id=-1, channel = self))

            sec_until_next = default_prog_interval
            d_start = d_stop

        return dummies


    def __import_programs(self, start, stop=-1, progs=[]):
        """
        Get programs from the database to create Program from then
        add them to our local list.  If there are gaps between the programs
        we will add dummy programs to fill it (TODO).
        """
        new_progs = []
        dummy_progs = []

        if not progs:
            progs = get_epg().get_programs(self.chan_id, start, stop)
        for p in progs:
            i = Program(p.title, p.start, p.stop, subtitle=p.subtitle,
                        description=p['description'], id=p.id,
                        channel=self)
            new_progs.append(i)

            # TODO: add information about program being recorded which
            #       comes from another DB table - same with categories,
            #       ratings and advisories.

        l = len(new_progs)
        if not l:
            dummy_progs = self.__get_dummy_programs(start, stop)
        else:
            for p in new_progs:
                i = new_progs.index(p)
                if i == 0:
                    # fill gaps before
                    if p.start > start:
                        n = self.__get_dummy_programs(start, p.start)
                        dummy_progs += n

                if i < l-1:
                    # fill gaps between programs
                    next_p = new_progs[i+1]
                    if p.stop < next_p.start:
                        n = self.__get_dummy_programs(p.stop, next_p.start)
                        dummy_progs += n

                elif i == l-1:
                    # fill gaps at the end
                    if p.stop < stop:
                        n = self.__get_dummy_programs(p.stop, stop)
                        dummy_progs += n

        for i in new_progs + dummy_progs:
            if not i in self.programs:
                self.programs.append(i)

        self.sort_programs()


    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        # get programs
        if self.programs:
            # see if we're missing programs before start
            p = self.programs[0]
            if p.start > start:
                self.__import_programs(start, p.start)
            # see if we're missing programs after end
            p = self.programs[-1]
            if stop == -1:
                self.__import_programs(p.stop, stop)
            else:
                if p.stop < stop:
                    self.__import_programs(p.stop, stop)
        else:
            self.__import_programs(start, stop)

        # return the needed programs
        if stop == 0:
            # only get what's running at time start
            return filter(lambda x: (x.start <= start and x.stop > start),
                          self.programs)
        elif stop == -1:
            # get everything from time start onwards
            return filter(lambda x: (x.start <= start and x.stop > start) or \
                          x.start > start, self.programs)

        elif stop > 0:
            # get everything from time start to time stop
            return filter(lambda x: (x.start <= start and x.stop > start) or \
                          (x.start > start and x.stop < stop) or \
                          (x.start < stop and x.stop >= stop),
                          self.programs)
        raise Exception('bad request: %s-%s' % (start, stop))



    def get_relative(self, pos, prog):
        new_pos = self.programs.index(prog) + pos
        if new_pos < 0:
            # requested program before start
            self.__import_programs(prog.start-3*3600, prog.start)
            return self.get_relative(pos, prog)
        if new_pos >= len(self.programs):
            # requested program after end
            last = self.programs[-1]
            self.__import_programs(last.stop, last.stop+3*3600)
            return self.get_relative(pos, prog)
        return self.programs[new_pos]
    



class ChannelList:
    """
    This is the channel list internal to Freevo.  Here we get channel
    information from pyepg (using EPGDB) and append it with anything
    specific to Freevo like which device to use, or override other
    things such as the display name.
    """

    def __init__(self, TV_CHANNELS=[], TV_CHANNELS_EXCLUDE=[]):
        self.channel_list = []
        self.channel_dict = {}

        try:
            self.epg = get_epg()
        except:
            print 'Failed to load EPGDB! (%s)' % EPGDB
            traceback.print_exc()
            return

        # Check TV_CHANNELS and add them to the list
        for c in TV_CHANNELS:
            self.add_channel(Channel(c[0], c[1], c[2:]))

        # Check the EPGDB for channels. All channels not in the exclude list
        # will be added if not already in the list
        for c in self.epg.get_channels():
            if String(c['id']) in TV_CHANNELS_EXCLUDE:
                # Skip channels that we explicitly do not want.
                continue
            if not c['id'] in self.channel_dict.keys():
                self.add_channel(Channel(c['id'], c['display_name'], c['access_id']))

    def sort_channels(self):
        pass


    def add_channel(self, channel):
        """
        add a channel to the list
        """
        if not self.channel_dict.has_key(channel.chan_id):
            # Add the channel to both the dictionary and the list. This works
            # well in Python since they will both point to the same object!
            self.channel_dict[channel.chan_id] = channel
            self.channel_list.append(channel)


    def __getitem__(self, key):
        return self.channel_list[key]


    def get_all(self):
        return self.channel_list
    

    def get(self, pos, start=None):
        if not start:
            start = self.channel_list[0]
        cpos = self.channel_list.index(start)
        pos  = (cpos + pos) % len(self.channel_list)
        return self.channel_list[pos]
    
        
