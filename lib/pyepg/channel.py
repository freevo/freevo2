# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# channel.py - an epg channel
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a channel class for usage inside the guide. The channel
# has support for pynotifier and will call the step function on longer
# operations.
# 
# The channel has the following attributes:
#   id          id inside the database
#   access_id   access id for tuner etc.
#   logo        url of a logo
#   name        channel name
#   title       channel display name
# 
# To get programs from the epg about the channel use
#   channel[time]       get the programm running at 'time'
#   channel[start:stop] get the programms between start and stop
#   channel[start:]     get all programms beginning at start
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

import time
import logging

# Try to import the notifier or set the variable notifier to None. If
# 'notifier' is not None and 'notifier.step' is not None, call the step
# function to keep the notifier alive

try:
    import notifier
except ImportError:
    notifier = None
    
from program import Program

# get logging object
log = logging.getLogger('pyepg')

START_TIME = 0
STOP_TIME  = 2147483647


class Channel:
    """
    Information about one specific channel, also containing
    epg informations.

    The channel has the following attributes:
    id          id inside the database
    access_id   access id for tuner etc.
    logo        url of a logo
    name        channel name
    title       channel display name

    To get programs from the epg about the channel use
    channel[time]       get the programm running at 'time'
    channel[start:stop] get the programms between start and stop
    channel[start:]     get all programms beginning at start
    """
    def __init__(self, id, display_name, access_id, epg):
        self.id        = id
        self.access_id = access_id
        self.programs  = []
        self.logo      = ''
        self.__epg     = epg
        self.name      = display_name
        self.title     = display_name


    def __get_dummy_program(self, start, stop):
        """
        Return some default Program with intervals no longer than a
        set default.
        """
        log.info('create dummy for id=%s, %s-%s' % (self.id, start, stop))
        return Program(-1, u'NO DATA', start, stop, '', '', '', self)


    def __import_programs(self, start, stop=-1, progs=[]):
        """
        Get programs from the database to create Program from then
        add them to our local list.  If there are gaps between the programs
        we will add dummy programs to fill it (TODO).
        """
        log.debug('import for id=%s, %s-%s' % (self.id, start, stop))
        new_progs = []
        dummy_progs = []
        # keep the notifier alive
        notifier_counter = 0
        if not progs:
            progs = self.__epg.sql_get_programs(self.id, start, stop)
        for p in progs:
            i = Program(p.id, p.title, p.start, p.stop, p.episode, p.subtitle,
                        p['description'], channel=self)
            new_progs.append(i)
            notifier_counter = (notifier_counter + 1) % 500
            if not notifier_counter and notifier and notifier.step:
                notifier.step(False, False)
            # TODO: add information about program being recorded which
            #       comes from another DB table - same with categories,
            #       ratings and advisories.

        l = len(new_progs)
        if not l:
            # No programs found? That's bad. Try to find the last before start
            # and the first after end and create a dummy.
            before = self.__epg.sql_get_programs(self.id, 0, start)
            if before:
                d_start = before[-1].stop
            else:
                d_start = START_TIME
            after = self.__epg.sql_get_programs(self.id, stop, -1)
            if after:
                d_stop = after[0].start
            else:
                d_stop = STOP_TIME
            dummy_progs.append(self.__get_dummy_program(d_start, d_stop))
        else:
            p0 = new_progs[0]
            p1 = new_progs[-1]
            last = None

            for p in new_progs:
                notifier_counter = (notifier_counter + 1) % 500
                if not notifier_counter and notifier and notifier.step:
                    notifier.step(False, False)
                if p == p0 and p.start > start:
                    # gap at the beginning, find first program before this
                    # item and fill the space with a dummy
                    more = self.__epg.sql_get_programs(self.id, 10, start)
                    if more:
                        d = self.__get_dummy_program(more[-1].stop, p.start)
                    else:
                        d = self.__get_dummy_program(START_TIME, p.start)
                    dummy_progs.append(d)
                elif p == p1 and p.stop < stop:
                    # gap at the end, try to find next program and fill
                    # the gap or create an 'endless' entry
                    more = self.__epg.sql_get_programs(self.id, stop, -1)
                    if more:
                        d = self.__get_dummy_program(p.stop, more[0].start)
                    else:
                        d = self.__get_dummy_program(p.stop, STOP_TIME)
                    dummy_progs.append(d)
                elif p != p0 and p != p1 and last.stop < p.start:
                    # fill gaps between programs
                    d = self.__get_dummy_program(last.stop, p.start)
                    dummy_progs.append(d)
                last = p
                # Add program. Because of some bad jitter from 60 seconds in
                # __import_programs calling the first one and the last could
                # already be in self.programs
                if (p == new_progs[0] or p == new_progs[-1]) and \
                   p in self.programs:
                    continue
                self.programs.append(p)
                
        for p in dummy_progs:
            # Add program. Because of some bad jitter from 60 seconds in
            # __import_programs calling the first one and the last could
            # already be in self.programs
            if (p == dummy_progs[0] or p == dummy_progs[-1]) and \
                   p in self.programs:
                continue
            self.programs.append(p)

        # sort the programs
        self.programs.sort(lambda a, b: cmp(a.start, b.start))


    def __getitem__(self, key):
        """
        Get a program or a list of programs. Possible usage is
        channel[time] to get the programm running at 'time'
        channel[start:stop] to get the programms between start and stop
        channel[start:] to get all programms beginning at start
        """
        if isinstance(key, slice):
            start = key.start
            stop  = key.stop
        else:
            start = key
            stop  = 0

        if start < START_TIME + 120:
            start = START_TIME + 120
        if stop > 0 and stop > STOP_TIME - 120:
            stop = STOP_TIME - 120

        # get programs
        if self.programs:
            # see if we're missing programs before start
            p = self.programs[0]
            if p.start > start - 60:
                self.__import_programs(start - 60, p.start)
            # see if we're missing programs after end
            p = self.programs[-1]
            if stop == None:
                self.__import_programs(p.stop, -1)
            elif stop == 0 and p.stop < start + 60:
                self.__import_programs(p.stop, start + 60)
            elif p.stop < stop:
                self.__import_programs(p.stop, stop + 60)
        else:
            if stop == 0:
                self.__import_programs(start - 60, start + 60)
            else:
                self.__import_programs(start, stop)

        # return the needed programs
        if stop == 0:
            # only get what's running at time start
            return filter(lambda x: x.start <= start, self.programs)[-1]
        elif stop == None:
            # get everything from time start onwards
            return filter(lambda x: x.stop > start, self.programs)

        elif stop > 0:
            # get everything from time start to time stop
            return filter(lambda x: (x.start <= start and x.stop > start) or \
                          (x.start > start and x.stop < stop) or \
                          (x.start < stop and x.stop >= stop),
                          self.programs)
        raise Exception('bad request: %s-%s' % (start, stop))


    def __str__(self):
        return '%s: %s' % (self.id, self.name)
