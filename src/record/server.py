# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# server.py -
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

import copy
import os
import time

import notifier
import pyepg

import sysconfig
import config
import util

from mcomm import RPCServer, RPCError, RPCReturn

from recording import Recording
from favorite import Favorite

# FIXME: move to config file
EPGDB = os.path.join(config.FREEVO_CACHEDIR, 'epgdb')


CONFLICT  = 'conflict'
SCHEDULED = 'scheduled'
MISSED    = 'missed'
SAVED     = 'saved'

class RecordServer(RPCServer):
    def __init__(self):
        RPCServer.__init__(self, 'recordserver')
        self.epgdb = pyepg.get_epg(EPGDB)
        self.fxdfile = sysconfig.cachefile('recordserver.fxd')
        self.load()


    def resolve_conflict(self, recordings):
        # Sort by priority ans can all except the one with the
        # lowest priority again if the conflict is now solved.
        #
        # FIXME:
        # This is a very poor solution, maybe we have more than one card
        # and two items at the same time doesn't matter at all. Or maybe
        # a plugin can record two items at the same time. So this function
        # needs a huge update!!!
        recordings.sort(lambda l, o: cmp(l.priority,o.priority))
        self.scan_for_conflicts(recordings[:-1])


    def scan_for_conflicts(self, recordings):
        # Sort by start time
        recordings.sort(lambda l, o: cmp(l.start,o.start))

        # Remove conflict status and set the scheduled. Maybe the old
        # conflict is gone now
        for r in recordings:
            if r.status == CONFLICT:
                r.status = SCHEDULED

        # all conflicts found
        conflicts = []

        # Check all recordings in the list for conflicts
        for r in recordings:
            if r.status == CONFLICT:
                # Already marked as conflict
                continue
            current = []
            # Set stop time for the conflict area to current stop time. The
            # start time doesn't matter since the recordings are sorted by
            # start time and this is the first
            stop = r.stop
            while True:
                for c in recordings[recordings.index(r)+1:]:
                    # Check all recordings after the current 'r' if the
                    # conflict
                    if c.status == CONFLICT:
                        # Already marked as conflict
                        continue
                    if c.start < stop:
                        # Found a conflict here. Mark the item as conflict and
                        # add to the current conflict list
                        current.append(c)
                        c.status = CONFLICT
                        # Get new stop time and repeat the scanning with it
                        # starting from 'r' + 1
                        stop = max(stop, c.stop)
                        break
                else:
                    # No new conflicts found, the while True is done
                    break
            if current:
                # Conflict found. Mark the current 'r' as conflict and
                # add it to the conflict list. 'current' will be reset to
                # [] for the next scanning to get groups of conflicts
                r.status = CONFLICT
                conflicts.append([ r ] + current)

        for c in conflicts:
            # Resolve the conflicts
            self.resolve_conflict(c)


    def check_recordings(self):
        ctime = time.time()
        # remove informations older than one week
        self.recordings = filter(lambda r: r.start > ctime - 60*60*24*7,
                                 self.recordings)
        # sort by start time
        self.recordings.sort(lambda l, o: cmp(l.start,o.start))

        # check recordings we missed
        for r in self.recordings:
            if r.stop < ctime and r.status != SAVED:
                r.status = MISSED

        # scan for conflicts
        self.scan_for_conflicts(filter(lambda r: r.stop > ctime and \
                                       r.status in (CONFLICT, SCHEDULED),
                                       self.recordings))

        # print current schedule
        print
        print 'recordings:'
        for r in self.recordings:
            print ' ',
            for e in r.short_list():
                print String(e),
            print
        print
        print 'favorites:'
        for f in self.favorites:
            print ' ',
            for e in f.short_list():
                print String(e),
            print
        print
        print 'next record id', self.rec_id
        print 'next favorite id', self.fav_id

        # save status
        if os.path.isfile(self.fxdfile):
            os.unlink(self.fxdfile)
        fxd = util.fxdparser.FXD(self.fxdfile)
        for r in self.recordings:
            fxd.add(r)
        for r in self.favorites:
            fxd.add(r)
        fxd.save()


    def check_favorites(self):
        print 'checking favorites against epg'
        for f in self.favorites:
            for entry in self.epgdb.search_programs(f.name):
                dbid, channel, title, subtitle, foo, descr, \
                      start, stop = entry[:8]
                if not f.match(title, channel, start):
                    continue
                r = Recording(self.rec_id, title, channel, 1000+f.priority,
                              start, stop)
                if r in self.recordings:
                    continue
                print '  added %s: %s (%s)' % (String(channel),
                                               String(title), start)
                self.recordings.append(r)
                self.rec_id += 1
        self.check_recordings()


    def __load_recording(self, parser, node):
        try:
            r = Recording()
            r.parse_fxd(parser, node)
            self.recordings.append(r)
            self.rec_id = max(self.rec_id, r.id + 1)
        except Exception, e:
            print 'server.load_recording:', e


    def __load_favorite(self, parser, node):
        try:
            f = Favorite()
            f.parse_fxd(parser, node)
            self.favorites.append(f)
            self.fav_id = max(self.fav_id, f.id + 1)
        except Exception, e:
            print 'server.load_favorite:', e


    def load(self):
        self.rec_id = 0
        self.fav_id = 0
        self.recordings = []
        self.favorites = []
        try:
            fxd = util.fxdparser.FXD(self.fxdfile)
            fxd.set_handler('recording', self.__load_recording)
            fxd.set_handler('favorite', self.__load_favorite)
            fxd.parse()
        except Exception, e:
            print 'FXDFile corrupt:', self.fxdfile
            print e

        self.check_favorites()



    #
    # home.theatre.recording rpc commands
    #

    def __rpc_recording_list__(self, addr, val):
        self.parse_parameter(val, () )
        ret = []
        for r in self.recordings:
            ret.append(r.short_list())
        return RPCReturn(ret)


    def __rpc_recording_describe__(self, addr, val):
        id = self.parse_parameter(val, ( int, ))
        print 'recording.describe: %s' % id
        for r in self.recordings:
            if r.id == id:
                return RPCReturn(r.long_list())
        return RPCError('Recording not found')


    def __rpc_recording_add__(self, addr, val):
        name, channel, priority, start, stop, filename, info = \
              self.parse_parameter(val, ( unicode, unicode, int, int, int,
                                          str, dict ) )
        print 'recording.add: %s' % String(name)
        r = Recording(self.rec_id, name, channel, priority, start, stop,
                      filename, info)
        if r in self.recordings:
            return RPCError('Already scheduled')
        self.recordings.append(r)
        self.rec_id += 1
        self.check_recordings()
        return RPCReturn(self.rec_id - 1)


    def __rpc_recording_remove__(self, addr, val):
        id = self.parse_parameter(val, ( int, ))
        print 'recording.remove: %s' % id
        for r in self.recordings:
            if r.id == id:
                r.status = 'deleted'
                self.check_recordings()
                return RPCReturn()
        return RPCError('Recording not found')


    def __rpc_recording_modify__(self, addr, val):
        id, key_val = self.parse_parameter(val, ( int, dict ))
        print 'recording.modify: %s' % id
        for r in self.recordings:
            if r.id == id:
                cp = copy.copy(self.recordings[id])
                for key in key_val:
                    setattr(cp, key, key_val[key])
                self.recordings[self.recordings.index(r)] = cp
                return RPCReturn()
        return RPCError('Recording not found')


    #
    # home.theatre.favorite rpc commands
    #

    def __rpc_favorite_update__(self, addr=None, val=[]):
        self.check_favorites()
        return RPCReturn()


    def __rpc_favorite_add__(self, addr, val):
        name, channel, priority, day, time = \
              self.parse_parameter(val, ( unicode, list, int, list, list ))
        print 'favorite.add: %s' % String(name)
        f = Favorite(self.fav_id, name, channel, priority, day, time)
        if f in self.favorites:
            return RPCError('Already scheduled')
        self.favorites.append(f)
        self.fav_id += 1
        return self.__rpc_favorite_update__()
