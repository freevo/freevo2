# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer plugin for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.39  2004/07/26 18:10:17  dischi
# move global event handling to eventhandler.py
#
# Revision 1.38  2004/07/21 11:18:26  dischi
# fix unicode error
#
# Revision 1.37  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.36  2004/07/09 04:08:50  outlyer
# Fixed webradio support for shoutcast streams using the 'pls' extension. Most
# use m3u, but some (including ones in the webradio.fxd file) use pls.
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


import os
import re

import config     # Configuration handler. reads config file.
import childapp   # Handle child applications

import plugin

from event import *


class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the audio player. Use mplayer to play all audio
    files.
    """
    def __init__(self):
        # create the mplayer object
        plugin.Plugin.__init__(self)

        # register mplayer as the object to play audio
        plugin.register(MPlayer(), plugin.AUDIO_PLAYER, True)


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self):
        self.name     = 'mplayer'
        self.app_mode = 'audio'
        self.app      = None


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.url.startswith('radio://'):
            return 0
        if item.url.startswith('cdda://'):
            return 1
        return 2

        
    def get_demuxer(self, filename):
        DEMUXER_MP3 = 17
        DEMUXER_OGG = 18
        rest, extension     = os.path.splitext(filename)
        if extension.lower() == '.mp3':
            return "-demuxer " + str(DEMUXER_MP3)
        if extension.lower() == '.ogg':
            return "-demuxer " + str(DEMUXER_OGG)
        else:
            return ''


    def play(self, item, playerGUI):
        """
        play a audioitem with mplayer
        """
        self.playerGUI = playerGUI
        filename       = item.filename

        if filename and not os.path.isfile(filename):
            return _('%s\nnot found!') % Unicode(item.url)
            
        if not filename:
            filename = item.url
            
        # Build the MPlayer command
        mpl = '--prio=%s %s -slave %s' % (config.MPLAYER_NICE,
                                          config.MPLAYER_CMD,
                                          config.MPLAYER_ARGS_DEF)

        if not item.network_play:
            demux = ' %s ' % self.get_demuxer(filename)
        else:
            # Don't include demuxer for network files
            demux = ''

        extra_opts = item.mplayer_options

        is_playlist = False
        if hasattr(item, 'is_playlist') and item.is_playlist:
            is_playlist = True
        
        if item.network_play and ( str(filename).endswith('m3u') or str(filename).endswith('pls')):
            is_playlist = True

        if item.network_play:
            extra_opts += ' -cache 100'

        if hasattr(item, 'reconnect') and item.reconnect:
            extra_opts += ' -loop 0'
            
        command = '%s -vo null -ao %s %s %s' % (mpl, config.MPLAYER_AO_DEV, demux,
                                                extra_opts)

        if command.find('-playlist') > 0:
            command = command.replace('-playlist', '')
            
        command = command.replace('\n', '').split(' ')

        if is_playlist:
            command.append('-playlist')
            
        command.append(filename)

        self.plugins = plugin.get('mplayer_audio')
        for p in self.plugins:
            command = p.play(command, self)
            
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item

        _debug_('MPlayer.play(): Starting cmd=%s' % command)
            
        self.app = MPlayerApp(command, self)
        return None
    

    def stop(self):
        """
        Stop mplayer
        """
        self.app.stop('quit\n')

        for p in self.plugins:
            command = p.stop()


    def is_playing(self):
        return self.app.isAlive()


    def refresh(self):
        self.playerGUI.refresh()
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        for p in self.plugins:
            if p.eventhandler(event):
                return True

        if event == PLAY_END and event.arg:
            self.stop()
            if self.playerGUI.try_next_player():
                return True
            
        if event == AUDIO_SEND_MPLAYER_CMD:
            self.app.write('%s\n' % event.arg)
            return True

        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        elif event == PAUSE or event == PLAY:
            self.app.write('pause\n')
            return True

        elif event == SEEK:
            self.app.write('seek %s\n' % event.arg)
            return True

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
            
            
# ======================================================================

class MPlayerApp(childapp.ChildApp2):
    """
    class controlling the in and output from the mplayer process
    """
    def __init__(self, app, player):
        self.item        = player.item
        self.player      = player
        self.elapsed     = 0
        self.stop_reason = 0 # 0 = ok, 1 = error
        self.RE_TIME     = re.compile("^A: *([0-9]+)").match
	self.RE_TIME_NEW = re.compile("^A: *([0-9]+):([0-9]+)").match

        # check for mplayer plugins
        self.stdout_plugins  = []
        self.elapsed_plugins = []
        for p in plugin.get('mplayer_audio'):
            if hasattr(p, 'stdout'):
                self.stdout_plugins.append(p)
            if hasattr(p, 'elapsed'):
                self.elapsed_plugins.append(p)
        childapp.ChildApp2.__init__(self, app, stop_osd=0)


    def stop_event(self):
        return Event(PLAY_END, self.stop_reason, handler=self.player.eventhandler)

        
    def stdout_cb(self, line):
        if line.startswith("A:"):         # get current time
            m = self.RE_TIME_NEW(line)
            if m:
                self.stop_reason = 0
		timestrs = m.group().split(":")
		if len(timestrs) == 5:
		    # playing for days!
                    self.item.elapsed = 86400*int(timestrs[1]) + \
		                        3600*int(timestrs[2]) + \
		                        60*int(timestrs[3]) + \
					int(timestrs[4])
                elif len(timestrs) == 4:
		    # playing for hours
                    self.item.elapsed = 3600*int(timestrs[1]) + \
		                        60*int(timestrs[2]) + \
					int(timestrs[3])
                elif len(timestrs) == 3:
		    # playing for minutes
                    self.item.elapsed = 60*int(timestrs[1]) + int(timestrs[2])
                elif len(timestrs) == 2:
		    # playing for only seconds
                    self.item.elapsed = int(timestrs[1])
            else:
                m = self.RE_TIME(line) # Convert decimal 
                if m:
                    self.item.elapsed = int(m.group(1))

            if self.item.elapsed != self.elapsed:
                self.player.refresh()
            self.elapsed = self.item.elapsed
            
            for p in self.elapsed_plugins:
                p.elapsed(self.elapsed)
            
        elif not self.item.elapsed:
            for p in self.stdout_plugins:
                p.stdout(line)
                



    def stderr_cb(self, line):
        if line.startswith('Failed to open'):
            self.stop_reason = 1
        for p in self.stdout_plugins:
            p.stdout(line)
