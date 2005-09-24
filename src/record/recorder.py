# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recorder.py - base class for recorder plugins
# -----------------------------------------------------------------------------
# $Id$
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
import os
import time
import string
import copy
import logging

import mbus

# kaa imports
from kaa.notifier import OneShotTimer, Callback

# freevo imports
import config

# record imports
from record_types import *

# get logging object
log = logging.getLogger('record')

# internal 'unique' ids
UNKNOWN_ID  = -1
IN_PROGRESS = -2

# recording daemon
DAEMON = {'type': 'home-theatre', 'module': 'record-daemon'}



class RecorderList(object):
    def __init__(self, server):
        self.recorder = []
        self.best_recorder = {}
        self.server = server

        # add notify callback
        server.mbus_instance.register_entity_notification(self.mbus_entity_update)
        server.mbus_instance.register_event('vdr.started', self.mbus_eventhandler)
        server.mbus_instance.register_event('vdr.stopped', self.mbus_eventhandler)



    def append(self, recorder):
        if not recorder in self.recorder:
            log.info('add %s' % recorder)
            self.recorder.append(recorder)
        self.check()


    def remove(self, recorder):
        if recorder in self.recorder:
            log.info('remove %s' % recorder)
            self.recorder.remove(recorder)
            self.check()


    def check(self):
        """
        Check all possible recorders.
        """
        # reset best recorder list
        self.best_recorder = {}
        for p in self.recorder:
            for l in p.current_bouquets:
                for c in l:
                    if not self.best_recorder.has_key(c):
                        self.best_recorder[c] = -1, None
                    if self.best_recorder[c][0] < p.rating:
                        self.best_recorder[c] = p.rating, p, p.device
        for c in self.best_recorder:
            self.best_recorder[c] = self.best_recorder[c][1]
        self.server.check_recordings(True)


    def __iter__(self):
        return self.recorder.__iter__()


    def mbus_entity_update(self, entity):
        """
        Update recorders on entity changes.
        """
        if not entity.matches(DAEMON):
            # no recorder
            return

        if entity.present:
            entity.call('devices.list', Callback(self.mbus_list_cb, entity))
            return

        for r in self.recorder[:]:
            if r.entity == entity:
                log.info('lost recorder %s', r)
                self.remove(r)


    def mbus_list_cb(self, result, entity):
        """
        RPC return for device.list()
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return
        for device in result.arguments:
            Recorder(entity, self, device)


    def mbus_eventhandler(self, event):
        addr = event.header.srcAdr
        args = event.payload[0].args
        name = event.payload[0].name
        for r in self.recorder:
            if r.entity.addr != addr:
                continue
            for rec in r.recordings:
                if rec.id == args[0]:
                    break
            else:
                continue
            break
        else:
            log.error('unable to find recorder for event')
            return True

        if name.endswith('started'):
            self.server.start_recording(rec.recording)
        else:
            self.server.stop_recording(rec.recording)
        return True


class RemoteRecording(object):
    """
    Wrapper for recordings to add 'id' and 'valid' for internal use inside
    the recorder.
    """
    def __init__(self, recording, start):
        self.recording = recording
        self.id = UNKNOWN_ID
        self.valid = True
        self.start = start


class Recorder(object):
    """
    External recorder
    """
    next_livetv_id = 1

    def __init__(self, entity, handler, device):
        self.type = 'recorder'
        # reference to the recordserver
        self.handler = handler
        self.entity = entity
        self.device = device
        self.name = '%s:%s' % (entity.addr['id'], device)
        self.recordings = []
        self.check_timer = OneShotTimer(self.check_recordings)
        self.livetv = {}
        self.entity.call('device.describe', self.describe_cb, device)
        self.rating = 0


    def __str__(self):
        return '<Recorder for %s>' % (self.name)


    def describe_cb(self, result):
        """
        RPC return for device.describe()
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.handler.remove(self)
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.handler.remove(self)
            return

        self.possible_bouquets = result.arguments[2]
        self.rating = result.arguments[1]
        self.update()


    def update(self):
        if self.livetv:
            # return the listing with the first channel in it
            # (they all need to be in the same list, so no problem here)
            self.current_bouquets = [ c for c in self.possible_bouquets \
                                      if self.livetv.values()[0][0] in c ]
        else:
            self.current_bouquets = self.possible_bouquets
        self.handler.append(self)


    def get_url(self, rec):
        """
        Return url (e.g. filename) for the given recording
        """
        if not rec.url:
            filename_array = { 'progname': String(rec.name),
                               'title'   : String(rec.subtitle) }

            filemask = config.TV_RECORD_FILEMASK % filename_array
            filename = ''
            for letter in time.strftime(filemask, time.localtime(rec.start)):
                if letter in string.ascii_letters + string.digits:
                    filename += letter
                elif filename and filename[-1] != '_':
                    filename += '_'
            filename = filename.rstrip(' -_:') + '.mpg'
            filename = 'file:' + os.path.join(config.TV_RECORD_DIR, filename)
        else:
            # check filename
            if rec.url.startswith('file:'):
                filename = os.path.join(config.TV_RECORD_DIR, rec.url[5:])
                if filename.endswith('.suffix'):
                    filename = os.path.splitext(filename)[0] + '.mpg'
                filename = 'file:' + filename
        if filename.startswith('file:'):
            # check if target dir exists
            d = os.path.dirname(filename[5:])
            if not os.path.isdir(d):
                os.makedirs(d)
        return filename


    # ****************************************************************************
    # add or remove a recording
    # ****************************************************************************


    def record(self, recording, start, stop):
        """
        Add a recording.
        """
        self.recordings.append(RemoteRecording(recording, start))

        # update recordings at the remote application
        self.check_timer.start(0.1)


    def remove(self, recording):
        """
        Remove a recording
        """
        for remote in self.recordings:
            if remote.recording == recording:
                remote.valid = False

        # update recordings at the remote application
        self.check_timer.start(0.1)


    def check_recordings(self):
        """
        Check the internal list of recordings and add or remove them from
        the recorder.
        """
        for remote in copy.copy(self.recordings):
            if remote.id == IN_PROGRESS:
                # already checking
                break
            if remote.id == UNKNOWN_ID and not remote.valid:
                # remove it from the list, looks like the recording
                # was already removed and not yet scheduled
                log.error('UNKNOWN_ID')
                self.recordings.remove(remote)
                continue
            if remote.id == UNKNOWN_ID:
                # add the recording
                rec      = remote.recording
                channel  = rec.channel
                filename = self.get_url(rec)
                rec.url  = filename
                log.info('%s: schedule %s' % (self.name, String(rec.name)))
                self.entity.call('vdr.record', self.start_recording_cb, self.device,
                                 channel, remote.start, rec.stop + rec.stop_padding,
                                 filename, ())
                remote.id = IN_PROGRESS
                break
            if not remote.valid:
                # remove the recording
                log.info('%s: remove %s' % (self.name, String(remote.recording.name)))
                try:
                    self.entity.call('vdr.remove', self.remove_recording_cb, remote.id)
                except:
                    pass
                self.recordings.remove(remote)
                break
        # the function will be rescheduled by mbus return
        return False


    def start_recording_cb(self, result):
        """
        Callback for vdr.record
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.handler.remove(self)
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.handler.remove(self)
            return

        # result is an unique id
        for remote in self.recordings:
            if remote.id == IN_PROGRESS:
                remote.id = result.arguments
                break
        else:
            log.info('id not found')

        # check more recordings
        self.check_recordings()


    def remove_recording_cb(self, result):
        """
        Callback for vdr.remove
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.handler.remove(self)
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.handler.remove(self)
            return
        # check more recordings
        self.check_recordings()


    # ****************************************************************************
    # live tv handling
    # ****************************************************************************


    def start_livetv(self, channel, url):
        log.info('start live tv')

        self.entity.call('vdr.record', self.start_livetv_cb, self.device,
                         channel, 0, 2147483647, url, ())
        id = Recorder.next_livetv_id
        Recorder.next_livetv_id = id + 1
        self.livetv[id] = channel, None
        self.update()
        return id


    def start_livetv_cb(self, result):
        """
        Callback for vdr.record for live tv
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.handler.remove(self)
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.handler.remove(self)
            return
        log.info('return for live tv start')
        for key, value in self.livetv.items():
            self.livetv[key] = value[0], result.arguments
            break
        else:
            log.error('key not found')


    def stop_livetv(self, id):
        log.info('stop live tv')
        if not id in self.livetv:
            # FIXME: handle error
            log.error('id not in list')
            return
        channel, remote_id = self.livetv[id]
        del self.livetv[id]
        if remote_id != None:
            self.entity.call('vdr.remove', self.stop_livetv_cb, remote_id)
        else:
            log.error('remote id is None')
        self.update()


    def stop_livetv_cb(self, result):
        """
        Callback for vdr.remove for live tv
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.handler.remove(self)
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.handler.remove(self)
            return
        log.info('return for live tv stop')
        return
