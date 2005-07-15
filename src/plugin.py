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

# kaa imports
import kaa.notifier

# freevo imports
import config
from event import Event
import eventhandler

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
    def __init__(self):
        """
        Execute on activation of the plugin.
        """
        for var, val, desc in self.config():
            if not hasattr(config, var):
                setattr(config, var, val)
        plugin_loader.Plugin.__init__(self)


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
    def __init__(self):
        Plugin.__init__(self)
        self.plugin_type = 'mainmenu'
        self.plugin_special = True


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
    def __init__(self):
        Plugin.__init__(self)
        self.plugin_type = 'item'
        self.plugin_special = True


    def actions(self, item):
        """
        return a list of actions to that item. Each actions is a tuple
        (function, 'name-in-the-menu')
        """
        return []


    def eventhandler(self, item, event, menuw=None):
        """
        Additional eventhandler for this item.
        """
        return False


class DaemonPlugin(Plugin):
    """
    Plugin class for daemon objects who will be activate in the
    background while Freevo is running
    """
    def __init__(self):
        Plugin.__init__(self)
        self.poll_interval  = 100       # poll every x milliseconds
        self.poll_menu_only = True      # poll only when menu is active
        self.events         = []        # events to register to ([] == all)


    def poll(self):
        """
        This function will be called every poll_interval milliseconds.
        """
        pass


    def __poll(self):
        """
        wrapper for the poll function
        """
        if self.poll_menu_only and not eventhandler.is_menu():
            return True
        self.poll()
        return True


    def plugin_activate(self):
        """
        Execute on activation of the plugin.
        """
        Plugin.plugin_activate(self)
        if self.__class__.poll != DaemonPlugin.poll:
            # plugin has a self defined poll function, register it
            self.__timer = kaa.notifier.Timer(self.__poll).start(self.poll_interval)

        if self.__class__.eventhandler != DaemonPlugin.eventhandler:
            # plugin has a self defined eventhandler
            kaa.notifier.EventHandler(self.eventhandler).register(self.events)


    def eventhandler(self, event):
        """
        Handle events passed to the eventhandler.
        """
        return False


class MimetypePlugin(Plugin):
    """
    Plugin class for mimetypes handled in a directory/playlist.
    self.display_type is a list of display types where this mimetype
    should be displayed, [] for always.
    """
    def __init__(self):
        Plugin.__init__(self)
        self.display_type = []
        self.plugin_type = 'mimetype'


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
        return len(listing.match_suffix(self.suffix()))


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        pass


    def dirconfig(self, diritem):
        """
        adds configure variables to the directory
        """
        return []


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
RECORD         = 'RECORD'


def event(name, arg=None):
    """
    create plugin event
    """
    return Event('PLUGIN_EVENT %s' % name, arg=arg)


def isevent(event):
    """
    plugin event parsing
    """
    event = str(event)
    if event[:12] == 'PLUGIN_EVENT':
        return event[13:]
    else:
        return None


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
