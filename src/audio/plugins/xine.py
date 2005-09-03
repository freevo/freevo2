# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xine.py - the Freevo xine plugin and application for audio
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
import logging

# freevo imports
import config
import plugin

from event import *
from application import ChildApp

# the logging object
log = logging.getLogger('audio')


class PluginInterface(plugin.Plugin):
    """
    MPlayer plugin for the audio player. It will create an MPlayer object
    and register it to the plugin interface as audio player.
    """
    def __init__(self):
        config.detect('xine')

        try:
            if not config.CONF.fbxine:
                raise Exception
        except:
            self.reason = "'fbxine' not found"
            return

        if config.FBXINE_VERSION < '0.99.1' and \
               config.FBXINE_VERSION < '0.9.23':
            self.reason = "'fbxine' version too old"
            return
            
        plugin.Plugin.__init__(self)
        # register xine as the object to play
        plugin.register(Xine(), plugin.AUDIO_PLAYER, True)



class Xine(ChildApp):
    """
    The main class to control xine for audio playback
    """
    def __init__(self):
        ChildApp.__init__(self, 'xine', 'audio', False, False, False)
        self.name = 'xine'
        self.app = None
        self.command = '%s -V none -A %s --stdctl' % \
                       (config.CONF.fbxine, config.XINE_AO_DEV)
        if config.FBXINE_USE_LIRC:
            self.command = '%s --no-lirc' % self.command

        
    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.url.startswith('radio://'):
            return 0
        return 2


    def play(self, item, player):
        """
        play an audio file with xine
        """
        self.item = item
        add_args  = []
        
        url = item.url
        if url.startswith('cdda://'):
            url = url.replace('//', '/')
            add_args.append('cfg:/input.cdda_device:%s' % \
                            item.media.devicename)
            
        command  = self.command.split(' ') + add_args + [ url ]
    
        self.item = item
        self.player = player

        # start child
        self.child_start(command, config.MPLAYER_NICE, 'quit\n')
        return None


    def is_playing(self):
        """
        Return True if mplayer is playing right now.
        """
        return self.child_running()


    def eventhandler(self, event):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        ChildApp.eventhandler(self, event)

        if event == PLAY_END:
            # Should to be passed to this handler. This happens because the
            # mplayer application code thinks this is the real application
            # shown by Freevo. But it is the player.py code using this object
            # only in the background.
            return self.player.eventhandler(event)

        if not self.child_running():
            return False

        if event == PAUSE or event == PLAY:
            self.child_stdin('pause\n')
            return True

        if event == SEEK:
            pos = int(event.arg)
            if pos < 0:
                action='SeekRelative-'
                pos = 0 - pos
            else:
                action='SeekRelative+'
            if pos <= 15:
                pos = 15
            elif pos <= 30:
                pos = 30
            else:
                pos = 30
            self.child_stdin('%s%s\n' % (action, pos))
            return True

        return False
