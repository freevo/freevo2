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

__all__ = [ 'set_mapping', 'get_mapping', 'InputPlugin' ]


# python imports
import copy
import logging

# freevo imports
import config
import plugin

# get logging object
log = logging.getLogger('input')

# set key mapping for input
_mapping = None

def set_mapping(mapping):
    """
    Set new key mapping.
    """
    global _mapping
    _mapping = mapping


def get_mapping():
    """
    Get current key mapping.
    """
    return _mapping


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

        for c in (_mapping, 'global'):
            if not config.EVENTS.has_key(c):
                continue
            if not config.EVENTS[c].has_key(key):
                continue

            return config.EVENTS[c][key].post()

        log.warning('no event mapping for key %s in %s' % (key, _mapping))
