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
import sys
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
import conflict

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
        self.fxdfile = sysconfig.datafile('recordserver.fxd')
        # get list of best recorder for each channel
        self.best_recorder = {}
        for p in recorder.plugins:
            for dev, rating, listing in p.get_channel_list():
                for l in listing:
                    for c in l:
                        if not self.best_recorder.has_key(c):
                            self.best_recorder[c] = -1, None
                        if self.best_recorder[c][0] < rating:
                            self.best_recorder[c] = rating, p, dev
        for c in self.best_recorder:
            self.best_recorder[c] = self.best_recorder[c][1:]
        # variables for check_recordings
        self.check_timer = None
        self.check_running = False
        self.check_needed = False
        # load the recordings file
        self.load(True)


    def check_recordings(self):
        """
        Wrapper for __check_recordings to avoid recursive calling
        """
        if not self.check_running:
            print 'start timer'
            self.check_timer   = notifier.addTimer(0, self.__check_recordings)
            self.check_running = True
            self.check_needed  = False
        else:
            print 'foo'
            self.check_needed  = True


    def __check_recordings(self):
        """
        Check the current recordings. This includes checking conflicts,
        removing old entries. At the end, the timer is set for the next
        recording.
        """
        notifier.removeTimer(self.check_timer)
        self.check_timer = None

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
        next_recordings = filter(lambda r: r.stop > ctime and \
                                 r.status in to_check, self.recordings)
        for r in next_recordings:
            try:
                r.recorder = self.best_recorder[r.channel]
                if r.status != RECORDING:
                    r.status   = SCHEDULED
            except KeyError:
                r.recorder = None, None
                r.status   = CONFLICT
                print 'no recorder for recording'
                print r

        conflict.resolve(next_recordings)

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

        # send schedule to plugins
        for p in recorder.plugins:
            p.schedule(filter(lambda x: x.recorder[0] == p, next_recordings),
                       self)

        print 'checking took %s seconds' % \
              (float(int((time.time() - ctime) * 100)) / 100)

        # check if something requested a new check while this function was
        # running. If so, call the check_recordings functions again
        self.check_running = False
        if self.check_needed:
            self.check_recordings()
        return False


    def check_favorites(self):
        """
        Check favorites against the database and add them to the list of
        recordings
        """
        print 'recordserver.check_favorites'
        for f in copy.copy(self.favorites):
            for entry in self.epgdb.search_programs(f.name):
                dbid, channel, title, subtitle, descr, episode, \
                      start, stop = entry[:8]
                if not f.match(title, channel, start):
                    continue
                r = Recording(self.rec_id, title, channel, f.priority,
                              start, stop)
                if r in self.recordings:
                    # This does not only avoids adding recordings twice, it
                    # also prevents from added a deleted favorite as active
                    # again.
                    continue
                print '  added %s: %s (%s)' % (String(channel),
                                               String(title), start)
                f.add_data(r)
                self.recordings.append(r)
                self.rec_id += 1
                if f.once:
                    self.favorites.remove(f)
                    break
        # now check the schedule again
        self.check_recordings()


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
        for r in self.recordings:
            if r.id == id:
                return RPCReturn(r.long_list())
        return RPCError('Recording not found')


    def __rpc_recording_add__(self, addr, val):
        """
        add a new recording
        parameter: name channel priority start stop optionals
        optionals: subtitle, url, start-padding, stop-padding, description
        """
        if len(val) == 2 or len(val) == 5:
            # missing optionals
            val.append([])
        if len(val) == 3:
            # add by dbid
            dbid, priority, info = \
                  self.parse_parameter(val, ( int, int, dict ))
            channel, name, subtitle, descr, episode, \
                     start, stop = self.epgdb.get_programs_by_id(dbid)[1:8]
            if subtitle and not info.has_key('subtitle'):
                info['subtitle'] = subtitle
            if descr and not info.has_key('description'):
                info['description'] = descr
        else:
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
        name, channels, priority, days, times, once = \
              self.parse_parameter(val, ( unicode, list, int, list, list,
                                          bool ))
        print 'favorite.add: %s' % String(name)
        f = Favorite(self.fav_id, name, channels, priority, days, times, once)
        if f in self.favorites:
            return RPCError('Already scheduled')
        self.favorites.append(f)
        self.fav_id += 1
        return self.__rpc_favorite_update__()


    def __rpc_favorite_list__(self, addr, val):
        """
        """
        self.parse_parameter(val, () )
        ret = []
        for f in self.favorites:
            ret.append(f.long_list())
        return RPCReturn(ret)
