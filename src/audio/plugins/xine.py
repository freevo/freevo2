# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for audio
# -----------------------------------------------------------------------
# $Id$
#
# This contains plugin, control and childapp classes for using xine as
# audio player.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.22  2004/10/06 19:13:41  dischi
# use config auto detection for xine version
#
# Revision 1.21  2004/10/06 19:01:34  dischi
# use new childapp interface
#
# Revision 1.20  2004/09/29 18:58:17  dischi
# cleanup
#
# Revision 1.19  2004/09/29 18:48:41  dischi
# fix xine lirc handling
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

# python imports
import re

# freevo imports
import config
import childapp
import plugin
from event import *


class PluginInterface(plugin.Plugin):
    """
    Xine plugin for the audio player.
    """
    def __init__(self):
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


class Xine:
    """
    The main class to control xine for audio playback
    """
    def __init__(self):
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


    def play(self, item, playerGUI):
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
        self.app = XineApp(command, playerGUI)
    

    def is_playing(self):
        return self.app.isAlive()


    def stop(self):
        """
        Stop xine
        """
        self.app.stop('quit\n')
            

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if event == PAUSE or event == PLAY:
            self.app.write('pause\n')
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
            self.app.write('%s%s\n' % (action, pos))
            return True

        return False

        
# ======================================================================

class XineApp(childapp.Instance):
    """
    class controlling the in and output from the xine process
    """
    def __init__(self, app, player):
        self.item        = player.item
        self.player      = player
        self.elapsed     = 0
        self.stop_reason = 0 # 0 = ok, 1 = error
        childapp.Instance.__init__(self, app, stop_osd=0)


    def stop_event(self):
        return Event(PLAY_END, self.stop_reason,
                     handler=self.player.eventhandler)


    def stdout_cb(self, line):
        if line.startswith("time: "):
            self.item.elapsed = int(line[6:])
            if self.item.elapsed != self.elapsed:
                self.player.refresh()
            self.elapsed = self.item.elapsed


    def stderr_cb(self, line):
        if line.startswith('Unable to open MRL'):
            self.stop_reason = 1
