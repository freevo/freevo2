# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# generic.py - plugin for recording one program with a specific command
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

# notifier
import notifier

# freevo imports
import config
import childapp

# record imports
from record.recorder import Plugin


class Childapp(childapp.Instance):
    """
    ChildApp wrapper for use inside a recorder plugin
    """
    def __init__(self, app, control, debugname = None, doeslogging = 0,
                 prio = 0):
        """
        Init the childapp
        """
        childapp.Instance.__init__(self, app, debugname, doeslogging, prio, 0)
        self.control = control


    def finished(self):
        """
        Callback when the child died
        """
        self.control.stopped()
        self.control = None



class PluginInterface(Plugin):
    """
    Generic plugin. This plugin is sometimes too generic, so other plugins
    like dvb inherit from it. This plugin can only handle recording one
    item at a time using one specific application to do so.
    """
    def __init__(self):
        Plugin.__init__(self)
        # set a nice name for debug
        if not hasattr(self, 'name'):
            self.name = 'generic'
        print 'plugin: activating %s record' % self.name
        # childapp running the external program
        self.app  = None
        # recording item
        self.item = None
        # timer for stop the child when it's all done
        self.stop_timer = None
        # the recordings scheduled by the plugin
        self.recordings = []
        # timer for next recording
        self.rec_timer = None


    def get_cmd(self, rec):
        """
        Build the command to record. A class which inherits from the plugin
        should override this function.
        """
        # FIXME
        frequency = 0 

        # FIXME:
        tunerid = rec.channel
        for c in config.TV_CHANNELS:
            if tunerid == c[0] or tunerid == c[1]:
                tunerid = c[2]
                break
            
        duration = rec.stop - rec.start
        if rec.url.startswith('file:'):
            filename = rec.url[5:]
            basename = os.path.basename(filename)
        else:
            filename = rec.url
            basename = ''
        cl_options = { 'channel'       : tunerid,
                       'frequency'     : frequency,
                       'filename'      : filename,
                       'url'           : filename,
                       'base_filename' : basename,
                       'title'         : rec.name,
                       'subtitle'      : rec.subtitle,
                       'seconds'       : duration }

        return config.VCR_CMD % cl_options


    def get_channel_list(self):
        raise Exception('generic: get_channel_list() missing')
    

    def schedule(self, recordings, server=None):
        """
        Function called from the server. This function updates the
        recordings scheduled by the plugin.
        """
        if self.item and not self.item in recordings:
            self.stop()
        self.recordings = recordings
        if server:
            self.server = server

        if self.rec_timer:
            notifier.removeTimer(self.rec_timer)
            self.rec_timer = None

        if not self.recordings:
            print '%s.schedule: nothing scheduled' % self.name
            return
        
        # sort by start time
        recordings.sort(lambda l, o: cmp(l.start,o.start))
        if recordings[0].status == 'recording':
            # the first one is running right now, so the timer
            # should be set to the next one
            if len(self.recordings) == 1:
                print '%s.schedule: scheduled already recording' % self.name
                return
            rec0 = recordings[0]
            rec1 = recordings[1]
            # get end time of current recording incl. padding
            end = rec0.stop + rec0.stop_padding
            if end < rec1.start - rec1.start_padding:
                # both recordings don't overlap at the start time
                start = rec1.start - rec1.start_padding
            else:
                # recordings overlap in the padding
                # start new recording with mimimum padding possible
                start = min(end, rec1.start)
        else:
            rec   = recordings[0]
            start = rec.start - rec.start_padding
            
        secs = max(0, int(start - time.time()))
        print '%s.schedule: next in %s sec' % (self.name, secs)
        
        self.rec_timer = notifier.addTimer(secs * 1000, self.record)



    def record(self):
        """
        Record the next item in the recordings list. If the first is
        currently recording, stop the recording and record the next.
        """
        # remove the timer, just to be sure
        notifier.removeTimer(self.rec_timer)
        self.rec_timer = None

        if self.item:
            print '%s.record: there is something running, stopping it' % \
                  self.name
            self.stop()
            # return here, this function gets called by notifier using the
            # new rec_timer at once because stop() called schedule again.
            return False

        rec = self.recordings[0]
        rec.status = 'recording'
            
        # create a filename if it is missing
        if not rec.url:
            filename_array = { 'progname': String(rec.name),
                               'title'   : String(rec.subtitle) }

            filemask = config.TV_RECORDFILE_MASK % filename_array
            filename = ''
            for letter in time.strftime(filemask, time.localtime(rec.start)):
                if letter in string.ascii_letters + string.digits:
                    filename += letter
                elif filename and filename[-1] != '_':
                    filename += '_'
            filename = filename.rstrip(' -_:') + config.TV_RECORDFILE_SUFFIX
            rec.url = 'file:' + os.path.join(config.TV_RECORD_DIR, filename)

        # get the cmd for the childapp
        cmd = self.get_cmd(rec)
        self.item = rec
        self.app = Childapp(cmd, self)
        rec.recorder = self

        # Set auto stop for stop time + padding + 10 secs
        if self.stop_timer:
            notifier.removeTimer(self.stop_timer)
        timer = max(0, int(rec.stop + rec.stop_padding + 10 - time.time()))
        print '%s.record: add stop timer for %s seconds' % (self.name, timer)
        self.stop_timer = notifier.addTimer(timer * 1000, self.stop)

        # Create fxd file now, even if we don't know if it is working. It
        # will be deleted later when there is a problem
        self.create_fxd(rec)

        # schedule next recording
        self.schedule(self.recordings)

        return False
    

    def stop(self):
        """
        Stop the current running recording
        """
        if not self.item:
            # nothing to stop here
            return False
        print '%s.stop: stop recording' % self.name
        # remove the stop timer, we don't need it anymore
        notifier.removeTimer(self.stop_timer)
        self.stop_timer = None
        # stop the application
        self.app.stop()
        return False


    def stopped(self):
        """
        Callback when the recording has stopped
        """
        if self.stop_timer:
            notifier.removeTimer(self.stop_timer)
        if self.item.url.startswith('file:'):
            filename = self.item.url[5:]
            if os.path.isfile(filename):
                self.item.status = 'saved'
                # TODO: create thumbnail
            else:
                self.item.status = 'failed'
                # TODO: delete fxd
        else:
            self.item.status = 'done'
        print '%s.stopped: recording finished, new status' % self.name
        print self.item
        self.server.save()
        self.item.recorder = None
        self.item = None
        self.app = None
        # reset our timer by calling schedule again with the shorter list
        self.schedule(self.recordings[1:])
