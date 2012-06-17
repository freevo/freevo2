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
import kaa.metadata

# Freevo imports
from ... import core as freevo

# get logging object
log = logging.getLogger('video')


class Player(freevo.Application):
    """
    Video player object.
    """

    name = 'videoplayer'
    player = None

    def __init__(self):
        capabilities = (freevo.CAPABILITY_FULLSCREEN, )
        super(Player, self).__init__('video', capabilities)

    @kaa.coroutine()
    def play(self, item):
        """
        play an item
        """
        if not self.status in (freevo.STATUS_IDLE, freevo.STATUS_STOPPED):
            # Already running, stop the current player by sending a STOP
            # event. The event will also get to the playlist behind the
            # current item and the whole list will be stopped.
            freevo.Event(freevo.STOP, handler=self.eventhandler).post()
            # Now wait for our own 'stop' signal
            yield kaa.inprogress(self.signals['stop'])
            if not self.status in (freevo.STATUS_IDLE, freevo.STATUS_STOPPED):
                log.error('unable to stop current video playback')
                yield False
        if not kaa.main.is_running():
            # Freevo is in shutdown mode, do not start a new player, the old
            # only stopped because of the shutdown.
            yield False
        self.context.item = item.properties
        self.context.candy_player = item.player
        # Try to get VIDEO and AUDIO resources. The ressouces will be freed
        # by the system when the application switches to STATUS_STOPPED or
        # STATUS_IDLE.
        if (yield self.get_resources('AUDIO', 'VIDEO', force=True)) == False:
            log.error("Can't get resource AUDIO, VIDEO")
            yield False
        # store item and playlist
        self.item = item
        self.playlist = self.item.playlist
        if self.playlist:
            self.playlist.select(self.item)
        # set the current item to the gui engine
        # self.engine.set_item(self.item)
        self.status = freevo.STATUS_RUNNING
        self.is_in_menu = False
        self.eventmap = 'video'
        if not self.item.selected_audio:
            self.item.selected_audio = 0
        self.item.elapsed_secs = 0
        freevo.PLAY_START.post(self.item)
        # update GUI to a blank screen
        yield kaa.NotFinished
        # get the player object; each play() call has its own player
        # unless it is a playlist, in this case we want to reuse the
        # player
        self.player = self.widget.stage.get_widget('player')
        self.player.url = item.filename
        self.player.config['mplayer.passthrough'] = \
            bool(freevo.config.video.player.mplayer.passthrough)
        self.player.config['mplayer.vdpau'] = \
            bool(freevo.config.video.player.mplayer.vdpau)
        self.player.set_audio(self.item.selected_audio)
        # self.player.seek(20, self.player.SEEK_PERCENTAGE)
        self.player.signals['finished'].connect_weak_once(freevo.PLAY_END.post, self.item)
        self.player.signals['progress'].connect_weak(self.set_elapsed)
        self.player.play()
        yield True

    def set_elapsed(self, pos):
        """
        Callback from kaa.candy to update the playtime
        """
        if self.item.elapsed_secs != round(pos):
            self.item.elapsed_secs = round(pos)
            self.context.sync()

    def stop(self):
        """
        Stop playing.
        """
        if self.status != freevo.STATUS_RUNNING:
            return True
        self.status = freevo.STATUS_STOPPING
        self.player.stop()

    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
        if event == freevo.STOP:
            # Stop the player and pass the event to the item
            self.stop()
            self.item.eventhandler(event)
            return True
        if event == freevo.PLAY_START:
            self.item.eventhandler(event)
            return True
        if event == freevo.PLAY_END and event.arg == self.item:
            # Now the player has stopped (either we called self.stop() or the
            # player stopped by itself. So we need to set the application to
            # to stopped.
            if self.player:
                self.player = None
            self.status = freevo.STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == freevo.STATUS_STOPPED:
                self.status = freevo.STATUS_IDLE
            return True
        if self.player:
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
            if event == freevo.VIDEO_NEXT_AUDIOLANG:
                # FIXME: cache this or add it to beacon
                metadata = kaa.metadata.parse(self.item.filename)
                self.item.selected_audio += 1
                if self.item.selected_audio >= len(metadata.audio):
                    self.item.selected_audio = 0
                self.player.set_audio(self.item.selected_audio)
                lang = metadata.audio[self.item.selected_audio].language or \
                    '#%s' % self.item.selected_audio
                freevo.Event(freevo.OSD_MESSAGE, _('Audio %s' % lang)).post()
        return self.item.eventhandler(event)


# create singleton object
player = kaa.utils.Singleton(Player)

# create functions to use from the outside
play = player.play
stop = player.stop
