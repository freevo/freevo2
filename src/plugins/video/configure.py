# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# configure.py - Configure video playing
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines some configure actions for a VideoItem.
#
# Note: The functions are not bound to a class, so the item passed by the
# menu stack is not the VideoItem that should be changed. To resolve that
# problem, all functions get the VideoItem as parameter, the first parameter
# 'selected' is the item in the menu that is selected, a simple item.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
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

__all__ = [ 'get_items' ]

# kaa imports
import kaa.popcorn

# freevo imports
from ... import core as freevo

# def play_movie(item, **kwargs):
#     """
#     play the movie (again)
#     """
#     item.menustack.back_to_menu(item.menu, False)
#     item.play(**kwargs)


# def set_variable(item, variable, value):
#     """
#     Set a variable for the item.
#     """
#     setattr(item, variable, value)
#     item.menustack.back_one_menu()


# def start_chapter(item, chapter):
#     """
#     Handle chapter selection.
#     """
#     item.menustack.back_to_menu(item.menu, False)
#     # FIXME: kaa.popcorn syntax
#     play_movie(item, chapter=chapter)


# def audio_selection(item):
#     """
#     Submenu for audio selection.
#     """
#     menu_items = []
#     for a in item.info['audio']:
#         if not a.has_key('id') or a['id'] in ('', None):
#             a['id'] = item.info['audio'].index(a) + 1
#         if not a.has_key('language') or not a['language']:
#             a['language'] = _('Stream %s') % a['id']
#         if not a.has_key('channels') or not a['channels']:
#             a['channels'] = 2 # wild guess :-)
#         if not a.has_key('codec') or not a['codec']:
#             name = '%s (channels=%s)' % (a['language'], a['channels'])
#         else:
#             name = '%s (channels=%s %s)' % (a['language'], a['channels'], a['codec'])
#         action = freevo.ActionItem(name, item, set_variable)
#         action.parameter('selected_audio', a['id'])
#         menu_items.append(action)
#     item.menustack.pushmenu(freevo.Menu(_('Audio Menu'), menu_items))


# def subtitle_selection(item):
#     """
#     Submenu for subtitle selection.
#     """
#     action = freevo.ActionItem(_('no subtitles'), item, set_variable)
#     action.parameter('selected_subtitle', -1)
#     menu_items = [ action ]
#     for pos, s in enumerate(item.info['subtitles']):
#         name = s.get('language')
#         if s.get('title'):
#             name = '%s (%s)' % (s.get('name'), s.get('language'))
#         action = freevo.ActionItem(name, item, set_variable)
#         action.parameter('selected_subtitle', pos)
#         menu_items.append(action)
#     item.menustack.pushmenu(freevo.Menu(_('Subtitle Menu'), menu_items))


# def chapter_selection(item):
#     """
#     Submenu for chapter selection.
#     """
#     menu_items = []
#     if isinstance(item.info['chapters'], int):
#         for c in range(1, item.info['chapters']):
#             a = freevo.ActionItem(_('Play chapter %s') % c, item, start_chapter)
#             a.parameter('-chapter %s' % c)
#             menu_items.append(a)
#     elif item.info['chapters']:
#         for c in item.info['chapters']:
#             pos = '%01d:%02d:%02d' % (int(c.pos) / 3600, (int(c.pos) / 60) % 60,
#                                       int(c.pos) % 60)
#             a = freevo.ActionItem(pos, item, start_chapter)
#             a.parameter('-ss %s' % c.pos)
#             menu_items.append(a)
#     item.menustack.pushmenu(freevo.Menu(_('Chapter Menu'), menu_items))


# def toggle(item, name, variable):
#     """
#     Basic toggle function.
#     """
#     item[variable] = not item[variable]
#     # replace item
#     menuitem = item.menustack.current.selected
#     menuitem.menu.change_item(menuitem, add_toggle(item, name, variable))
#     # update menu
#     item.menustack.refresh()


# def add_toggle(item, name, var):
#     """
#     Add a 'toggle' item.
#     """
#     if item[var]:
#         action = freevo.ActionItem(_('Turn off %s') % name, item, toggle)
#     else:
#         action = freevo.ActionItem(_('Turn on %s') % name, item, toggle)
#     action.parameter(name, var)
#     return action


class PluginInterface(freevo.ItemPlugin):
    """
    class to configure video playback
    """
    def actions(self, item):
        """
        Return additional actions for the item.
        """
        return [ freevo.Action(_('Configure'), self.configure) ]
    
    def get_items(self, item):
        return [
            (freevo.ActionItem(_('Player: %s') % item.player, item, self.player_selection))
        ]

    def configure(self, item):
        item.menustack.pushmenu(freevo.Menu(_('Configure'), self.get_items(item), type='submenu'))

    def player_selection(self, item):
        """
        Submenu for player selection.
        """
        if item.player == 'gstreamer':
            item.player = 'mplayer'
        elif item.player == 'mplayer':
            item.player = 'gstreamer'
        item.menustack.current.selected.name = _('Player: %s') % item.player
        item.menustack.current.state += 1
        item.menustack.context.sync(force=True)
