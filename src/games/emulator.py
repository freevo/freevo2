# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# emulator.py - the plugin for the emulators
# -----------------------------------------------------------------------------
# $Id$
#
# This is a generic emulator player. This should work with most emulators.
# If something special is needed it should be possible to create a specialized
# version easely. See pcgames.py for an example.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Mathias Weber <mweb@gmx.ch>
# Maintainer:    Mathias Weber <mweb@gmx.ch>
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

__all__ = [ 'EmulatorPlugin', 'EmulatorItem', 'EmulatorPlayer', 'EmulatorMenuItem' ]

# python imports
import logging
import os

# kaa imports
import kaa.notifier
from kaa.notifier import Event
from kaa.weakref import weakref
import kaa.beacon

# freevo imports
from freevo.resources import ResourceHandler
from freevo.ui import SHAREDIR
from freevo.ui.mainmenu import MainMenuItem, MainMenuPlugin
from freevo.ui.directory import DirItem
from freevo.ui.event import EJECT
from freevo.ui import plugin, application
from freevo.ui.menu import Item, Action, Menu
from freevo.ui.mediamenu import MediaMenu

# games imports
import player as gameplayer

log = logging.getLogger('games')


class EmulatorPlugin(MainMenuPlugin):
    """
    Add the emualtor items to the games menu
    """
    possible_media_types = [ 'games' ]

    def roms(self, parent, listing, configitem):
        """
        Show all roms.
        """
        items = []
        for suffix in self.suffix(configitem):
            # if is only one object don't iterate over it.
            if isinstance(listing, kaa.beacon.file.File):
                filename = listing.get('name')
                if filename.endswith(suffix):
                    # cut the fileending off the file for the displaying name
                    name = filename[:-(len(suffix)+1)]
                    items.append(EmulatorItem(parent, name, \
                            listing.filename, configitem))
                    break
        return items


    def suffix(self, configitem):
        """
        return the list of suffixes this class handles
        """
        return configitem.suffix.split(',')


    def items(self, parent):
        """
        Return the main menu item.
        """
        return []


class EmulatorItem(Item):
    """
    Basic Item for all emulator types
    """

    def __init__(self, parent, name, url="", configitem=None):
        Item.__init__(self, parent)
        self.name = name
        self.url = url
        self.configitem = configitem
        log.info('create EmulatorItem name=%s, url=%s'%(name, url))


    def play(self):
        """
        Start the emulator with the generic EmulatorPlayer.
        """
        gameplayer.play(self, EmulatorPlayer(self.configitem.bin, \
                self.configitem.parameters))


    def remove(self):
        """
        Delete Rom from the disk
        """
        #FIXME
        log.info('Remove rom %s (FIXME not implemented)'%self.name)


    def actions(self):
        """
        Default action for the itmes. There are two actions available play
        and remove. Remove is for deleting a rom.
        """
        return [ Action(_('Play %s') % self.name, self.play),
                Action(_('Remove %s') % self.name, self.remove)]


class EmulatorPlayer(ResourceHandler):
    """
    Generic game player.
    """
    def __init__(self, command_name=None, parameters=""):
        self.command_name = command_name
        self.parameters = parameters
        self.url = None
        self.child = None

        self.signals = {
            "open": kaa.notifier.Signal(),
            "start": kaa.notifier.Signal(),
            "failed": kaa.notifier.Signal(),
            "end": kaa.notifier.Signal(),
        }

    def open(self, item):
        """
        Open an item, prepare for playing. Load url parameter from
        EmulatorItem
        """
        self.url = item.url


    def play(self):
        """
        Play game. Should work with most emulators. Will start
        [command_name] [parameters] [url]
        """
        params = "%s %s" % (self.parameters, self.url)
        log.info('Start playing EmulatorItem (%s %s)' % \
                (self.command_name, params))
        self.child = kaa.notifier.Process(self.command_name)
        self.child.start(params).connect(self.completed)
        self.signals = self.child.signals
        stop = kaa.notifier.WeakCallback(self.stop)
        self.child.set_stop_command(stop)


    def is_running(self):
        """
        check if player is still running
        """
        if self.child:
            return self.child.is_alive()

        return False


    def completed(self, child):
        """
        The game was quit. Send stop event to get back to the menu.
        """
        Event(STOP, handler=gameplayer.player.eventhandler).post()
        log.info('emulator completed')


    def stop(self):
        """
        Stop the game from playing
        """
        if self.child:
            self.child.stop()



class EmulatorMenuItem(MainMenuItem):
    """
    This is a menu entry for the different emulators in the games subdirectory.
    This class has a lot of similarities with the MediaMenu, maybe there
    could be some integration with this.
    """

    def __init__(self, parent, title, items, gamepluginlist, configitem,
            image=None, root=True):
        MainMenuItem.__init__(self,parent, title, image=image)
        if root:
            kaa.beacon.signals['media.add'].connect(self.media_change)
            kaa.beacon.signals['media.remove'].connect(self.media_change)

        self.menutitle = title
        self.item_menu = None
        self.gamepluginlist = gamepluginlist
        self.configitem = configitem
        self.isRoot = root

        self._items = items

        # add listener for the different directories
        for filename in self._items:
            if hasattr(filename, 'path'):
                #replace home variable
                filename = filename.path.replace('$(HOME)', \
                        os.environ.get('HOME'))
            if isinstance(filename, kaa.beacon.file.File):
                continue
            if not isinstance(filename, (str, unicode)):
                filename = filename[1]
            filename = os.path.abspath(filename)
            if os.path.isdir(filename) and \
                    not os.environ.get('NO_CRAWLER') and \
                    not filename == os.environ.get('HOME') and \
                    not filename == '/':
                kaa.beacon.monitor(filename)


    def main_menu_generate(self):
        """
        generate the itmes for the games menu. This is needed when first
        generating the menu and if something changes by pressing the EJECT
        button for example
        """
        items = []
        for item in self._items:
            try:
                filename = ''
                title = ''
                if hasattr(item, 'path'):
                    title = unicode(item.name)
                    filename = item.path.replace('$(HOME)', \
                            os.environ.get('HOME'))
                elif isinstance(item, (str, unicode)):
                    # only a filename is given
                    title, filename = u'', item
                elif isinstance(item, kaa.beacon.file.File):
                    title = u''
                    filename = item.filename
                filename = os.path.abspath(filename)
                if os.path.isdir(filename):
                    query = kaa.beacon.query(filename=filename)
                    for d in query.get(filter='extmap').get('beacon:dir'):
                        items.append(EmulatorMenuItem(self, "[%s]"%title, \
                                d.list().get(), self.gamepluginlist, \
                                self.configitem, root=False))
                    continue

                if not os.path.isfile(filename) and \
                        filename.startswith(os.getcwd()):
                    # file is in share dir
                    filename = filename[len(os.getcwd()):]
                    if filename[0] == '/':
                        filename = filename[1:]
                    filename = os.path.join(SHAREDIR, filename)

                query = kaa.beacon.query(filename=filename)
                listing = query.get()
                g_items = self.gamepluginlist(self, listing, self.configitem)
                if g_items:
                    items += g_items
            except:
                log.exception('Error parsing %s' %str(item))
                continue
        if self.isRoot:
            for media in kaa.beacon.media:
                if media.mountpoint == '/':
                    continue
                listing = kaa.beacon.wrap(media.root, filter='extmap')
                g_items = self.gamepluginlist(self, listing, self.configitem)
                if g_items:
                    items += g_items
                for d in listing.get('beacon:dir'):
                    items.append(EmulatorMenuItem(self, "[%s]"%media.label, \
                            d.list().get(), self.gamepluginlist, \
                            self.configitem, root=False))

        return items


    def select(self):
        """
        display the emulator menu
        """
        items = self.main_menu_generate()

        type = ""
        item_menu = Menu(self.menutitle, items, type=type, \
                reload_func=self.reload)
        item_menu.autoselect = True
        item_menu.skin_force_view = False
        self.item_menu = item_menu
        self.pushmenu(item_menu)


    def reload(self):
        """
        Reload the menu items
        """
        if self.item_menu:
            self.item_menu.set_items(self.main_menu_generate())


    def media_change(self, media):
        """
        Media change from kaa.beacon
        """
        if self.item_menu:
            self.item_menu.set_items(self.main_menu_generate())


    def eventhandler(self, event):
        """
        Handle events, eject for a media item
        """
        if event == EJECT and self.item_menu and \
                self.item_menu.selected.info['parent'] == \
                self.item_menu.selected.info['media']:
            self.item_menu.selected.info['media'].eject()
