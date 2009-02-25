# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# dpms.py - Manage DPMS settings for X displays
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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
# ----------------------------------------------------------------------- */

# python imports
import os

# kaa imports
import kaa.utils
import kaa

# freevo imports
from .. import core as freevo

# blanking modes
OFF, AUTO, USER = range(3)

class PluginInterface(freevo.Plugin):

    def plugin_activate(self, level):
        if not os.environ.get('DISPLAY') or not kaa.utils.which('xset'):
            return
        # get xset process to call
        self.xset = kaa.Process(kaa.utils.which('xset')).start
        self.counter = 0
        self._mode = OFF
        # Timer to poll and increase counter. It willbe started when the
        # menu is shown.
        self.timer = kaa.Timer(self.poll)
        # register to all events
        kaa.EventHandler(self.eventhandler).register()
        # turn on dpms on shutdown
        kaa.main.signals['shutdown'].connect(self.xset, '+dpms')
        # register to application changes
        freevo.signals['application-change'].connect(self.application_changed)
        # turn off dpms
        self.xset('-dpms s off')


    def poll(self):
        """
        Poll function called every minute to check for timeout.
        """
        self.counter += 1
        if self.counter == freevo.config.plugin.dpms.timeout:
            # timeout, force dpms and turn off the monitor
            self._mode = AUTO
            self.xset('dpms force off')
            # stop poll timer
            self.timer.stop()


    def application_changed(self, app):
        """
        Callback on application changes.
        """
        if app.name == 'menu' and self._mode == OFF:
            # menu is shown, start timer
            self.timer.start(60)
            self.counter = 0
        else:
            # something else is shown, stop timer
            self.timer.stop()


    def eventhandler(self, event):
        """
        Handle events from Freevo.
        """
        if event.source == 'user':
            # user generated event (key/button), reset timeout counter
            self.counter = 0
        if (event.source == 'user' and self._mode == AUTO) or \
               (self._mode == USER and event == freevo.DPMS_BLANK_SCREEN):
            # screen is blank right now, restore it
            self._mode = OFF
            self.xset('dpms force on s reset')
            kaa.OneShotTimer(self.xset, '-dpms s off').start(1)
            self.timer.start(60)
            return

        if event == freevo.DPMS_BLANK_SCREEN:
            # event to turn off the monitor
            self._mode = USER
            self.xset('dpms force off')
            self.timer.stop()
