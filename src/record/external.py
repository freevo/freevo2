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

import pyepg
import mbus

# record imports
from record.recorder import Plugin
from record.types import *

# get logging object
log = logging.getLogger('record')

# internal 'unique' ids
UNKNOWN_ID  = -1
IN_PROGRESS = -2


class Recording:
    """
    Wrapper for recordings to add 'id' and 'valid' for internal use inside
    the recorder.
    """
    def __init__(self, rec):
        self.rec = rec
        self.id = UNKNOWN_ID
        self.valid = True


    def __eq__(self, obj):
        """
        Compare two Recordings
        """
        if hasattr(obj, 'rec'):
            obj = obj.rec
        return self.rec == obj



class Recorder(Plugin):
    """
    External recorder plugin for one mbus entity
    """
    def __init__(self, entity):
        Plugin.__init__(self)
        self.entity  = entity
        self.devices = []
        self.recordings = []
        self.channels = {}
        self.suffix = '.mpg'
        self.entity.call('devices.list', self.__devices_list)


    def __devices_list(self, result):
        """
        RPC return for device.list()
        """
        if result.appResult != 'OK' or not result.appStatus:
            log.error(str(result.appDescription))
            return
        for device in result.arguments:
            self.entity.call('device.describe', self.__devices_desc, device)


    def __devices_desc(self, result):
        """
        RPC return for device.describe()
        """
        if result.appResult != 'OK' or not result.appStatus:
            log.error(str(result.appDescription))
            return

        # transform external name into local channel ids
        # FIXME: this code is ugly
        listing = []
        for b in result.arguments[2]:
            bouquet = []
            for dvb_name in b:
                for channel in pyepg.channels:
                    if channel.access_id == dvb_name:
                        bouquet.append(channel.id)
                        self.channels[channel.id] = dvb_name
                        break
            listing.append(bouquet)
        self.devices.append(result.arguments[:2] + [listing])
        # let the server recheck it's recorder, this one is updated
        self.server.check_recorder()


    def deactivate(self):
        """
        Deactivate this plugin because something went wrong.
        """
        log.warning('Plugin deactivated')
        self.channels = {}
        # let the recordserver recheck it's recorders, this one is
        # broken and everything needs to be recalculated
        self.server.check_recorder()


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
        if result.appResult != 'OK' or not result.appStatus:
            log.error(str(result.appDescription))
            self.deactivate()
            return
        if len(result.arguments) != 1:
            log.error('RPC return invalid')
            self.deactivate()
            return
        # result is an unique id
        for rec in copy.copy(self.recordings):
            if rec.id == IN_PROGRESS:
                rec.id = result.arguments[0]
        # check more recordings
        self.check_recordings()


    def __vdr_remove(self, result):
        """
        Callback for vdr.remove
        """
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.deactivate()
            return
        if result.appResult != 'OK' or not result.appStatus:
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
        for rec in copy.copy(self.recordings):
            if rec.id == IN_PROGRESS:
                # already checking
                break
            if rec.id == UNKNOWN_ID and not rec.valid:
                # remove it from the list, the external app still doesn't
                # know about this
                self.recordings.remove(rec)
                continue
            if rec.id == UNKNOWN_ID:
                # add the recording
                device   = rec.rec.recorder[1]
                channel  = self.channels[rec.rec.channel]
                filename = self.get_url(rec.rec)
                filename = filename.replace('file:/', 'file-mpeg:///')
                self.entity.call('vdr.record', self.__vdr_record, device,
                                 channel, rec.rec.start, rec.rec.stop,
                                 filename, 0, ())
                rec.id = IN_PROGRESS
                break
            if not rec.valid:
                # remove the recording
                self.entity.call('vdr.remove', self.__vdr_remove, rec.id)
                self.recordings.remove(rec)
                break


    def schedule(self, recordings, server=None):
        """
        Function called from the server. This function updates the
        recordings scheduled by the plugin.
        """
        for rec in recordings:
            if rec not in self.recordings:
                # add new recording
                self.recordings.append(Recording(rec))

        for rec in self.recordings:
            if rec.rec not in recordings:
                # set old recordings to valid = False
                rec.valid = False

        # update recordings at the remote application
        self.check_recordings()
