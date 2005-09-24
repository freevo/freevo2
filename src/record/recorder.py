# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recorder.py - base class for recorder plugins
# -----------------------------------------------------------------------------
# $Id$
#
# This file needs cleanup. A Recorder should not handle one entity, it should
# handle one device on an entity. It will be much easier if a recorder only
# has one device.
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
from kaa.notifier import OneShotTimer

# freevo imports
import config
import plugin
import mcomm

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
    def __init__(self):
        self.recorder = []
        self.best_recorder = {}
        self.server = None

        # add notify callback
        mcomm.register_entity_notification(self.entity_update)
        mcomm.register_event('vdr.started', self.start_event)
        mcomm.register_event('vdr.stopped', self.stop_event)



    def append(self, recorder):
        if not recorder in self.recorder:
            self.recorder.append(recorder)
            recorder.server = self.server
        self.check()
        

    def remove(self, recorder):
        if recorder in self.recorder:
            self.recorder.remove(recorder)
            self.check()

        
    def check(self):
        """
        Check all possible recorders.
        """
        # reset best recorder list
        self.best_recorder = {}
        for p in self.recorder:
            for dev, rating, listing in p.get_channel_list():
                for l in listing:
                    for c in l:
                        if not self.best_recorder.has_key(c):
                            self.best_recorder[c] = -1, None
                        if self.best_recorder[c][0] < rating:
                            self.best_recorder[c] = rating, p, dev
        for c in self.best_recorder:
            self.best_recorder[c] = self.best_recorder[c][1:]

        if self.server:
            self.server.check_recordings(True)
            

    def best_recorder(self, channel):
        return self.best_recorder[channel]
    

    def __iter__(self):
        return self.recorder.__iter__()


    def connect(self, server):
        self.server = server
        for p in self.recorder:
            p.server = server
        
        
    def entity_update(self, entity):
        """
        Update recorders on entity changes.
        """
        if not entity.matches(DAEMON):
            # no recorder
            return

        if entity.present:
            rec = Recorder(entity, self)
            return

        for r in self.recorder:
            if isinstance(r, Recorder) and r.entity == entity:
                log.info('lost recorder')
                r.deactivate()
                return


    def _find_recording(self, event):
        addr = event.header.srcAdr
        args = event.payload[0].args
        for r in self.recorder:
            if isinstance(r, Recorder) and r.entity.addr == addr:
                break
        else:
            log.error('unable to find recorder for event')
            return None, None

        for rec in r.recordings:
            if rec.id == args[0]:
                break
        else:
            log.error('unable to find recording for event')
            return None, r.server
        return rec.recording, r.server
    

    def start_event(self, event):
        rec, server = self._find_recording(event)
        server.start_recording(rec)
        return True


    def stop_event(self, event):
        rec, server = self._find_recording(event)
        server.stop_recording(rec)
        return True


class RemoteRecording(object):
    """
    Wrapper for recordings to add 'id' and 'valid' for internal use inside
    the recorder.
    """
    def __init__(self, recording, device, start):
        self.recording = recording
        self.device = device
        self.id = UNKNOWN_ID
        self.valid = True
        self.start = start


class LiveTV(object):
    def __init__(self, device, channel):
        self.device = device
        self.channel = channel
        self.id = None


class Recorder(object):
    """
    External recorder
    """
    next_livetv_id = 1

    def __init__(self, entity, handler):
        self.type = 'recorder'
        # reference to the recordserver
        self.server = None
        self.handler = handler
        self.entity = entity
        self.name = entity.addr['id']
        self.possible_bouquets = []
        self.current_bouquets = []
        self.recordings = []
        self.check_timer = OneShotTimer(self.check_recordings)
        self.livetv = {}
        self.devices_info()
        log.info('%s: add recorder' % self.name)


    def activate(self):
        self.current_bouquets = []
        used = {}
        for info in self.livetv.values():
            if not info.device in used:
                used[info.device] = []
            if not info.channel in used[info.device]:
                used[info.device].append(info.channel)

        for id, prio, channels in self.possible_bouquets:
            if id in used:
                # return the listing with the first channel in it
                # (they all need to be in the same list, so no problem here)
                channels = [ c for c in channels if used[id][0] in c ]
            self.current_bouquets.append([id, prio, channels])
        self.handler.append(self)


    def deactivate(self):
        self.handler.remove(self)

        
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
    # device information
    # ****************************************************************************


    def devices_info(self):
        """
        Get device information from the remote entiry.
        """
        self.entity.call('devices.list', self.devices_list_cb)

        
    def devices_list_cb(self, result):
        """
        RPC return for device.list()
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.deactivate()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return
        for device in result.arguments:
            self.entity.call('device.describe', self.devices_describe_cb, device)


    def devices_describe_cb(self, result):
        """
        RPC return for device.describe()
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.deactivate()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return

        self.possible_bouquets.append(result.arguments)
        self.current_bouquets.append(result.arguments)
        # let the server recheck it's recorder, this one is updated
        log.info('%s: activate recorder' % self.name)
        self.activate()


    def get_channel_list(self):
        """
        Return channel list to recordserver.
        """
        return self.current_bouquets


    # ****************************************************************************
    # add or remove a recording
    # ****************************************************************************


    def record(self, recording, device, start, stop):
        """
        Add a recording.
        """
        self.recordings.append(RemoteRecording(recording, device, start))

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
                # remove it from the list, the app still doesn't
                # know about this
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
                self.entity.call('vdr.record', self.start_recording_cb, remote.device,
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
            self.deactivate()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
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
            self.deactivate()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return
        # check more recordings
        self.check_recordings()


    # ****************************************************************************
    # live tv handling
    # ****************************************************************************


    def start_livetv(self, device, channel, url):
        log.info('start live tv')

        self.entity.call('vdr.record', self.start_livetv_cb, device,
                         channel, 0, 2147483647, url, ())
        id = Recorder.next_livetv_id
        Recorder.next_livetv_id = id + 1
        self.livetv[id] = LiveTV(device, channel)
        self.activate()
        return id

    
    def start_livetv_cb(self, result):
        """
        Callback for vdr.record for live tv
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.deactivate()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return
        log.info('return for live tv start')
        for key, value in self.livetv.items():
            self.livetv[key].id = result.arguments
            break
        else:
            log.error('key not found')


    def stop_livetv(self, id):
        log.info('stop live tv')
        if not id in self.livetv:
            # FIXME: handle error
            log.error('id not in list')
            return
        info = self.livetv[id]
        del self.livetv[id]
        if info.id != None:
            self.entity.call('vdr.remove', self.stop_livetv_cb, info.id)
        else:
            log.error('remote id is None')
        self.activate()

            
    def stop_livetv_cb(self, result):
        """
        Callback for vdr.remove for live tv
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.deactivate()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return
        log.info('return for live tv stop')
        return
    

recorder = RecorderList()
