# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tvguide.py - The the Freevo TV Guide
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
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
import logging

import kaa.epg

# freevo imports
import gui
import gui.areas

from event import *
from application import MenuApplication
from menu import Item
from program import ProgramItem

# get logging object
log = logging.getLogger('tv')

_guide = None


def get_singleton():
    """
    return the global tv guide
    """
    global _guide
    if not _guide:
        _guide = TVGuide()
    return _guide



class TVGuide(MenuApplication):
    """
    TVGuide application. It is _inside_ the menu, so it is a
    MenuApplication.
    """
    def __init__(self):
        MenuApplication.__init__(self, 'tvguide', 'tvmenu', False)
        self.item = None

    def start(self, parent):
        self.engine = gui.areas.Handler('tv', ('screen', 'title', 'subtitle',
                                               'view', 'tvlisting', 'info'))
        self.parent = parent
        # create fake parent item for ProgramItems
        self.item = Item(parent, None, 'tv')
        
        self.current_time = int(time.time())

        # current channel is the first one
        self.channel  = kaa.epg.channels[0]

        # current program is the current running
        self.selected = ProgramItem(self.channel[self.current_time], self.item)

        return True
    
        
    def show(self):
        """
        show the guide
        """
        self.channel = kaa.epg.get_channel()
        self.selected = ProgramItem(self.channel[self.current_time], self.item)
        self.refresh()
        MenuApplication.show(self)
        

    def hide(self):
        """
        hide the guide
        """
        MenuApplication.hide(self)
            
        
    def eventhandler(self, event):
        if MenuApplication.eventhandler(self, event):
            return True

        if event == MENU_CHANGE_STYLE:
            return True
            
        if event == MENU_UP:
            self.channel = kaa.epg.get_channel(self.channel, -1)
            self.selected = ProgramItem(self.channel[self.current_time],
                                        self.item)
            self.refresh()
            return True

        if event == MENU_DOWN:
            self.channel = kaa.epg.get_channel(self.channel, 1)
            self.selected = ProgramItem(self.channel[self.current_time],
                                        self.item)
            self.refresh()
            return True

        if event == MENU_LEFT:
            epg_prog = self.channel[self.selected.program.start - 1]
            self.selected = ProgramItem(epg_prog, self.item)
            if self.selected.start > 0:
                self.current_time = self.selected.start + 1
            self.refresh()
            return True

        if event == MENU_RIGHT:
            epg_prog = self.channel[self.selected.program.stop+1]
            self.selected = ProgramItem(epg_prog, self.item)
            if self.selected.start > 0:
                self.current_time = self.selected.start + 1
            self.refresh()
            return True

        if event == MENU_PAGEUP:
            self.channel = kaa.epg.get_channel(self.channel, -9)
            self.selected = ProgramItem(self.channel[self.current_time],
                                        self.item)
            self.refresh()
            return True

        if event == MENU_PAGEDOWN:
            self.channel = kaa.epg.get_channel(self.channel, 9)
            self.selected = ProgramItem(self.channel[self.current_time],
                                        self.item)
            self.refresh()
            return True

        if event == TV_SHOW_CHANNEL:
            self.selected.channel_details()
            return True
        
        if event == MENU_SUBMENU:
            self.selected.submenu(additional_items=True)
            return True
            
        if event == TV_START_RECORDING:
            self.selected.submenu(additional_items=True)
            return True
 
        if event == PLAY:
            self.selected.watch_channel()
            return True

        if event == MENU_SELECT or event == PLAY:
            # Check if the selected program is >7 min in the future
            # if so, bring up the submenu
            now = time.time() + (7*60)
            if self.selected.start > now:
                self.selected.submenu(additional_items=True)
            else:
                self.selected.watch_channel()
            return True
        
        if event == PLAY_END:
            self.show()
            return True

        return False


    def refresh(self):
        self.engine.draw(self)
