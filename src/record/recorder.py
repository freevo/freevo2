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
from util.fxdimdb import FxdImdb, makeVideo
from util.videothumb import snapshot

# list of possible plugins
plugins = []


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
        plugins.append(self)


    def create_fxd(self, rec):
        """
        Create fxd file for the recording
        """
        if not rec.url.startswith('file:'):
            return
        filename = rec.url[5:]

        fxd = FxdImdb()
        (filebase, fileext) = os.path.splitext(filename)
        fxd.setFxdFile(filebase, overwrite = True)

        video = makeVideo('file', 'f1', os.path.basename(filename))
        fxd.setVideo(video)
        if rec.episode:
            fxd.info['episode'] = fxd.str2XML(rec.episode)
            if rec.subtitle:
                fxd.info['subtitle'] = fxd.str2XML(rec.subtitle)
        elif rec.subtitle:
            fxd.info['tagline'] = fxd.str2XML(rec.subtitle)
        for i in rec.info:
            if i == 'description':
                fxd.info['plot'] = fxd.str2XML(rec.info[i])
            else:
                fxd.info[i] = fxd.str2XML(rec.info[i])

        fxd.info['runtime'] = '%s min.' % int((rec.stop - rec.start) / 60)
        fxd.info['record-start'] = str(int(time.time()))
        fxd.info['record-stop'] = str(rec.stop + rec.stop_padding)
        fxd.info['year'] = time.strftime('%m-%d %H:%M',
                                         time.localtime(rec.start))
        if rec.fxdname:
            fxd.title = rec.fxdname
        else:
            fxd.title = rec.name
        fxd.writeFxd()


    def delete_fxd(self, rec):
        """
        Delete the recording fxd file.
        """
        if not rec.url.startswith('file:'):
            return
        filename = os.path.splitext(rec.url[5:])[0] + '.fxd'
        if vfs.isfile(filename):
            vfs.unlink(filename)


    def create_thumbnail(self, rec):
        """
        Create a thumbnail for the recording
        """
        if not rec.url.startswith('file:'):
            return
        filename = rec.url[5:]
        snapshot(filename)


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


    def schedule(self, recordings):
        raise Exception('plugin has not defined schedule()')
