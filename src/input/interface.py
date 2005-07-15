# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - Base class for input plugins
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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
import copy
import logging

# freevo imports
import config
import plugin
import eventhandler

# get logging object
log = logging.getLogger('config')

class InputPlugin(plugin.Plugin):
    """
    Plugin for input devices such as keyboard and lirc. A plugin of this
    type should be in input/plugins
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._eventhandler = eventhandler.get_singleton()


    def post_key(self, key):
        """
        Send a keyboard event to the event queue
        """
        if not key:
            return None

        for c in (self._eventhandler.context, 'global'):
            try:
                e = copy.copy(config.EVENTS[c][key])
                e.context = self._eventhandler.context
                e.post()
                break
            except KeyError:
                pass
        else:
            log.warning('no event mapping for key %s in context %s' % \
                        (key, self._eventhandler.context))


    def post_event(self, event):
        """
        Send an event to the eventhandler.
        """
        self._eventhandler.post(event)
        
