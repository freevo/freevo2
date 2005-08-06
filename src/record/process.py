# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# process.py - template for plugins based on starting external processes
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
import time
import os
import string
import logging

# kaa imports
from kaa.notifier import Process, OneShotTimer

# freevo imports
import config

# record imports
from record.recorder import Plugin
from record.record_types import *

# get logging object
log = logging.getLogger('record')



class Recorder(Plugin):
    """
    Generic plugin. This plugin is sometimes too generic, so other plugins
    like dvb inherit from it. This plugin can only handle recording one
    item at a time using one specific application to do so.
    """
    def __init__(self):
        # set a nice name for debug
        if not hasattr(self, 'name'):
            self.reason = 'record.generic can\'t be used directly'
            return
        Plugin.__init__(self)
        log.info('plugin: activating %s record' % self.name)
        # childapp running the external program
        self.app  = None
        # recording item
        self.current_recording = None
        # the recordings scheduled by the plugin
        self.recordings = []
        # suffix for filename
        self.suffix = '.suffix'
        # timer for scheduling
        self.schedule_timer = OneShotTimer(self.schedule)
        self.start_timer = OneShotTimer(self.start)
        self.stop_timer = OneShotTimer(self.stop)

        
    def get_cmd(self, rec):
        """
        Build the command to record. A class which inherits from the plugin
        should override this function.
        """
        raise Exception('generic: get_cmd() missing')


    def get_channel_list(self):
        raise Exception('generic: get_channel_list() missing')


    def __sort(self, r1, r2):
        """
        Sort by scheduled_start time.
        """
        return cmp(r1.scheduled_start, r2.scheduled_start)


    def record(self, recording, device, start, stop):
        self.recordings.append(recording)
        self.schedule(True)


    def remove(self, recording):
        self.recordings.remove(recording)
        if recording == self.current_recording:
            log.info('%s: remove running recording' % self.name)
            self.stop()
        self.schedule(True)


    def get_time(self, timer, msg):
        txt = time.strftime('%H:%M', time.localtime(timer))
        # minumum 5 seconds
        sec = max(5, int(timer - time.time()))
        log.info('%s: %s at %s (%s sec)' % (self.name, msg, txt, sec))
        return sec * 1000
    

    def schedule(self, later=False):
        if later:
            self.schedule_timer.start(0)
            return
        
        # sort by start time
        self.recordings.sort(self.__sort)

        if not self.recordings:
            log.info('%s.schedule: nothing scheduled' % self.name)
            return

        # get first recording in list
        rec = self.recordings[0]

        if rec.status == RECORDING:
            # The first one is running right now. The next will be
            # scheduled on stop event
            log.info('%s.schedule: already scheduled' % self.name)
            return
        else:
            # schedule first recording
            msecs = self.get_time(rec.scheduled_start, 'next recording')
            self.start_timer.start(msecs)

        # get stop timer
        msecs = self.get_time(rec.scheduled_stop, 'stop timer')
        # schedule stop timer
        self.stop_timer.start(msecs)
        return False


    def start(self):
        """
        Record the next item in the recordings list. If the first is
        currently recording, stop the recording and record the next.
        """
        # The start function can only be called when no recording is
        # currently running, so no conflicts are possible
        rec = self.recordings[0]
        rec.url = self.get_url(rec)

        # notify server about a started recording
        self.server.start_recording(rec)

        log.info('%s: start new recording:\n%s' % (self.name, str(rec)))

        # get the cmd for the childapp
        cmd = self.get_cmd(rec)
        self.app = Process(cmd)
        self.app.signals["completed"].connect(self.stopped)
        self.app.start()
        return False


    def stop(self):
        """
        Stop the current running recording
        """
        rec = self.recordings[0]
        log.info('%s.stop: stop recording' % (self.name))
        # stop the application, this will trigger a reschedule
        # and schedule the next recording
        self.app.stop()
        return False


    def stopped(self):
        """
        Callback when the recording has stopped
        """
        # maybe the app stopped without 'stop' being called, remove
        # the callback, just in case
        self.stop_timer.stop()

        # get current recording
        rec = self.recordings[0]

        # notify server about a stopped recording
        self.server.stop_recording(rec)

        log.info('%s: recording finished:\n%s' % (self.name, str(rec)))

        # remove recording from the list
        self.recordings.remove(rec)
        self.app = None

        # schedule next recording
        self.schedule(True)
