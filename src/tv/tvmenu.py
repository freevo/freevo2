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
# Revision 1.25  2005/01/09 16:42:36  dischi
# add some debug for find a timing problem
#
# Revision 1.24  2005/01/07 20:41:03  dischi
# fix coming up and other parts of the tv menu
#
# Revision 1.23  2005/01/06 18:49:04  dischi
# remove old tv_util
#
# Revision 1.22  2004/12/04 01:23:55  rshortt
# Update comment.
#
# Revision 1.21  2004/10/18 01:17:32  rshortt
# Changes to allow people to have unset TV_CHANNELS since we're heading
# towards autodetecting everything we can.
#
# Revision 1.20  2004/08/05 17:27:16  dischi
# Major (unfinished) tv update:
# o the epg is now taken from pyepg in lib
# o all player should inherit from player.py
# o VideoGroups are replaced by channels.py
# o the recordserver plugins are in an extra dir
#
# Bugs:
# o The listing area in the tv guide is blank right now, some code
#   needs to be moved to gui but it's not done yet.
# o The only player working right now is xine with dvb
# o channels.py needs much work to support something else than dvb
# o recording looks broken, too
#
# Revision 1.19  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.18  2004/07/22 21:21:49  dischi
# small fixes to fit the new gui code
#
# Revision 1.17  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.16  2004/02/24 19:34:19  dischi
# make it possible to start a plugin guide
#
# Revision 1.15  2004/02/24 04:40:23  rshortt
# Make 'View Favorites' a menu based plugin, still incomplete.
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

import config
import menu
import plugin

from item import Item

import tvguide
from record.client import recordings
from directory import DirItem
from gui import AlertBox

import logging
log = logging.getLogger('tv')

class Info(Item):
    def __getitem__(self, key):
        if key in ('comingup', 'running'):
            return getattr(recordings, key)
        if key == 'recordserver':
            return recordings.server
        return Info.__getitem__(self, key)


class TVMenu(Item):
    """
    The tv main menu
    It shows the TV guide, the directory for recorded shows and all
    mainmenu_tv plugins.
    """
    def __init__(self):
        Item.__init__(self)
        self.type = 'tv'


    def main_menu(self, arg, menuw):
        items = []
        if True:
            # FIXME: change the tvguide into a plugin
            items.append(menu.MenuItem(_('TV Guide'), action=self.start_tvguide))

        items.append(DirItem(config.TV_RECORD_DIR, None, name = _('Recorded Shows'),
                             display_type='tv'))

        # XXX: these are becomming plugins
        # items.append(menu.MenuItem(_('Search Guide'), action=self.show_search))

        plugins_list = plugin.get('mainmenu_tv')
        for p in plugins_list:
            items += p.items(self)

        m = menu.Menu(_('TV Main Menu'), items, item_types = 'tv main menu')
        m.infoitem = Info()
        menuw.pushmenu(m)
        

    def start_tvguide(self, arg, menuw):

        # FIXME: debug, remove me
        t1 = time.time()

        # Should we check the validity of the guide here or remove this?
        if False:
            msg  = _('The list of TV channels is invalid!\n')
            msg += _('Please check the config file.')
            AlertBox(text=msg).show()
            return

        guide = plugin.getbyname('tvguide')
        if not guide:
            guide = tvguide.get_singleton()
            
        if guide.start(self):
            menuw.pushmenu(guide)
            menuw.refresh()
        
        # FIXME: debug, remove me
        t2 = time.time()
        log.info('complete tv menu update: %s' % (t2-t1))
        
