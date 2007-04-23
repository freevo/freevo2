# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - Base class for input plugins
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'InputPlugin' ]


# python imports
import copy
import logging

# freevo imports
from freevo import plugin
from freevo.ui import config
from freevo.ui.input import EVENTMAP
from freevo.ui.event import Event
from freevo.ui.application import get_eventmap

# get logging object
log = logging.getLogger('input')

class InputPlugin(plugin.Plugin):
    """
    Plugin for input devices such as keyboard and lirc. A plugin of this
    type should be in input/plugins
    """

    def plugin_activate(self, level):
        """
        Create eventmap on activate. FIXME: changing the setting during
        runtime has no effect.
        """
        self.eventmap = copy.deepcopy(EVENTMAP)
        for app, mapping in config.input.eventmap.items():
            for key, command in mapping.items():
                self.eventmap[app][key] = Event(*command.split(' '))

        
    def post_key(self, key):
        """
        Send a keyboard event to the event queue
        """
        if not key:
            return None

        for c in (get_eventmap(), 'global'):
            if not self.eventmap.has_key(c):
                continue
            if not self.eventmap[c].has_key(key):
                continue

            return self.eventmap[c][key].post(event_source='user')

        log.warning('no event mapping for key %s in %s' % (key, get_eventmap()))
