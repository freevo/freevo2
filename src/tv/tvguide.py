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

# pyepg
import pyepg

# freevo imports
import gui

from event import *
from application import MenuApplication
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
    MenuApplication. When inside the menuw, there is also a variable
    self.menuw.
    """
    def __init__(self):
        MenuApplication.__init__(self, 'tvguide', 'tvmenu', False)


    def start(self, parent):
        self.engine = gui.AreaHandler('tv', ('screen', 'title', 'subtitle',
                                             'view', 'tvlisting', 'info'))
        self.parent = parent
        self.current_time = int(time.time())

        # current channel is the first one
        self.channel  = pyepg.channels[0]

        # current program is the current running
        self.selected = ProgramItem(self.channel.get(self.current_time))

        return True
    
        
    def show(self):
        """
        show the guide
        """
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
            self.channel = pyepg.guide.get_channel(-1, self.channel)
            self.selected = ProgramItem(self.channel.get(self.current_time))
            self.refresh()
            return True

        if event == MENU_DOWN:
            self.channel = pyepg.guide.get_channel(1, self.channel)
            self.selected = ProgramItem(self.channel.get(self.current_time))
            self.refresh()
            return True

        if event == MENU_LEFT:
            epg_prog = self.channel.get_relative(-1, self.selected.program)
            self.selected = ProgramItem(epg_prog)
            if self.selected.start:
                self.current_time = self.selected.start + 1
            else:
                self.current_time -= 60 * 30
            self.refresh()
            return True

        if event == MENU_RIGHT:
            epg_prog = self.channel.get_relative(1, self.selected.program)
            self.selected = ProgramItem(epg_prog)
            if self.selected.start:
                self.current_time = self.selected.start + 1
            else:
                self.current_time -= 60 * 30
            self.refresh()
            return True

        if event == MENU_PAGEUP:
            return True

        if event == MENU_PAGEDOWN:
            return True

        if event == TV_SHOW_CHANNEL:
            self.selected.channel_details(menuw=self.menuw)
            return True
        
        if event == MENU_SUBMENU:
            self.selected.submenu(menuw=self.menuw, additional_items=True)
            return True
            
        if event == TV_START_RECORDING:
            self.selected.submenu(menuw=self.menuw, additional_items=True)
            return True
 
        if event == PLAY:
            self.selected.watch_channel(menuw=self.menuw)
            return True

        if event == MENU_SELECT or event == PLAY:
            # Check if the selected program is >7 min in the future
            # if so, bring up the submenu
            now = time.time() + (7*60)
            if self.selected.start > now:
                self.selected.submenu(menuw=self.menuw, additional_items=True)
            else:
                self.selected.watch_channel(menuw=self.menuw)
            return True
        
        if event == PLAY_END:
            self.show()
            return True

        return False


    def refresh(self):
        self.engine.draw(self)


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('tvguide')
