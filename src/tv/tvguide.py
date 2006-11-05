# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tvguide.py - The the Freevo TV Guide
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
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
# -----------------------------------------------------------------------------


# python imports
import os
import sys
import time
import logging

import kaa.epg

# freevo core imports
import freevo.ipc

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
        self.channel_index = 0

    def get_channel(self, offset=0):
        co = self.channel_index + offset
        channels = kaa.epg.get_channels(sort=True)

        if co < 0:
            co = len(channels)+co
        elif co > len(channels)-1:
            co = co-len(channels)
        self.channel_index = co
        return channels[co]

    def get_program(self, time=None):
        """
        return a program object based on time and the current channel.
        """
        # TODO: keep a cache of program objects for the current guide view
        #       unless this happens to be fast enough

        if not time:
            time = self.current_time

        log.debug('channel: %s', self.channel)
        p = kaa.epg.search(channel=self.channel, time=time)
        if p:
            # one program found, return it
            return p[0]
        # Now we are in trouble, there is no program item. We need to create a fake
        # one between the last stop and the next start time. This is very slow!!!
        p = kaa.epg.search(channel=self.channel, time=(0, time))
        p.sort(lambda x,y: cmp(x.start, y.start))
        if p:
            start = p[-1].stop
        else:
            start = 0

        p = kaa.epg.search(channel=self.channel, time=(time, sys.maxint))
        p.sort(lambda x,y: cmp(x.start, y.start))
        if p:
            stop = p[0].start
        else:
            stop = sys.maxint

        data = { 'start': start, 'stop': stop, 'title': _('No Program') }
        return kaa.epg.Program(self.channel, data)
    

    def start(self, parent):
        self.engine = gui.areas.Handler('tv', ('screen', 'title', 'subtitle',
                                               'view', 'tvlisting', 'info'))
        self.parent = parent
        # create fake parent item for ProgramItems
        self.item = Item(parent, None, 'tv')
        
        self.current_time = int(time.time())

        # current channel is the first one
        self.channel  = self.get_channel()

        # current program is the current running
        self.selected = ProgramItem(self.get_program(), self.item)

        return True
    
        
    def show(self):
        """
        show the guide
        """
        self.selected = ProgramItem(self.get_program(), self.item)
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
            self.channel  = self.get_channel(-1)
            self.selected = ProgramItem(self.get_program(), self.item)
            self.refresh()
            return True

        if event == MENU_DOWN:
            self.channel  = self.get_channel(1)
            self.selected = ProgramItem(self.get_program(), self.item)
            self.refresh()
            return True

        if event == MENU_LEFT:
            if self.selected.start == 0:
                return True
            epg_prog = self.get_program(self.selected.program.start - 1)
            self.selected = ProgramItem(epg_prog, self.item)
            if self.selected.start > 0:
                self.current_time = self.selected.start + 1
            self.refresh()
            return True

        if event == MENU_RIGHT:
            if self.selected.stop == sys.maxint:
                return True
            epg_prog = self.get_program(self.selected.program.stop + 1)
            self.selected = ProgramItem(epg_prog, self.item)
            if self.selected.stop < sys.maxint:
                self.current_time = self.selected.start + 1
            self.refresh()
            return True

        if event == MENU_PAGEUP:
            # FIXME: 9 is only a bad guess by Rob
            self.channel = self.get_channel(-9)
            self.selected = ProgramItem(self.get_program(), self.item)
            self.refresh()
            return True

        if event == MENU_PAGEDOWN:
            # FIXME: 9 is only a bad guess by Rob
            self.channel = self.get_channel(9)
            self.selected = ProgramItem(self.get_program(), self.item)
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
