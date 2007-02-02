# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediamenu.py - Basic menu for all kinds of media
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin can create submenus for the different kind of media plugins.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2007 Dirk Meyer, et al.
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

# python imports
import os
import copy
import logging

# kaa imports
import kaa.beacon
from kaa.weakref import weakref

# freevo imports
import freevo.conf

from freevo.ui import plugin
from freevo.ui.event import EJECT
from freevo.ui.directory import DirItem
from freevo.ui.mainmenu import MainMenuItem
from freevo.ui.menu import Menu, Item
# from games import machine

# get logging object
log = logging.getLogger()


class PluginInterface(plugin.MainMenuPlugin):
    """
    Plugin to integrate a mediamenu (video/audio/image/games) into
    the Freevo main menu. This plugin is auto-loaded when you activate
    the 'video', 'audio', 'image' or 'games' plugin.
    """
    def __init__(self, name, type, items):
        if items is None:
            self.reason = 'No items defined for %s menu' % type
            return
        plugin.MainMenuPlugin.__init__(self)
        self._name = name
        self._type = type
        self._items = items
        
    def items(self, parent):
        return [ MediaMenu(parent, self._name, self._type, self._items) ]



class MediaMenu(MainMenuItem):
    """
    This is the main menu for audio, video and images. It displays the default
    directories and the ROM_DRIVES
    """

    def __init__(self, parent, title, type, items):
        MainMenuItem.__init__(self, '', self.main_menu, type='main',
                              parent=parent, skin_type=type)
        self.force_text_view = False
        self.display_type = type
        self.item_menu = None

        kaa.beacon.signals['media.add'].connect(self.media_change)
        kaa.beacon.signals['media.remove'].connect(self.media_change)

        self.menutitle = title

        self._items = items
        for filename in self._items:
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
        generate the items for the main menu. This is needed when first
        generating the menu and if something changes by pressing the EJECT
        button
        """
        # Generate the media menu, we need to create a new listing (that sucks)
        # But with the listing we have, the order will be mixed up.
        items = []

        # add default items
        for item in self._items:
            try:
                # split the list on dir/file, title and add_args
                add_args = None
                if isinstance(item, (str, unicode)):
                    # only a filename is given
                    title, filename = u'', item
                elif self.display_type == 'games':
                    # has to be handled specially
                    if item[0] is 'USER':
                        title, filename = item[1], item[2][0]
                    # GAMES code:
                    # else:
                    #     title, filename = machine.title(item[0]), item[2][0]

                    add_args = item[3:]
                else:
                    # title and filename are given
                    (title, filename) = item[:2]
                    if len(item) > 2:
                        # ... and add_args
                        add_args = item[2:]

                filename = os.path.abspath(filename)
                if os.path.isdir(filename):
                    query = kaa.beacon.query(filename=filename)
                    for d in query.get(filter='extmap').get('beacon:dir'):
                        items.append(DirItem(d, self, name = title,
                                             type = self.display_type,
                                             add_args = add_args))
                    continue

                # normal file
                if not os.path.isfile(filename) and \
                       filename.startswith(os.getcwd()):
                    # file is in share dir
                    filename = filename[len(os.getcwd()):]
                    if filename[0] == '/':
                        filename = filename[1:]
                    filename = os.path.join(freevo.conf.SHAREDIR, filename)

                query = kaa.beacon.query(filename=filename)
                listing = query.get(filter='extmap')
                for p in plugin.mimetype(self.display_type):
                    p_items = p.get(self, listing)
                    if title:
                        for i in p_items:
                            i.name = title
                    items += p_items

            except:
                log.exception('Error parsing %s' % str(item))
                continue

        for media in kaa.beacon.media:
            if media.mountpoint == '/':
                continue
            listing = kaa.beacon.wrap(media.root, filter='extmap')
            for p in plugin.mimetype(self.display_type):
                items.extend(p.get(self, listing))
            for d in listing.get('beacon:dir'):
                items.append(DirItem(d, self, name=media.label,
                                     type = self.display_type))
        # add all plugin data
        if self.display_type:
            for p in plugin.get('mainmenu_%s' % self.display_type):
                items += p.items( self )

        return items


    def main_menu(self):
        """
        display the (IMAGE|VIDEO|AUDIO|GAMES) main menu
        """
        # generate all other items
        items = self.main_menu_generate()

        type = '%s main menu' % self.display_type
        item_menu = Menu(self.menutitle, items, type = type,
                         reload_func = self.reload)
        item_menu.autoselect = True
        item_menu.skin_force_text_view = self.force_text_view
        self.item_menu = weakref(item_menu)
        self.pushmenu(item_menu)


    def reload(self):
        """
        Reload the menu. maybe a disc changed or some other plugin.
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
        if event == EJECT and self.item_menu and \
           self.item_menu.selected.info['parent'] == \
           self.item_menu.selected.info['media']:
            self.item_menu.selected.info['media'].eject()
