# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tvguide.py - The the Freevo TV Guide
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
#
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
import os
import sys
import time
import logging

import kaa.epg
import kaa.notifier

# freevo core imports
import freevo.ipc

# freevo imports
from freevo.ui.event import *
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.menu import Menu, ActionItem
from freevo.ui.tv.program import ProgramItem
from freevo.ui.application import MessageWindow

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

# get logging object
log = logging.getLogger('tv')

class PluginInterface(MainMenuPlugin):

    def items(self, parent):
        return [ ActionItem(_('TV Guide'), parent, self.show) ]

    def show(self, parent):
        if not tvserver.epg.connected():
            MessageWindow(_('TVServer not running')).show()
            return
        guide = TVGuide(self)
        parent.pushmenu(guide)

    
class TVGuide(Menu):
    """
    TVGuide menu.
    """
    def __init__(self, parent):
        Menu.__init__(self, _('TV Guide'), choices=[], type = 'tvgrid')
        self.parent = parent
        self.channel_index = 0
        self.current_time = int(time.time())
        
        # current channel is the first one
        self.channels = kaa.epg.get_channels(sort=True)
        self.channel  = self.get_channel()

        # current program is the current running
        self.selected = None
        self.get_program()


    def get_channel(self, offset=0):
        co = self.channel_index + offset

        if co < 0:
            co = len(self.channels)+co
        elif co > len(self.channels)-1:
            co = co-len(self.channels)
        self.channel_index = co
        return self.channels[co]


    @kaa.notifier.yield_execution()
    def get_program(self, timestamp=None):
        """
        return a program object based on timestamp and the current channel.
        """
        # TODO: keep a cache of program objects for the current guide view
        #       unless this happens to be fast enough

        if not timestamp:
            timestamp = self.current_time

        log.info('channel: %s time %s', self.channel, timestamp)
        wait = kaa.notifier.YieldCallback()
        kaa.epg.search(channel=self.channel, time=timestamp, callback=wait)
        yield wait
        prg = wait.get()

        if prg:
            # one program found, return it
            prg = prg[0]
        else:
            # Now we are in trouble, there is no program item. We need to create a fake
            # one between the last stop and the next start time. This is very slow!!!
            wait = kaa.notifier.YieldCallback()
            kaa.epg.search(channel=self.channel, time=(0, timestamp), callback=wait)
            yield wait
            p = wait.get()
            p.sort(lambda x,y: cmp(x.start, y.start))
            if p:
                start = p[-1].stop
            else:
                start = 0

            wait = kaa.notifier.YieldCallback()
            kaa.epg.search(channel=self.channel, time=(timestamp, sys.maxint),
                           callback=wait)
            yield wait
            p = wait.get()
            p.sort(lambda x,y: cmp(x.start, y.start))
            if p:
                stop = p[0].start
            else:
                stop = sys.maxint

            dbdata = { 'start': start, 'stop': stop, 'title': _('No Program') }
            prg = kaa.epg.Program(self.channel, dbdata)

        self.selected = ProgramItem(prg, self.parent)
        if self.selected.start > 0:
            self.current_time = self.selected.start + 1
        if self.selected.stop < sys.maxint:
            self.current_time = self.selected.start + 1
        if self.stack:
            # FIXME: gui calls notifier.step()
            kaa.notifier.OneShotTimer(self.stack.refresh).start(0)
        

    def eventhandler(self, event):
        if not self.selected:
            # not ready yet
            return False

        if event == MENU_CHANGE_STYLE:
            return True

        if event == MENU_UP:
            self.channel  = self.get_channel(-1)
            self.get_program()
            return True

        if event == MENU_DOWN:
            self.channel  = self.get_channel(1)
            self.get_program()
            return True

        if event == MENU_LEFT:
            if self.selected.start == 0:
                return True
            self.get_program(self.selected.program.start - 1)
            return True

        if event == MENU_RIGHT:
            if self.selected.stop == sys.maxint:
                return True
            self.get_program(self.selected.program.stop + 1)
            return True

        if event == MENU_PAGEUP:
            # FIXME: 9 is only a bad guess by Rob
            self.channel = self.get_channel(-9)
            self.get_program()
            return True

        if event == MENU_PAGEDOWN:
            # FIXME: 9 is only a bad guess by Rob
            self.channel = self.get_channel(9)
            self.get_program()
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

        return False
