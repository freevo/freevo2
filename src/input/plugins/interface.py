# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - Base class for input plugins
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2005-2007 Dirk Meyer, et al.
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
# -----------------------------------------------------------------------------

__all__ = [ 'InputPlugin' ]


# python imports
import copy
import logging

# freevo imports
from freevo import plugin
from freevo.ui import config
from freevo.ui.input import EVENTMAP as global_map
from freevo.ui.event import Event
from freevo.ui.application import get_eventmap as current_app

# get logging object
log = logging.getLogger('input')

# get config event map
config_map = config.input.eventmap

class InputPlugin(plugin.Plugin):
    """
    Plugin for input devices such as keyboard and lirc. A plugin of this
    type should be in input/plugins
    """

    def post_key(self, key):
        """
        Send a keyboard event to the event queue
        """
        if not key:
            return None

        for app in (current_app(), 'global'):
            # check config file event mapping
            if app in config_map and key in config_map[app]:
                event = Event(*config_map[app][key].split(' '))
                return event.post(event_source='user')
            # check global pre-defined event mapping
            if app in global_map and key in global_map[app]:
                return global_map[app][key].post(event_source='user')

        log.warning('no event mapping for key %s in %s' % (key, current_app()))
