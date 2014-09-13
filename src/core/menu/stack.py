# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# stack.py - Menu stack for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a menu stack. It is not connected to the GUI so the real
# menu widget must inherit from this class and override the basic GUI functions
# show, hide and redraw.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2009 Dirk Meyer, et al.
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

__all__ = [ 'MenuStack' ]

# python imports
import logging

# kaa imports
import kaa
from kaa.weakref import weakref

# freevo imports
from .. import api as freevo

# get logging object
log = logging.getLogger('menu')


class MenuStack(object):
    """
    The MenuStack handles a stack of Menus
    """
    def __init__(self):
        self._stack = []
        self.locked = False
        if not hasattr(self, 'signals'):
            # The main menu inherits from appication which already
            # defines self.signals. ther menus need this because we
            # want to add a refresh signal
            self.signals = kaa.Signals()
        self.signals['refresh'] = kaa.Signal()

    def back_to_menu(self, menu, refresh=True):
        """
        Go back to the given menu.
        """
        while len(self._stack) > 1 and self._stack[-1] != menu:
            self._stack.pop()
        if refresh:
            self.refresh(True)

    def back_one_menu(self, refresh=True):
        """
        Go back one menu page.
        """
        if len(self._stack) == 1:
            return False
        self._stack.pop()
        if refresh:
            self.refresh(True)
        return True

    def back_submenu(self, refresh=True, reload=False):
        """
        Delete all submenus at the end. Also refreshes or reloads the
        new top menu if the attributes are set to True.
        """
        changed = False
        while len(self._stack) > 0:
            if self._stack[-1].type != 'submenu':
                break
            self._stack.pop()
            changed = True
        if changed and refresh:
            self.refresh(reload)

    def pushmenu(self, menu):
        """
        Add a new Menu to the stack and show it
        """
        if not menu.choices:
            freevo.OSD_MESSAGE.post('directory is empty')
            return
        if menu.type != 'submenu':
            # remove submenus from the stack
            self.back_submenu(False)
        # set stack (self) pointer to menu
        menu.stack = weakref(self)
        if len(self._stack) > 0:
            previous = self._stack[-1]
        else:
            previous = None
        # set menu.pos and append
        menu.pos = len(self._stack)
        self._stack.append(menu)
        if menu.autoselect and len(menu.choices) == 1:
            log.info('autoselect action')
            # autoselect only item in the menu
            menu.choices[0]._get_actions()[0]()
            return
        # refresh will do the update
        self.refresh()

    def refresh(self, reload=False):
        """
        Refresh the stack and redraw it.
        """
        if self.locked:
            return
        menu = self._stack[-1]
        if menu.autoselect and len(menu.choices) == 1:
            # do not show a menu with only one item. Go back to
            # the previous page
            log.info('delete menu with only one item')
            self.back_one_menu()
        elif reload and menu.reload_func:
            # The menu has a reload function. Call it to rebuild
            # this menu. If the functions returns something, replace
            # the old menu with the returned one.
            new_menu = menu.reload_func()
            if new_menu and not isinstance(new_menu, kaa.InProgress):
                # FIXME: is this special case needed?
                self._stack[-1] = new_menu
                menu = new_menu
        self.signals['refresh'].emit()

    def __getitem__(self, attr):
        """
        Return menustack item.
        """
        return self._stack[attr]

    def __setitem__(self, attr, value):
        """
        Set menustack item.
        """
        self._stack[attr] = value

    @property
    def current(self):
        """
        Return the current menu.
        """
        return self._stack[-1]

    def get_json(self, httpserver):
        """
        Return a dict with attributes about the menu used by
        the provided httpserver to send to a remote controlling
        client.
        """
        items = []
        series = None
        # get the various poster used in case they are all the
        # same. If they are, use the image thumbnail for TV shows
        poster = []
        for item in self.current.choices:
            if item.properties.poster and not item.properties.poster in poster:
                poster.append(item.properties.poster)
        for pos, item in enumerate(self.current.choices):
            properties = item.properties
            image = httpserver.register_image(properties.thumbnail)
            attributes = {'name': item.name, 'id': pos, 'image': image, 'type': item.type}
            if properties.series and properties.season and properties.episode:
                attributes['line1'] = properties.title
                attributes['line2'] = '%s %sx%02d' % (properties.series, properties.season, properties.episode)
                if len(poster) > 1:
                    attributes['image'] = httpserver.register_image(item.get_thumbnail_attribute('poster'))
            elif properties.poster:
                attributes['line1'] = properties.name
                attributes['line2'] = ''
                attributes['image'] = httpserver.register_image(item.get_thumbnail_attribute('poster'))
            elif properties.artist and properties.title:
                if item.type == 'directory':
                    if properties.title != properties.artist:
                        attributes['line1'] = properties.title
                        attributes['line2'] = properties.artist
                    else:
                        attributes['line1'] = properties.title
                        attributes['line2'] = ''
                else:
                    attributes['line1'] = properties.title
                    attributes['line2'] = '%s - %s' % (properties.artist, properties.album)
            else:
                attributes['line1'] = item.name
                attributes['line2'] = ''
            items.append(attributes)
        return { 'menu': items }

    def eventhandler(self, event):
        """
        Eventhandler for menu control
        """
        menu = self._stack[-1]
        result = menu.eventhandler(event)
        if result:
            self.refresh()
            return result
        if event == freevo.MENU_GOTO_MAINMENU:
            while len(self._stack) > 1:
                self._stack.pop()
            self.refresh()
            return True
        if event == freevo.MENU_BACK_ONE_MENU:
            return self.back_one_menu()
        if event == freevo.MENU_GOTO_MEDIA:
            goto = event.arg
            if not isinstance(goto, (list, tuple)):
                goto = (goto, None)
            # TODO: it would be nice to remember the current menu stack
            # but that is something we have to do inside mediamenu if it
            # is possible at all.
            if len(self._stack) > 1:
                current = self._stack[1]
                if getattr(current, 'media_type', None) == goto[0] and \
                   (getattr(current, 'media_subtype', None) == goto[1] or not goto[1]):
                    # already in that menu
                    return True
            menu = self._stack[0]
            for item in menu.choices:
                if getattr(item, 'media_type', None) == goto[0] and \
                   (getattr(item, 'media_subtype', None) == goto[1] or not goto[1]):
                    self._stack = [ menu ]
                    menu.select(item)
                    item.actions()[0]()
                    return True
            # not found. :( Try without the subtype
            for item in menu.choices:
                if getattr(item, 'media_type', None) == goto[0]:
                    self._stack = [ menu ]
                    menu.select(item)
                    item.actions()[0]()
                    return True
            return True
        if event == freevo.MENU_GOTO_MENU:
            # TODO: add some doc, example:
            # input.eventmap[menu][5] = MENU_GOTO_MENU /Watch a Movie/My Home Videos
            path = ' '.join(event.arg)
            self._stack = [ self._stack[0] ]
            self.locked = True
            for name in path.split(path[0])[1:]:
                menu = self.current
                for item in menu.choices:
                    if item.name == name:
                        menu.select(item)
                        item.actions()[0]()
                        break
                else:
                    break
            self.locked = False
            self.refresh()
        if not menu.choices:
            # handle empty menus
            if event in ( freevo.MENU_SELECT, freevo.MENU_SUBMENU, freevo.MENU_PLAY_ITEM):
                self.back_one_menu()
                return True
            selected = getattr(self._stack[-2], 'selected', None)
            if selected:
                return selected.eventhandler(event)
            return False
        if menu.selected:
            # pass to selected eventhandler
            return menu.selected.eventhandler(event)
        return False
