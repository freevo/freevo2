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
import logging

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
import external
from types import *
from recording import Recording
from favorite import Favorite
import conflict

# get logging object
log = logging.getLogger('record')

# FIXME: move to config file
EPGDB = sysconfig.datafile('epgdb')

# external recording daemon
DAEMON = {'type': 'home-theatre', 'module': 'record-daemon'}

class RecordServer(RPCServer):
    """
    Class for the recordserver. It handles the rpc calls and checks the
    schedule for recordings and favorites. The recordings itself are
    done by plugins in record/plugins.
    """
    def __init__(self):
        RPCServer.__init__(self, 'recordserver')
        self.clients = []
        config.detect('tvcards', 'channels')
        # file to load / save the recordings and favorites
        self.fxdfile = sysconfig.datafile('recordserver.fxd')
        # load the recordings file
        self.load(True)
        # init the recorder
        plugin.init(exclusive = [ 'record' ])
        # get list of best recorder for each channel
        self.check_recorder(False)
        # variables for check_recordings
        self.check_timer = None
        self.check_running = False
        self.check_needed = False
        # add notify callback
        self.mbus_instance.register_entity_notification(self.__entity_update)
        # check everything
        self.check_favorites()


    def check_recorder(self, update=True):
        """
        Check all possible recorders. If 'update' is True, all recordings
        will be re-checked.
        """
        # clear the conflict cache
        conflict.clear_cache()
        # reset best recorder list
        self.best_recorder = {}
        for p in recorder.plugins:
            p.server = self
            for dev, rating, listing in p.get_channel_list():
                for l in listing:
                    for c in l:
                        if not self.best_recorder.has_key(c):
                            self.best_recorder[c] = -1, None
                        if self.best_recorder[c][0] < rating:
                            self.best_recorder[c] = rating, p, dev
        for c in self.best_recorder:
            self.best_recorder[c] = self.best_recorder[c][1:]
        if update:
            # update recordings
            self.check_recordings()


    def send_update(self):
        """
        Send and updated list to the clients
        """
        ret = []
        for r in self.recordings:
            ret.append(r.short_list())
        for c in self.clients:
            log.info('send update to %s' % c)
            self.mbus_instance.send_event(c, 'record.list.update', ret)


    def __check_epg(self):
        """
        Update the recording list with the epg
        """
        ctime = time.time()
        to_check = (CONFLICT, SCHEDULED, RECORDING)
        next_recordings = filter(lambda r: r.stop + r.stop_padding > ctime \
                                 and r.status in to_check, self.recordings)

        # check if the show is still in the db or maybe moved
        for r in next_recordings:
            if r.status == RECORDING:
                # do not move a current running recording
                continue
            results = pyepg.search(r.name, r.channel)
            for p in results:
                if p.start == r.start and p.stop == r.stop:
                    break
            else:
                # try to find it
                for p in results:
                    if r.start - 20 * 60 < p.start < r.start + 20 * 60:
                        # found it again
                        r.start = p.start
                        r.stop = p.stop
                        log.info('changed schedule\n%s' % r)
                        break
                else:
                    log.info('unable to find recording in epg:\n%s' % r)
        return True


    def check_recordings(self):
        """
        Wrapper for __check_recordings to avoid recursive calling
        """
        if not self.check_running:
            self.check_timer   = notifier.addTimer(0, self.__check_recordings)
            self.check_running = True
            self.check_needed  = False
        else:
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
        next_recordings = filter(lambda r: r.stop + r.stop_padding > ctime \
                                 and r.status in to_check, self.recordings)

        # check if the show is still in the db or maybe moved
        for r in next_recordings:
            results = pyepg.search(r.name, r.channel)
            for p in results:
                if p.start == r.start and p.stop == r.stop:
                    break
            else:
                # try to find it
                for p in results:
                    if r.start - 20 * 60 < p.start < r.start + 20 * 60:
                        # found it again
                        log.info('changed schedule\n%s' % r)
                        r.start = p.start
                        r.stop = p.stop
                        break
                else:
                    log.info('unable to find recording in epg:\n%s' % r)

        for r in next_recordings:
            try:
                r.recorder = self.best_recorder[r.channel]
                if r.status != RECORDING:
                    r.status   = SCHEDULED
            except KeyError:
                r.recorder = None, None
                r.status   = CONFLICT
                log.error('no recorder for recording:\n  %s', str(r))

        # resolve conflicts (and get the time it took for debug)
        t1 = time.time()
        conflict.resolve(next_recordings)
        t2 = time.time()

        info = 'recordings:\n'
        for r in self.recordings:
            info += '%s\n' % r
        log.info(info)
        info = 'favorites:\n'
        for f in self.favorites:
            info += '%s\n' % f
        log.info(info)
        log.info('next ids: record=%s favorite=%s' % \
                 (self.rec_id, self.fav_id))

        # save status
        self.save()

        # send schedule to plugins
        for p in recorder.plugins:
            p.schedule(filter(lambda x: x.recorder[0] == p, next_recordings))

        log.info('checking took %2.2f seconds' % (t2 - t1))

        # send update
        self.send_update()

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
        log.info('recordserver.check_favorites')
        # check epg if something changed
        self.__check_epg()
        for f in copy.copy(self.favorites):
            for p in pyepg.search(f.name):
                if not f.match(p.title, p.channel.id, p.start):
                    continue
                r = Recording(self.rec_id, p.title, p.channel.id, f.priority,
                              p.start, p.stop)
                if r in self.recordings:
                    # This does not only avoids adding recordings twice, it
                    # also prevents from added a deleted favorite as active
                    # again.
                    continue
                r.episode  = p.episode
                r.subtitle = p.subtitle
                r.description = p.description
                log.info('added %s: %s (%s)' % (String(p.channel.id),
                                                String(p.title), p.start))
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
            log.exception('recordserver.load_recording')


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
            log.exception('recordserver.load_favorite:')


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
            log.exception('recordserver.load: %s corrupt:' % self.fxdfile)

        if rebuild:
            for r in self.recordings:
                r.id = self.recordings.index(r)
            for f in self.favorites:
                f.id = self.favorites.index(f)


    def save(self):
        """
        save the fxd file
        """
        if not len(self.recordings) and not len(self.favorites):
            # do not save here, it is a bug I havn't found yet
            log.info('do not save fxd file')
            return
        try:
            log.info('save fxd file')
            if os.path.isfile(self.fxdfile):
                os.unlink(self.fxdfile)
            fxd = util.fxdparser.FXD(self.fxdfile)
            for r in self.recordings:
                fxd.add(r)
            for r in self.favorites:
                fxd.add(r)
            fxd.save()
        except:
            log.exception('lost the recordings.fxd, send me the trace')


    def __entity_update(self, entity):
        if not entity.present and entity in self.clients:
            log.info('lost client %s' % entity)
            self.clients.remove(entity)

        if not entity.matches(DAEMON):
            return

        if entity.present:
            rec = external.Recorder(entity)
            rec.server = self
        else:
            # FIXME
            pass

    #
    # home.theatre.recording rpc commands
    #

    def __rpc_recording_list__(self, addr, val):
        """
        list the current recordins in a short form.
        result: [ ( id channel priority start stop status ) (...) ]
        """
        if not addr in self.clients:
            log.info('add client %s' % addr)
            self.clients.append(addr)
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
            prog = pyepg.guide.get_program_by_id(dbid)
            if not prog:
                return RPCError('Unknown id')
            channel = prog.channel.id
            name = prog.name
            start = prog.start
            stop = prog.stop
            if prog.subtitle and not info.has_key('subtitle'):
                info['subtitle'] = prog.subtitle
            if prog.episode and not info.has_key('episode'):
                info['episode'] = prog.episode
            if prog.description and not info.has_key('description'):
                info['description'] = prog.description
        else:
            name, channel, priority, start, stop, info = \
                  self.parse_parameter(val, ( unicode, unicode, int, int, int,
                                              dict ) )
        # fix description encoding
        if info.has_key('description') and \
               info['description'].__class__ == str:
            info['description'] = Unicode(info['description'], 'UTF-8')

        log.info('recording.add: %s' % String(name))
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
        log.info('recording.remove: %s' % id)
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
        log.info('recording.modify: %s' % id)
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
        log.info('favorite.add: %s' % String(name))
        f = Favorite(self.fav_id, name, channels, priority, days, times, once)
        if f in self.favorites:
            return RPCError('Already scheduled')
        self.favorites.append(f)
        self.fav_id += 1
        return self.__rpc_favorite_update__()


    def __rpc_favorite_list__(self, addr, val):
        """
        """
        if not addr in self.clients:
            log.info('add client %s' % addr)
            self.clients.append(addr)
        self.parse_parameter(val, () )
        ret = []
        for f in self.favorites:
            ret.append(f.long_list())
        return RPCReturn(ret)


    def __rpc_status__(self, addr, val):
        """
        Send status on rpc status request.
        """
        status = {}
        ctime = time.time()

        # find currently running recordings
        rec = filter(lambda r: r.status == RECORDING, self.recordings)
        if rec:
            # something is recording, add busy time of first recording
            busy = rec[0].stop + rec[0].stop_padding - ctime
            status['busy'] = max(1, int(busy / 60) + 1)

        # find next scheduled recordings for wakeup
        rec = filter(lambda r: r.status == SCHEDULED and \
                     r.start - r.start_padding > ctime, self.recordings)
        if rec:
            # set wakeup time
            status['wakeup'] = rec[0].start - rec[0].start_padding

        # return results
        return RPCReturn(status)
