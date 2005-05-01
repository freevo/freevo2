# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxdfile.py - Plugin to generated fxd files for recordings
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

# freevo imports
from record.plugins import Plugin
from util.fxdimdb import FxdImdb, makeVideo
from record.record_types import *

class PluginInterface(Plugin):
    """
    Plugin to generated fxd files for recordings
    """
    def start_recording(self, recording):
        """
        Create fxd file for file:// recordings when the recording starts.
        """
        if not recording.url.startswith('file:'):
            return
        filename = recording.url[5:]

        fxd = FxdImdb()
        (filebase, fileext) = os.path.splitext(filename)
        fxd.setFxdFile(filebase, overwrite = True)

        video = makeVideo('file', 'f1', os.path.basename(filename))
        fxd.setVideo(video)
        if recording.episode:
            fxd.info['episode'] = fxd.str2XML(recording.episode)
            if recording.subtitle:
                fxd.info['subtitle'] = fxd.str2XML(recording.subtitle)
        elif recording.subtitle:
            fxd.info['tagline'] = fxd.str2XML(recording.subtitle)
        if recording.description:
            fxd.info['plot'] = fxd.str2XML(recording.description)
        for i in recording.info:
            fxd.info[i] = fxd.str2XML(recording.info[i])

        fxd.info['runtime'] = '%s min.' % \
                              int((recording.stop - recording.start) / 60)
        fxd.info['record-start'] = str(int(time.time()))
        fxd.info['record-stop'] = str(recording.stop + recording.stop_padding)
        fxd.info['year'] = time.strftime('%m-%d %H:%M',
                                         time.localtime(recording.start))
        if recording.fxdname:
            fxd.title = recording.fxdname
        else:
            fxd.title = recording.name
        fxd.writeFxd()


    def stop_recording(self, recording):
        """
        Remove the fxd file on stop when something went wrong.
        """
        if recording.status == SAVED:
            return
        if not recording.url.startswith('file:'):
            return
        filename = os.path.splitext(recording.url[5:])[0] + '.fxd'
        if os.path.isfile(filename):
            # fxd file must be in real not in overlay dir, without
            # that, the recorder couldn't even store the file
            os.unlink(filename)
