# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# external.py - External plugin handling over mbus
# -----------------------------------------------------------------------------
# $Id$
#
# This file will bind external mbus modules for recording as plugins in the
# recordserver.
#
# Note: this is work in progress. The mbus commands/events may change. There
# is also one app right now supporting this and this app isn't released to
# the public yet.
#
# TODO:
# o define events for recording start/stop
# o check record command and remove the bad file-mpeg uri and maybe make
#   the chunk size an option.
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
import logging
import time

import kaa.epg
import mbus
import notifier

# record imports
import recorder
from record_types import *

# get logging object
log = logging.getLogger('record')

# internal 'unique' ids
UNKNOWN_ID  = -1
IN_PROGRESS = -2

# external recording daemon
DAEMON = {'type': 'home-theatre', 'module': 'record-daemon'}


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



class Recorder(recorder.Plugin):
    """
    External recorder plugin for one mbus entity
    """
    next_livetv_id = 1
    
    def __init__(self, entity):
        recorder.Plugin.__init__(self)
        self.entity = entity
        self.name = entity.addr['id']
        self.devices = []
        self.recordings = []
        self.check_timer = None
        self.livetv_id = {}
        # FIXME: use kaa.epg for this during runtime
        self.channels = {}
        for channel in kaa.epg.channels:
            self.channels[channel.id] = channel.access_id
        self.suffix = '.mpg'
        self.entity.call('devices.list', self.__devices_list)
        log.info('%s: add external plugin' % self.name)


    def __devices_list(self, result):
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
            self.entity.call('device.describe', self.__devices_desc, device)


    def __devices_desc(self, result):
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

        # transform external name into local channel ids
        # FIXME: this code is ugly
        listing = []
        for b in result.arguments[2]:
            bouquet = []
            for dvb_name in b:
                for channel in kaa.epg.channels:
                    if channel.access_id == dvb_name:
                        bouquet.append(channel.id)
                        break
            listing.append(bouquet)
        self.devices.append(result.arguments[:2] + [listing])
        # let the server recheck it's recorder, this one is updated
        log.info('%s: activate external plugin' % self.name)
        self.activate()


    def get_channel_list(self):
        """
        Return channel list to recordserver.
        """
        return self.devices


    def __vdr_record(self, result):
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
            # FIXME: livetv, ugly ugly hack. We need to update
            # the whole mbus stuff to make it look more like kaa
            # callbacks
            log.info('return for live tv')
            for key, value in self.livetv_id.items():
                if value == None:
                    self.livetv_id[key] = result.arguments
                    break
            else:
                log.error('key not found')
                
        # check more recordings
        self.check_recordings()


    def __vdr_remove(self, result):
        """
        Callback for vdr.remove
        """
        if 0 and isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.deactivate()
            return
        if 0 and not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return
        # check more recordings
        self.check_recordings()


    def check_recordings(self):
        """
        Check the internal list of recordings and add or remove them from
        the external application.
        """
        if self.check_timer:
            notifier.removeTimer(self.check_timer)
        for remote in copy.copy(self.recordings):
            if remote.id == IN_PROGRESS:
                # already checking
                break
            if remote.id == UNKNOWN_ID and not remote.valid:
                # remove it from the list, the external app still doesn't
                # know about this
                self.recordings.remove(remote.recording)
                continue
            if remote.id == UNKNOWN_ID:
                # add the recording
                rec      = remote.recording
                channel  = self.channels[rec.channel]
                filename = self.get_url(rec)
                rec.url  = filename
                log.info('%s: schedule %s' % (self.name, String(rec.name)))
                self.entity.call('vdr.record', self.__vdr_record,
                                 remote.device, channel,
                                 remote.start, rec.stop + rec.stop_padding,
                                 filename, ())
                remote.id = IN_PROGRESS
                break
            if not remote.valid:
                # remove the recording
                log.info('%s: remove %s' % (self.name, String(remote.recording.name)))
                try:
                    self.entity.call('vdr.remove', self.__vdr_remove,
                                     remote.id)
                except:
                    pass
                self.recordings.remove(remote)
                break
        # return False, the function will be rescheduled by mbus return
        return False
    

    def record(self, recording, device, start, stop):
        """
        Add a recording to this plugin
        """
        self.recordings.append(RemoteRecording(recording, device, start))

        # update recordings at the remote application
        if self.check_timer:
            notifier.removeTimer(self.check_timer)
        self.check_timer = notifier.addTimer(100, self.check_recordings)


    def remove(self, recording):
        """
        Remove a recording
        """
        for remote in self.recordings:
            if remote.recording == recording:
                remote.valid = False
                
        # update recordings at the remote application
        if self.check_timer:
            notifier.removeTimer(self.check_timer)
        self.check_timer = notifier.addTimer(100, self.check_recordings)


    def start_livetv(self, device, channel, url):
        log.info('start live tv')
        self.entity.call('vdr.record', self.__vdr_record,
                         device, self.channels[channel], 0, 2147483647, url, ())
        id = Recorder.next_livetv_id
        Recorder.next_livetv_id = id + 1
        self.livetv_id[id] = None
        return id

    
    def stop_livetv(self, id):
        log.info('stop live tv')
        if not id in self.livetv_id:
            # FIXME: handle error
            return
        extid = self.livetv_id[id]
        del self.livetv_id[id]
        if extid != None:
            # running
            self.entity.call('vdr.remove', self.__vdr_remove, extid)


def entity_update(entity):
    """
    Update external recorders on entity changes.
    """
    if not entity.matches(DAEMON):
        # no external recorder
        return

    if entity.present:
        rec = Recorder(entity)
        return

    for r in recorder.recorder:
        if isinstance(r, Recorder) and r.entity == entity:
            log.info('lost external recorder')
            r.deactivate()
            return


def _find_recording(event):
    addr = event.header.srcAdr
    args = event.payload[0].args
    for r in recorder.recorder:
        if isinstance(r, Recorder) and r.entity.addr == addr:
            break
    else:
        log.error('unable to recorder for event')
        return None, None

    for rec in r.recordings:
        if rec.id == args[0]:
            break
    else:
        log.error('unable to recording for event')
        return None, r.server
    return rec.recording, r.server
    

def start_event(event):
    rec, server = _find_recording(event)
    server.start_recording(rec)
    return True

def stop_event(event):
    rec, server = _find_recording(event)
    server.stop_recording(rec)
    return True
