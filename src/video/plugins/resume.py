# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# resume.py - Plugin to handle resume playback
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
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
import logging
import kaa.beacon

# freevo imports
from freevo.ui.menu import Action, Menu, ItemPlugin
from freevo.ui.event import PLAY_START, PLAY_END, STOP, SEEK, Event

# the logging object
log = logging.getLogger()

# variable to store the auto resume
RESUME = 'autobookmark_resume'

kaa.beacon.register_file_type_attrs('video',
    autobookmark_resume = (int, kaa.beacon.ATTR_SIMPLE))


class PluginInterface(ItemPlugin):
    """
    class to handle auto bookmarks
    """

    def __init__(self):
        ItemPlugin.__init__(self)
        self._ignore_end = False
        self._seek = 0


    def actions(self, item):
        """
        Return additional actions for the item.
        """
        if item[RESUME]:
            return [ Action(_('Resume playback'), self.resume) ]
        return []


    def resume(self, item):
        """
        Resume playback
        """
        self._seek = max(0, item[RESUME] - 10)
        item.get_menustack().delete_submenu()
        item.play()


    def eventhandler(self, item, event):
        """
        Handle video events.
        """
        # auto bookmark store
        if event == STOP:
            if item.mode == 'file' and item.elapsed:
                # this will store in kaa.beacon
                log.info('auto-bookmark store')
                item[RESUME]= item.elapsed
                self._ignore_end = True
            else:
                log.info('auto-bookmark not supported for this item')
            return False

        # seek to the given position
        if event == PLAY_START and self._seek:
            Event(SEEK, self._seek).post()
            self._seek = 0
            return False

        # auto bookmark delete
        if event == PLAY_END:
            if self._ignore_end:
                self._ignore_end = False
            else:
                item[RESUME] = None
            return False

        return False
