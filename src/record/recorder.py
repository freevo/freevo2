# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recorder.py - base class for recorder plugins
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
import plugin
import childapp

# list of possible plugins
plugins = []

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


class Plugin(plugin.Plugin):
    """
    Plugin template for a recorder plugin
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        self.type = 'recorder'
        # childapp running the external program
        self.app  = None
        # recording item
        self.item = None
        # timer for stop the child when it's all done
        self.timer = None
        # reference to the recordserver
        self.server = None
        plugins.append(self)


    def get_cmd(self, rec):
        """
        Function for the plugin to create the command running the
        external program.
        """
        raise Exception('no record command function defined')


    def create_fxd(self, rec):
        """
        Create fxd file for the recording
        TODO: write this function
        """
        pass


    def record(self, server, rec):
        """
        Record 'rec', called from the recordserver 'server'
        """
        if self.item:
            print 'plugin.record: there is something running, stopping it'
            self.stop()
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
        self.server = server
        self.item = rec
        self.app = Childapp(cmd, self)
        rec.recorder = self

        # Set auto stop for stop time + padding + 10 secs
        if self.timer:
            notifier.removeTimer(self.timer)
        timer = max(0, int(rec.stop + rec.padding + 10 - time.time()))
        print 'plugin.record: add stop timer for %s seconds' % (timer)
        self.timer = notifier.addTimer(timer * 1000, self.stop)
        # Create fxd file now, even if we don't know if it is working. It
        # will be deleted later when there is a problem
        self.create_fxd()


    def stop(self):
        """
        Stop the current running recording
        """
        if not self.item:
            return False
        print 'plugin.stop: stop recording'
        notifier.removeTimer(self.timer)
        self.app.stop()
        self.timer = None
        return False


    def stopped(self):
        """
        Callback when the recording has stopped
        """
        if self.timer:
            notifier.removeTimer(self.timer)
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
        print 'plugin.stopped: recording finished, new status'
        print self.item
        if self.server:
            self.server.save()
        self.item.recorder = None
        self.item   = None
        self.app    = None
        self.server = None
