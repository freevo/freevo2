#if 0 /*
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
# Revision 1.36  2004/07/09 04:08:50  outlyer
# Fixed webradio support for shoutcast streams using the 'pls' extension. Most
# use m3u, but some (including ones in the webradio.fxd file) use pls.
#
# Revision 1.35  2004/02/19 04:37:21  gsbarbieri
# MPlayer Audio Visualization support.
# Get mpav from http://gsbarbieri.sytes.net/mpav/
#
# Revision 1.34  2004/01/31 12:39:47  dischi
# delete unused audio variables
#
# Revision 1.33  2004/01/14 20:36:16  mikeruelle
# they guys do not play radio
#
# Revision 1.32  2003/12/29 22:33:30  dischi
# Oops
#
# Revision 1.31  2003/12/29 22:09:19  dischi
# move to new Item attributes
#
# Revision 1.30  2003/12/13 14:27:19  outlyer
# Since ChildApp2 defaults to stopping the OSD, stop_osd=0 needs to be defined
# here or the audio player will try to stop the display and then try to write
# to the screen (and crash)
#
# Revision 1.29  2003/12/10 19:10:35  dischi
# AUDIO_PLAY_END is not needed anymore
#
# Revision 1.28  2003/12/10 19:02:38  dischi
# move to new ChildApp2 and remove the internal thread
#
# Revision 1.27  2003/12/06 13:43:35  dischi
# expand the <audio> parsing in fxd files
#
# Revision 1.26  2003/11/22 15:30:55  dischi
# support more than one player
#
# Revision 1.25  2003/11/11 18:01:44  dischi
# fix playback problems with fxd files (and transform to list app style)
#
# Revision 1.24  2003/11/08 13:21:18  dischi
# network m3u support, added AUDIOCD plugin register
#
# Revision 1.23  2003/10/21 21:17:41  gsbarbieri
# Some more i18n improvements.
#
# Revision 1.22  2003/10/20 13:36:07  outlyer
# Remove the double-quit
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
import re

import config     # Configuration handler. reads config file.
import childapp   # Handle child applications

import rc
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
            return _('%s\nnot found!') % item.url
            
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
