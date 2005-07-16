# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# playlist.py - Plugin for playlist support
# -----------------------------------------------------------------------
# $Id: 
#
# Notes: This plugin will allow you to make playlists.
#
# TODO:
#       Make it possible to remove items from the playlist
#       Force Freevo to reload the playlist when an item is added...
#       Feedback onscreen for when an item is added. Preferably not a
#         popup box since it makes things harder if you're adding lots of
#         stuff
#       Ability to add entire folders or even other playlists
#
# -----------------------------------------------------------------------
# $Log: 
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */


import os
import menu
import plugin
import time
import config
import util

from event import *

class PluginInterface(plugin.ItemPlugin):
    """
    This plugin will allow you to create playlists of audio files. It will also
    add a "Playlists" submenu to your Audio Folder. 
    To activate this plugin, put the following in your local_conf.py.

    plugin.activate( 'audio.playlist' ) 

    You can also change the physical location of the Playlists folder, or 
    specify the naming convention like this:

    plugin.activate('audio.playlist', args=('/path/to/folder','Freevo %m%d'))

    where the naming format uses the standard strftime format options.

    You can also add a hot button to queue a file without traversing the submenu.

    Add something like this to your local_conf.py

    EVENTS['menu']['REC']  = Event(MENU_CALL_ITEM_ACTION, 'queue_a_track')
    EVENTS['menu']['SAVE'] = Event(MENU_CALL_ITEM_ACTION, 'close_playlist')

    """
    
    def __init__(self,playlist_folder=None, naming='Freevo Playlist - %m%d-%I%M'):
        self.reason = config.REDESIGN_UNKNOWN
        return
        if playlist_folder == None:
            self.playlist_folder = ('%s/playlists' % config.FREEVO_CACHEDIR)
        else:
            self.playlist_folder = playlist_folder
        if not os.path.isdir(self.playlist_folder):
            os.mkdir(self.playlist_folder)

        self.naming = naming

        config.AUDIO_ITEMS.append((_('Playlists'), self.playlist_folder))
        self.playlist_handle = None
        plugin.ItemPlugin.__init__(self)


    def actions(self, item):
        self.item = item

        if self.item.parent and self.item.parent.type != 'dir':
            # only activate this for directory items
            return []

        if self.item.type == 'playlist':
            # that could cause us much trouble
            return []

        items = [ (self.queue_file, _('Enqueue this Music in Playlist'), 'queue_a_track') ]
        if self.playlist_handle:
            items.append((self.new_playlist, _( 'Make a new Audio Playlist' ),
                          'close_playlist'))
        return items

    
    def queue_file(self,arg=None, menuw=None):
        if not self.playlist_handle:
            self.playlist_handle = open(('%s/%s.m3u' % (self.playlist_folder,
                                                        time.strftime(self.naming))),'w+')
        for f in self.item.files.get():
            if os.path.isdir(f):
                for file in util.match_files_recursively(f, config.AUDIO_SUFFIX):
                    self.playlist_handle.write('%s\n' % os.path.join(f, file))
            else:
                self.playlist_handle.write('%s\n' % f)
        self.playlist_handle.flush()
        if menuw:
            if self.item.type == 'dir':
                menuw.delete_submenu(True, True, _('Queued Directory'))
            else:
                menuw.delete_submenu(True, True, _('Queued Track'))
        return

    def new_playlist(self, arg=None, menuw=None):
        if self.playlist_handle:
            self.playlist_handle.close()
            self.playlist_handle = None
        if menuw:
            menuw.delete_submenu(True, True, _('Added New Playlist'))
        return
