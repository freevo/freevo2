#if 0 /*
# -----------------------------------------------------------------------
# playlist.py - Plugin for playlist support
# -----------------------------------------------------------------------
# $Id: 
#
# Notes: This plugin will allow you to make playlists.
#
# -----------------------------------------------------------------------
# $Log: 
#
#
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
#endif

import os
import menu
import plugin
import time
import config

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

    EVENTS['menu']['REC'] = Event(MENU_CALL_ITEM_ACTION, arg='queue_a_track')

    """
    
    def __init__(self,playlist_folder=None, naming='Freevo Playlist - %m%d-%I%M'):
        if playlist_folder == None:
            self.playlist_folder = ('%s/playlists' % config.FREEVO_CACHEDIR)
        else:
            self.playlist_folder = playlist_folder
        if not os.path.isdir(self.playlist_folder):
            os.mkdir(self.playlist_folder)

        self.naming = naming

        config.DIR_AUDIO.append(('Playlists',self.playlist_folder))
        self.playlist_handle = None
        plugin.ItemPlugin.__init__(self)


    def actions(self, item):
        self.item = item
        return [ ( self.queue_file, 'Queue a Track',
                               'queue_a_track'),
                 ( self.new_playlist, 'Make a New Playlist',
                               'close_playlist')]

    def queue_file(self,arg=None, menuw=None):
        if not self.playlist_handle:
            self.playlist_handle = open(('%s/%s.m3u' % (self.playlist_folder, time.strftime(self.naming))),'w+')
        self.playlist_handle.write('%s\n' % self.item.filename)
        self.playlist_handle.flush()
        return

    def new_playlist(self, arg=None, menuw=None):
        if self.playlist_handle:
            self.playlist_handle.close()
            self.playlist_handle = None
        return
