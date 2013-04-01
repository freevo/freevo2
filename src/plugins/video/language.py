# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Audio and subtitle language selection
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2013 Dirk Meyer, et al.
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
import sys
import logging

# freevo imports
from ... import core as freevo
from player import player as videoplayer
from item import VideoItem

# the logging object
log = logging.getLogger()


class PluginInterface(freevo.ItemPlugin):
    """
    Plugin to select audio and subtitle language
    """

    plugin_media = 'video'

    #
    # Audio handling
    #

    def audio_selection(self, item, origin, aid):
        """
        Select audio language
        """
        item.language_aid = aid
        if origin is not item:
            self.audio_player_set(item)
        origin.menustack.back_one_menu()

    def audio_menu(self, item, origin):
        """
        Show audio language menu
        """
        items = []
        for aid in range(len(item.metadata.audio)):
            items.append(freevo.ActionItem(self.audio_title(item, aid), item,
                    self.audio_selection, args=(origin, aid)))
        menu = freevo.Menu(_('Language'), items, type='submenu')
        menu.select(item.language_aid)
        origin.menustack.pushmenu(menu)

    def audio_title(self, item, aid = None):
        """
        Get a human readable title for the audio track
        """
        if aid is None:
            aid = item.language_aid
        audio = item.metadata.audio[aid]
        if audio.title and audio.language:
            return '%s - %s' % (audio.title, audio.language)
        if audio.title:
            return audio.title
        if audio.language:
            return audio.language
        return '#%s' % (aid + 1)

    def audio_next(self, item):
        """
        Select the next audio track during playback
        """
        if item.language_aid is None:
            item.language_aid = 0
        item.language_aid += 1
        if item.language_aid >= len(item.metadata.audio):
            item.language_aid = 0
        self.audio_player_set(item)
        msg = _('Audio %s' % self.audio_title(item))
        freevo.Event(freevo.OSD_MESSAGE, msg).post()

    def audio_player_set(self, item):
        """
        Set the audio language in the player
        """
        # FIXME: use the id from videoplayer.player.streaminfo
        return videoplayer.player.set_audio(item.metadata.audio[item.language_aid].id)

    #
    # Subtitle handling
    #

    def subtitle_selection(self, item, origin, sid):
        """
        Select subtitle language
        """
        item.language_sid = sid
        if origin is not item:
            self.subtitle_player_set(item)
        origin.menustack.back_one_menu()

    def subtitle_menu(self, item, origin):
        """
        Show subtitle language menu
        """
        items = []
        for sid in range(-1, len(item.metadata.subtitles)):
            items.append(freevo.ActionItem(
                    self.subtitle_title(item, sid), item, 
                    self.subtitle_selection, args=(origin, sid)))
        menu = freevo.Menu(_('Language'), items, type='submenu')
        menu.select(item.language_sid+1)
        origin.menustack.pushmenu(menu)

    def subtitle_title(self, item, sid = None):
        """
        Get a human readable title for the subtitle
        """
        if sid is None:
            sid = item.language_sid
        if sid == -1:
            return _('Off')
        subtitle = item.metadata.subtitles[sid]
        return subtitle.language or '#%s' % (sid + 1)

    def subtitle_next(self, item):
        """
        Select the next subtitle during playback
        """
        if item.language_sid is None:
            item.language_sid = -1
        item.language_sid += 1
        if item.language_sid >= len(item.metadata.subtitles):
            item.language_sid = -1
        self.subtitle_player_set(item)
        msg = _('Subtitle %s' % self.subtitle_title(item))
        freevo.Event(freevo.OSD_MESSAGE, msg).post()
        
    def subtitle_player_set(self, item):
        """
        Set the subtitle in the player
        """
        if item.language_sid == -1:
            return videoplayer.player.set_subtitle(-1)
        # FIXME: use the id from videoplayer.player.streaminfo
        return videoplayer.player.set_subtitle(item.metadata.subtitles[item.language_sid].id)
        
    #
    # Plugin core
    #

    def actions_generic(self, item, origin):
        if not item.metadata:
            return []
        actions = []
        if len(item.metadata.audio) > 1:
            a = freevo.ActionItem(_('Select language'), item, self.audio_menu)
            a.args = origin,
            actions.append(a)
        if len(item.metadata.subtitles) > 0:
            a = freevo.ActionItem(_('Select subtitle'), item, self.subtitle_menu)
            a.args = origin,
            actions.append(a)
        return actions

    def actions_menu(self, item):
        return self.actions_generic(item, item)

    def actions_playback(self, item, player):
        return self.actions_generic(item, player)

    def eventhandler(self, item, event):
        if event == freevo.VIDEO_NEXT_AUDIOLANG:
            self.audio_next(item)
        if event == freevo.VIDEO_NEXT_SUBTITLE:
            self.subtitle_next(item)
        if event == freevo.PLAY_START:
            if item.language_aid is not None:
                videoplayer.player.set_audio(item.language_aid)
            if item.language_sid is not None:
                videoplayer.player.set_subtitle(item.language_sid)

VideoItem.register_attribute('language_aid', True)
VideoItem.register_attribute('language_sid', True)
