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


# python imports
import copy
import os
import time
import traceback

# notifier
import notifier

# pyepg
import pyepg

# freevo imports
import sysconfig
import config
import util
import plugin

# mbus support
from mcomm import RPCServer, RPCError, RPCReturn

# record imports
import recorder
from recording import Recording
from favorite import Favorite


# FIXME: move to config file
EPGDB = os.path.join(config.FREEVO_CACHEDIR, 'epgdb')


CONFLICT  = 'conflict'
SCHEDULED = 'scheduled'
RECORDING = 'recording'
MISSED    = 'missed'
SAVED     = 'saved'
DELETED   = 'deleted'


class RecordServer(RPCServer):
    """
    Class for the recordserver. It handles the rpc calls and checks the
    schedule for recordings and favorites. The recordings itself are
    done by plugins in record/plugins.
    """
    def __init__(self):
        RPCServer.__init__(self, 'recordserver')
        plugin.init(exclusive = [ 'record' ])
        # db access to match favorites
        self.epgdb = pyepg.get_epg(EPGDB)
        # file to load / save the recordings and favorites
        self.fxdfile = sysconfig.cachefile('recordserver.fxd')
        # timer for record callback
        self.rec_timer = None
        # load the config file and rebuild index
        self.load(True)


    def resolve_conflict(self, recordings):
        """
        Resolve a conflict for recordings. A higher priority wins. A
        conflict doesn't mean they can't be all recorded, maybe a plugin can
        record two programs at a time or there is more than one plugin.
        """
        # FIXME:
        # This is a very poor solution, maybe we have more than one card
        # and two items at the same time doesn't matter at all. Or maybe
        # a plugin can record two items at the same time. So this function
        # needs a huge update!!!
        print 'recordserver.resolve_conflict'
        for r in recordings:
            print String(r)
        recordings.sort(lambda l, o: cmp(l.priority,o.priority))
        # check if a conflict is recorded right now
        for r in recordings:
            if r.recorder:
                # This recording active right now. It wins against all
                # priorities, we don't stop a running recording
                r.status = RECORDING
                
        for r in recordings:
            if r.status == RECORDING:
                continue
            for c in filter(lambda l: l.status in (SCHEDULED, RECORDING),
                            recordings):
                if c.start <= r.start <= c.stop or \
                       r.start <= c.start <= r.stop:
                    break
            else:
                # no conflict for this recording
                r.status = SCHEDULED
        print 'result:'
        for r in recordings:
            print String(r)
        print


    def scan_for_conflicts(self, recordings):
        """
        Scan the scheudle for conflicts. A conflict is a list of recordings
        with overlapping times. After scanning the conflicts will be
        resolved by resolve_conflict.
        """
        print 'recordserver.scan_for_conflicts'
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
        """
        Check the current recordings. This includes checking conflicts,
        removing old entries. At the end, the timer is set for the next
        recording.
        """
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
        to_check = (CONFLICT, SCHEDULED, RECORDING)
        self.scan_for_conflicts(filter(lambda r: r.stop > ctime and \
                                       r.status in to_check, self.recordings))

        # print current schedule
        print
        print 'recordings:'
        for r in self.recordings:
            print r
        print
        print 'favorites:'
        for f in self.favorites:
            print f
        print
        print 'next ids: record=%s favorite=%s' % (self.rec_id, self.fav_id)

        # save status
        self.save()

        # set wakeup call
        if self.rec_timer:
            notifier.removeTimer(self.rec_timer)
        for r in self.recordings:
            if r.status == SCHEDULED:
                secs = max(0, int(r.start - time.time()))
                print 'recordserver.check_recordings: next in %s sec' % timer
                self.rec_timer = notifier.addTimer(secs * 1000, self.record)
                break


    def check_favorites(self):
        """
        Check favorites against the database and add them to the list of
        recordings
        """
        print 'recordserver.check_favorites'
        for f in copy.copy(self.favorites):
            for entry in self.epgdb.search_programs(f.name):
                dbid, channel, title, subtitle, foo, descr, \
                      start, stop = entry[:8]
                if not f.match(title, channel, start):
                    continue
                r = Recording(self.rec_id, title, channel, 1000+f.priority,
                              start, stop)
                r.favorite = True
                if r in self.recordings:
                    # This does not only avoids adding recordings twice, it
                    # also prevents from added a deleted favorite as active
                    # again.
                    continue
                print '  added %s: %s (%s)' % (String(channel),
                                               String(title), start)
                self.recordings.append(r)
                self.rec_id += 1
                if f.once:
                    self.favorites.remove(f)
                    break
        # now check the schedule again
        self.check_recordings()


    def record(self):
        """
        Record a program now using one of the record plugins
        """
        # FIXME: handle not conflicting recordings when the padding
        # has a conflict!
        for r in self.recordings:
            if r.status == SCHEDULED:
                break
        else:
            print 'recordserver.record: unable to find the next recording'
            # This should never happen
            self.check_recordings()
            return False
        if not recorder.plugins:
            print 'recordserver.record: no plugins found'
            return False

        # FIXME: find the correct recorder
        record_plugin = recorder.plugins[0]

        # remove timer that called this function
        notifier.removeTimer(self.rec_timer)
        self.rec_timer = None

        if record_plugin.item and record_plugin.item.stop > time.time():
            # The recorder is recording something. If we are at this point
            # it means that the current recording has a padding overlapping
            # the recording of the last recording. So just wait until the
            # old recording is done
            secs = record_plugin.item.stop - time.time()
            self.rec_timer = notifier.addTimer(secs * 1000, self.record)
            return False
        
        print 'recordserver.record: start recording'
        print r
        # set status to recording
        r.status = RECORDING

        # schedule next recording
        for next in self.recordings:
            if next.status == SCHEDULED:
                secs = max(0, int(next.start - time.time()))
                print 'recordserver.record: next in %s sec' % timer
                self.rec_timer = notifier.addTimer(secs * 1000, self.record)
                break

        # FIXME: handle more than one recorder
        try:
            record_plugin.record(self, r)
        except:
            print 'recordserver.record: plugin failed'
            traceback.print_exc()
            r.status = MISSED
        return False


    #
    # load / save fxd file with recordings and favorites
    #

    def __load_recording(self, parser, node):
        """
        callback for <recording> in the fxd file
        """
        try:
            r = Recording()
            r.parse_fxd(parser, node)
            self.recordings.append(r)
            self.rec_id = max(self.rec_id, r.id + 1)
        except Exception, e:
            print 'recordserver.load_recording:', e


    def __load_favorite(self, parser, node):
        """
        callback for <favorite> in the fxd file
        """
        try:
            f = Favorite()
            f.parse_fxd(parser, node)
            self.favorites.append(f)
            self.fav_id = max(self.fav_id, f.id + 1)
        except Exception, e:
            print 'recordserver.load_favorite:', e


    def load(self, rebuild=False):
        """
        load the fxd file
        """
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
            print 'recordserver.load: %s corrupt:' % self.fxdfile
            print e

        if rebuild:
            for r in self.recordings:
                r.id = self.recordings.index(r)
            for f in self.favorites:
                f.id = self.favorites.index(f)
        self.check_favorites()


    def save(self):
        """
        save the fxd file
        """
        if os.path.isfile(self.fxdfile):
            os.unlink(self.fxdfile)
        fxd = util.fxdparser.FXD(self.fxdfile)
        for r in self.recordings:
            fxd.add(r)
        for r in self.favorites:
            fxd.add(r)
        fxd.save()


    #
    # home.theatre.recording rpc commands
    #

    def __rpc_recording_list__(self, addr, val):
        """
        list the current recordins in a short form.
        result: [ ( id channel priority start stop status ) (...) ]
        """
        self.parse_parameter(val, () )
        ret = []
        for r in self.recordings:
            ret.append(r.short_list())
        return RPCReturn(ret)


    def __rpc_recording_describe__(self, addr, val):
        """
        send a detailed description about a recording
        parameter: id
        result: ( id name channel priority start stop status padding info )
        """
        id = self.parse_parameter(val, ( int, ))
        print 'recording.describe: %s' % id
        for r in self.recordings:
            if r.id == id:
                return RPCReturn(r.long_list())
        return RPCError('Recording not found')


    def __rpc_recording_add__(self, addr, val):
        """
        add a new recording
        parameter: name channel priority start stop optionals
        optionals: subtitle, url, padding, description
        """
        name, channel, priority, start, stop, info = \
              self.parse_parameter(val, ( unicode, unicode, int, int, int,
                                          dict ) )
        print 'recording.add: %s' % String(name)
        r = Recording(self.rec_id, name, channel, priority, start, stop,
                      info = info)
        if r in self.recordings:
            r = self.recordings[self.recordings.index(r)]
            if r.status == DELETED:
                r.status   = 'scheduled'
                r.favorite = False
                self.check_recordings()
                return RPCReturn(self.rec_id - 1)
            return RPCError('Already scheduled')
        self.recordings.append(r)
        self.rec_id += 1
        self.check_recordings()
        return RPCReturn(self.rec_id - 1)


    def __rpc_recording_remove__(self, addr, val):
        """
        remove a recording
        parameter: id
        """
        id = self.parse_parameter(val, ( int, ))
        print 'recording.remove: %s' % id
        for r in self.recordings:
            if r.id == id:
                if r.status == RECORDING:
                    r.status = SAVED
                    r.recorder.stop()
                else:
                    r.status = DELETED
                self.check_recordings()
                return RPCReturn()
        return RPCError('Recording not found')


    def __rpc_recording_modify__(self, addr, val):
        """
        modify a recording
        parameter: id [ ( var val ) (...) ]
        """
        id, key_val = self.parse_parameter(val, ( int, dict ))
        print 'recording.modify: %s' % id
        for r in self.recordings:
            if r.id == id:
                if r.status == RECORDING:
                    return RPCError('Currently recording')
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
        """
        updates favorites with data from the database
        """
        self.check_favorites()
        return RPCReturn()


    def __rpc_favorite_add__(self, addr, val):
        """
        add a favorite
        parameter: name channels priority days times
        channels is a list of channels
        days is a list of days ( 0 = Sunday - 6 = Saturday )
        times is a list of hh:mm-hh:mm
        """
        print val
        name, channels, priority, days, times, once = \
              self.parse_parameter(val, ( unicode, list, int, list, list,
                                          bool ))
        print once
        print 'favorite.add: %s' % String(name)
        f = Favorite(self.fav_id, name, channels, priority, days, times, once)
        if f in self.favorites:
            return RPCError('Already scheduled')
        self.favorites.append(f)
        self.fav_id += 1
        return self.__rpc_favorite_update__()
