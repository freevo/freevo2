# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# tv.py - This is the Freevo TV module.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
# Please see the file doc/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */


import time
import kaa.notifier

# freevo core imports
import freevo.ipc

from freevo.ui import config
from freevo.ui import plugin

from freevo.ui.mainmenu import MainMenuItem
from freevo.ui.menu import Item, ActionItem, Menu

import tvguide
from directory import DirItem
from freevo.ui.application import TextWindow, MessageWindow

import logging
log = logging.getLogger('tv')

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

class Info(Item):
    def __getitem__(self, key):
        if key in ('comingup', 'running'):
            return getattr(tvserver.recordings, key)
        if key == 'recordserver':
            return tvserver.recordings.server
        return Info.__getitem__(self, key)


class TVMenu(MainMenuItem):
    """
    The tv main menu
    It shows the TV guide, the directory for recorded shows and all
    mainmenu_tv plugins.
    """
    def __init__(self, parent):
        MainMenuItem.__init__(self, '', self.main_menu, parent=parent,
                              skin_type = 'tv')


    def main_menu(self):
        items = []
        if True:
            # FIXME: change the tvguide into a plugin
            items.append(ActionItem(_('TV Guide'), self, self.start_tvguide))

        items.append(DirItem(config.TV_RECORD_DIR, None,
                             name = _('Recorded Shows'),
                             type='tv'))

        # XXX: these are becomming plugins
        # items.append(menu.MenuItem(_('Search Guide'),
        # action=self.show_search))

        plugins_list = plugin.get('mainmenu_tv')
        for p in plugins_list:
            items += p.items(self)

        m = Menu(_('TV Main Menu'), items, type = 'tv main menu')
        m.infoitem = Info()
        self.pushmenu(m)


    def start_tvguide(self):

        # FIXME: debug, remove me
        t1 = time.time()

        # Should we check the validity of the guide here or remove this?
        if False:
            msg  = _('The list of TV channels is invalid!\n')
            msg += _('Please check the config file.')
            MessageWindow(msg).show()
            return

        guide = tvguide.TVGuide(self)
        self.pushmenu(guide)

        # FIXME: debug, remove me
        t2 = time.time()
        log.info('complete tv menu update: %s' % (t2-t1))
