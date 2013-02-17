# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# resume.py - Plugin to handle resume playback
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2012 Dirk Meyer, et al.
#
# First Edition: Aubin Paul <aubin@outlyer.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import sys
import logging

# kaa.imports
import kaa.beacon

# freevo imports
from ... import core as freevo

# the logging object
log = logging.getLogger()

# variable to store the auto resume
RESUME = 'autobookmark_resume'

kaa.beacon.register_file_type_attrs('video',
    autobookmark_resume = (int, kaa.beacon.ATTR_SIMPLE))
kaa.beacon.register_file_type_attrs('file',
    autobookmark_resume = (int, kaa.beacon.ATTR_SIMPLE))


class PluginInterface(freevo.ItemPlugin):
    """
    class to handle auto bookmarks
    """

    plugin_media = 'video'

    def __init__(self):
        super(PluginInterface, self).__init__()
        self._ignore_end = False
        self._seek = 0

    def actions_menu(self, item):
        """
        Return additional actions for the item.
        """
        if item[RESUME]:
            return [ freevo.Action(_('Resume playback'), self.resume) ]
        return []

    def resume(self, item):
        """
        Resume playback
        """
        self._seek = max(0, item[RESUME] - 10)
        item.menustack.back_submenu()
        item.play()

    def eventhandler(self, item, event):
        """
        Handle video events.
        """
        # auto bookmark store
        if event == freevo.STOP:
            if item.url.startswith('file://') and item.elapsed_secs:
                # this will store in kaa.beacon
                log.info('auto-bookmark store')
                item[RESUME]= item.elapsed_secs
                self._ignore_end = True
            else:
                log.info('auto-bookmark not supported for this item')
            return False
        # seek to the given position
        if event == freevo.PLAY_START and self._seek and event.arg == item:
            # FIXME: the event shows the OSD. Find a way to manipulate
            # the player directly
            freevo.Event(freevo.SEEK, self._seek).post()
            self._seek = 0
            return False
        # auto bookmark delete
        if event == freevo.PLAY_END and event.arg == item:
            if self._ignore_end:
                self._ignore_end = False
            else:
                item[RESUME] = None
            return False
        return False
