# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin.py - Plugin interface
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines some special plugins known to Freevo. It also contains
# all functions defined in the plugin_loader.
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

# kaa imports
import kaa.notifier

# freevo imports
import config

# plugin loader
from plugin_loader import *
import plugin_loader


#
# Some basic plugins known to Freevo.
#

class Plugin(plugin_loader.Plugin):
    """
    Basic plugin class.
    """
    def __init__(self, name=''):
        """
        Execute on activation of the plugin.
        """
        for var, val, desc in self.config():
            if not hasattr(config, var):
                setattr(config, var, val)
        plugin_loader.Plugin.__init__(self, name)


    def config(self):
        """
        return a list of config variables this plugin needs to be set in
        in freevo_config.py. Each variable in again a list and contains
        (varname, default value, description)
        """
        return []


    def shutdown(self):
        """
        Execute on plugin shutdown (== system shutdown)
        """
        pass


    def plugin_activate(self):
        """
        Execute on activation of the plugin.
        """
        # register shutdown handler
        if self.__class__.shutdown != Plugin.shutdown:
            # plugin has a self defined shutdown function
            kaa.notifier.signals['shutdown'].connect( self.shutdown )



class MainMenuPlugin(Plugin):
    """
    Plugin class for plugins to add something to the main menu
    """
    def __init__(self, name=''):
        Plugin.__init__(self, name)
        self._plugin_type = 'mainmenu'
        self._plugin_special = True


    def items(self, parent):
        """
        return the list of items for the main menu
        """
        return []



class ItemPlugin(Plugin):
    """
    Plugin class to add something to the item action list

    The plugin can also have an eventhandler. All events passed to the item
    will also be passed to this plugin. This works only for VideoItems right
    now (each item type must support it directly). If the function returns
    True, the event won't be passed to other eventhandlers and also not to
    the item itself.
    """
    def __init__(self, name=''):
        Plugin.__init__(self, name)
        self._plugin_type = 'item'
        self._plugin_special = True


    def actions(self, item):
        """
        return a list of actions to that item. Each action is type Action
        """
        return []


    def eventhandler(self, item, event):
        """
        Additional eventhandler for this item.
        """
        return False


class MimetypePlugin(Plugin):
    """
    Plugin class for mimetypes handled in a directory/playlist.
    self.display_type is a list of display types where this mimetype
    should be displayed, [] for always.
    """
    def __init__(self, name=''):
        Plugin.__init__(self, name)
        self.display_type = []
        self._plugin_type = 'mimetype'


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return []


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        return []


    def count(self, parent, listing):
        """
        return how many items will be build on files
        """
        c = 0
        for t in self.suffix():
            c += len(listing.get(t))
        return c


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        pass


    def database(self):
        """
        returns a database object
        """
        return None


#
# Some plugin names to avoid typos
#

AUDIO_PLAYER   = 'AUDIO_PLAYER'
RADIO_PLAYER   = 'RADIO_PLAYER'
VIDEO_PLAYER   = 'VIDEO_PLAYER'
TV             = 'TV'
GAMES          = 'GAMES'

def mimetype(display_type=None):
    """
    return all MimetypePlugins for the given display_type. If display_type
    is None, return all MimetypePlugins.
    """
    if not display_type:
        return plugin_loader.get('mimetype')
    ret = []
    for p in plugin_loader.get('mimetype'):
        if not p.display_type or display_type in p.display_type:
            ret.append(p)
    return ret
