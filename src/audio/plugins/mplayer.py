# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer plugin and application for audio
# -----------------------------------------------------------------------------
# $Id$
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

# python imports
import os
import logging

# freevo imports
import config
import plugin

from event import *
from application import mplayer

# the logging object
log = logging.getLogger('audio')

class PluginInterface(plugin.Plugin):
    """
    MPlayer plugin for the audio player. It will create an MPlayer object
    and register it to the plugin interface as audio player.
    """
    def __init__(self):
        # init plugin
        plugin.Plugin.__init__(self)

        # register mplayer as the object to play audio
        plugin.register(MPlayer(), plugin.AUDIO_PLAYER, True)


class MPlayer(mplayer.Application):
    """
    The main class to control mplayer for audio playback
    """
    def __init__(self):
        """
        Init the MPlayer object.
        """
        mplayer.Application.__init__(self, 'audio', False)


    def rate(self, item):
        """
        Rating about how good the player can play the given item. Possible
        values are 2 (good), 1 (possible) and 0 (unplayable).
        """
        if item.url.startswith('radio://'):
            return 0
        if item.url.startswith('cdda://'):
            return 1
        return 2


    def play(self, item, player):
        """
        Play a AudioItem with mplayer
        """
        filename = item.filename

        if filename and not os.path.isfile(filename):
            return _('%s\nnot found!') % Unicode(item.url)

        if not filename:
            filename = item.url

        # Build the MPlayer command
        mpl = '%s -slave %s' % ( config.MPLAYER_CMD, config.MPLAYER_ARGS_DEF )

        extra_opts = item.mplayer_options

        is_playlist = False
        if hasattr(item, 'is_playlist') and item.is_playlist:
            is_playlist = True

        if item.network_play and ( str(filename).endswith('m3u') or \
                                   str(filename).endswith('pls')):
            is_playlist = True

        if item.network_play:
            extra_opts += ' -cache 100'

        if hasattr(item, 'reconnect') and item.reconnect:
            extra_opts += ' -loop 0'

        # build the mplayer command
        command = '%s -vo null -ao %s %s %s' % \
                  (mpl, config.MPLAYER_AO_DEV, extra_opts)
        if command.find('-playlist') > 0:
            command = command.replace('-playlist', '')
        command = command.replace('\n', '').split(' ')

        if is_playlist:
            command.append('-playlist')

        if config.MPLAYER_RESAMPLE_AUDIO and item.info['samplerate'] and \
           item.info['samplerate'] < 40000:
            srate = max(41000, min(item.info['samplerate'] * 2, 48000))
            log.info('resample audio from %s to %s' % \
                     (item.info['samplerate'], srate))
            command += [ '-srate', str(srate) ]

        command.append(filename)

        self.item = item
        self.player = player
        mplayer.Application.play(self, command)


    def elapsed(self, sec):
        """
        Callback for elapsed time changes.
        """
        self.item.elapsed = sec
        self.player.refresh()


    def eventhandler(self, event):
        """
        Eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if mplayer.Application.eventhandler(self, event):
            return True

        if event == PLAY_END:
            # Should to be passed to this handler. This happens because the
            # mplayer application code thinks this is the real application
            # shown by Freevo. But it is the player.py code using this object
            # only in the background.
            return self.player.eventhandler(event)

        if event == AUDIO_SEND_MPLAYER_CMD:
            self.send_command('%s\n' % event.arg)
            return True

        if event == PAUSE or event == PLAY:
            self.send_command('pause\n')
            return True

        if event == SEEK:
            self.send_command('seek %s\n' % event.arg)
            return True

        return False
