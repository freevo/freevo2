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
import os
import time
import string

# freevo imports
import config
import plugin

class RecorderList:
    def __init__(self):
        self.recorder = []
        self.best_recorder = {}
        self.server = None


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
        
        
class Plugin(plugin.Plugin):
    """
    Plugin template for a recorder plugin
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        self.type = 'recorder'
        # reference to the recordserver
        self.server = None
        self.suffix = 'suffix'


    def activate(self):
        recorder.append(self)


    def deactivate(self):
        recorder.remove(self)

        
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
            filename = filename.rstrip(' -_:') + self.suffix
            filename = 'file:' + os.path.join(config.TV_RECORD_DIR, filename)
        else:
            # check filename
            if rec.url.startswith('file:'):
                filename = os.path.join(config.TV_RECORD_DIR, rec.url[5:])
                if filename.endswith('.suffix'):
                    filename = os.path.splitext(filename)[0] + self.suffix
                filename = 'file:' + filename
        if filename.startswith('file:'):
            # check if target dir exists
            d = os.path.dirname(filename[5:])
            if not os.path.isdir(d):
                os.makedirs(d)
        return filename


    def get_channel_list(self):
        raise Exception('plugin has not defined get_channel_list()')


    def record(self, recording, device):
        raise Exception('plugin has not defined record()')


    def remove(self, recording):
        raise Exception('plugin has not defined remove()')


recorder = RecorderList()
