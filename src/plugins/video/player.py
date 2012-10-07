# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - the Freevo video player
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2012 Dirk Meyer, et al.
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

__all__ = [ 'play', 'stop' ]

# python imports
import logging

# kaa imports
import kaa
import kaa.utils
import kaa.candy

# Freevo imports
from ... import core as freevo

# get logging object
log = logging.getLogger('video')


class Player(freevo.Player):
    """
    Video player object.
    """

    name = 'videoplayer'
    player = None

    def __init__(self):
        capabilities = (freevo.CAPABILITY_TOGGLE, freevo.CAPABILITY_FULLSCREEN, )
        super(Player, self).__init__('video', capabilities)

    @kaa.coroutine()
    def play(self, item):
        """
        play an item
        """
        if not (yield super(Player, self).play(item, ['AUDIO', 'VIDEO'])):
            yield False
        if item.url.startswith('dvd://'):
            # kaa.candy does not support dvd playback with gstreamer
            item.player = 'mplayer'
        # FIXME: this handle is kind of ugly. Must be fixed in
        # kaa.candy supporting player changes before play()
        self.context.candy_player = item.player
        self.eventmap = 'video'
        if self.item.selected_audio == None:
            self.item.selected_audio = 0
        if self.item.selected_sub == None:
            self.item.selected_sub = -1
        # get the player object; each play() call has its own player
        # unless it is a playlist, in this case we want to reuse the
        # player
        self.streaminfo = None
        self.player = self.widget.get_widget('player')
        self.player.uri = item.filename or item.url
        self.player.config['mplayer.passthrough'] = \
            bool(freevo.config.video.player.mplayer.passthrough)
        self.player.config['mplayer.vdpau'] = \
            bool(freevo.config.video.player.mplayer.vdpau)
        if not item.url.startswith('dvd://'):
            # Restore last audio/subtitle settings. This only makes
            # sense for files and not DVDs with changing audio /
            # subtitle streams depending on the title.
            self.player.set_audio(self.item.selected_audio)
            self.player.set_subtitle(self.item.selected_sub)
        # self.player.seek(20, self.player.SEEK_PERCENTAGE)
        self.player.signals['finished'].connect_weak_once(self.PLAY_END.post, self.item)
        self.player.signals['progress'].connect_weak(self.set_elapsed)
        self.player.signals['streaminfo'].connect_weak(self.set_streaminfo)
        self.player.play()
        self.PLAY_START.post(self.item)
        yield True

    def set_streaminfo(self, streaminfo):
        """
        Callback from kaa.candy with information about the current stream
        """
        self.streaminfo = streaminfo
        self.eventmap = 'dvdnav' if streaminfo['is_menu'] else 'video'

    def do_stop(self):
        """
        Stop playing.
        """
        self.player.stop()

    def get_json(self, httpserver):
        """
        Return a dict with attributes about the application used by
        the provided httpserver to send to a remote controlling
        client.
        """
        properties = self.item.properties
        image = httpserver.register_image(properties.image)
        poster = httpserver.register_image(self.item.get_thumbnail_attribute('poster'))
        return { 'title': properties.title, 
                 'series': properties.series, 
                 'season': properties.season, 
                 'episode': properties.episode,
                 'description': properties.description,
                 'imdb': properties.imdb,
                 'image': image,
                 'poster': poster,
               }

    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
        if super(Player, self).eventhandler(event):
            # Generic start/stop handling
            if event == freevo.PLAY_END and self.player:
                self.player = None
            return True
        if not self.player:
            # No player object and therefore, no playback control
            return self.item.eventhandler(event)
        # player control makes only sense if the player is still running
        if event == freevo.TOGGLE_OSD:
            self.widget.osd_toggle('info')
        if event in (freevo.PAUSE, freevo.PLAY):
            if self.player.state == kaa.candy.STATE_PLAYING:
                self.widget.osd_show('pause')
                self.player.pause()
                return True
            if self.player.state == kaa.candy.STATE_PAUSED:
                self.widget.osd_hide('pause')
                self.player.resume()
                return True
            return False
        if event == freevo.SEEK:
            if not self.widget.osd_visible('info'):
                self.widget.osd_show('seek', autohide=2)
            self.player.seek(int(event.arg), kaa.candy.SEEK_RELATIVE)
            return True
        if event == freevo.VIDEO_CHANGE_ASPECT:
            self.player.set_aspect(kaa.candy.NEXT)
        if event == freevo.VIDEO_NEXT_AUDIOLANG:
            self.item.selected_audio = self.player.set_audio(kaa.candy.NEXT)
            lang = self.streaminfo['audio'][self.item.selected_audio] or \
                '#%s' % self.item.selected_audio
            freevo.Event(freevo.OSD_MESSAGE, _('Audio %s' % lang)).post()
        if event == freevo.VIDEO_NEXT_SUBTITLE:
            self.item.selected_sub = self.player.set_subtitle(kaa.candy.NEXT)
            if self.item.selected_sub == -1:
                lang = _('off')
            else:
                lang = self.streaminfo['subtitle'][self.item.selected_sub] or \
                '#%s' % self.item.selected_sub
            freevo.Event(freevo.OSD_MESSAGE, _('Subtitle %s' % lang)).post()
        if str(event).startswith('DVDNAV_'):
            self.player.nav_command(str(event)[7:].lower())
            return True
        return self.item.eventhandler(event)


# create singleton object
player = kaa.utils.Singleton(Player)

# create functions to use from the outside
play = player.play
stop = player.stop
