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
# $Log$
# Revision 1.29  2005/08/07 13:56:59  dischi
# use Signal inside a gui button and add connect to the box
#
# Revision 1.28  2005/08/07 10:46:40  dischi
# adjust to new menu interface
#
# Revision 1.27  2005/06/18 11:53:52  dischi
# adjust to new menu code
#
# Revision 1.26  2005/06/04 17:18:15  dischi
# adjust to gui changes
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------- */


import time

# freevo core imports
import freevo.ipc.tvserver as tvserver

import config
import plugin

from mainmenu import MainMenuItem
from menu import Item, ActionItem, Menu

import tvguide
from directory import DirItem
from gui.windows import MessageBox

import logging
log = logging.getLogger('tv')

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
                             display_type='tv'))

        # XXX: these are becomming plugins
        # items.append(menu.MenuItem(_('Search Guide'),
        # action=self.show_search))

        plugins_list = plugin.get('mainmenu_tv')
        for p in plugins_list:
            items += p.items(self)

        m = Menu(_('TV Main Menu'), items, item_types = 'tv main menu')
        m.infoitem = Info()
        self.pushmenu(m)


    def start_tvguide(self):

        # FIXME: debug, remove me
        t1 = time.time()

        # Should we check the validity of the guide here or remove this?
        if False:
            msg  = _('The list of TV channels is invalid!\n')
            msg += _('Please check the config file.')
            MessageBox(msg).show()
            return

        guide = plugin.getbyname('tvguide')
        if not guide:
            guide = tvguide.get_singleton()

        if guide.start(self):
            self.pushmenu(guide)

        # FIXME: debug, remove me
        t2 = time.time()
        log.info('complete tv menu update: %s' % (t2-t1))
