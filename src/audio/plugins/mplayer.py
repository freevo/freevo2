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

import time, os
import string
import threading, signal
import re

import config     # Configuration handler. reads config file.
import util       # Various utilities
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
        mplayer = util.SynchronizedObject(MPlayer())

        # register it as the object to play audio
        plugin.register(mplayer, plugin.AUDIO_PLAYER, True)


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self):
        self.name = 'mplayer'
        self.thread = childapp.ChildThread()
        self.mode = None
        self.app_mode = 'audio'


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.filename.startswith('cdda://'):
            return 1
        return 2

        
    def get_demuxer(self, filename):
        DEMUXER_MP3 = 17
        DEMUXER_OGG = 18
        rest, extension     = os.path.splitext(filename)
        if string.lower(extension) == '.mp3':
            return "-demuxer " + str(DEMUXER_MP3)
        if string.lower(extension) == '.ogg':
            return "-demuxer " + str(DEMUXER_OGG)
        else:
            return ''


    def play(self, item, playerGUI):
        """
        play a audioitem with mplayer
        """
        if item.url:
            filename = item.url
        else:
            filename = item.filename

        self.playerGUI = playerGUI
        
        # Is the file streamed over the network?
        if filename.find('http://') == 0 or filename.find('https://') == 0 or \
               filename.find('mms://') == 0 or filename.find('rtsp://') == 0:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0

        if not os.path.isfile(filename) and filename.find('://') == -1:
            return _('%s\nnot found!') % filename
            
        # Build the MPlayer command
        mpl = '--prio=%s %s -slave %s' % (config.MPLAYER_NICE,
                                          config.MPLAYER_CMD,
                                          config.MPLAYER_ARGS_DEF)

        if not network_play:
            demux = ' %s ' % self.get_demuxer(filename)
        else:
            # Don't include demuxer for network files
            demux = ''

        extra_opts = item.mplayer_options
        if network_play and filename.endswith('m3u') and \
               extra_opts.find('-playlist') == -1:
            extra_opts += ' -playlist'

        if network_play:
            extra_opts += ' -cache 100'

        command = '%s -vo null -ao %s %s %s' % (mpl, config.MPLAYER_AO_DEV, demux,
                                                extra_opts)
        
        command = command.replace('\n', '').split(' ')
        command.append(filename)
        
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item

        if not self.item.valid:
            # Invalid file, show an error and survive.
            return _('Invalid audio file')

        _debug_('MPlayer.play(): Starting thread, cmd=%s' % command)
            
        self.thread.start(MPlayerApp, (command, item, self.refresh))
        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.stop('quit\n')


    def is_playing(self):
        return self.thread.mode != 'idle'


    def refresh(self):
        self.playerGUI.refresh()
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        if event == AUDIO_PLAY_END:
            if event.arg:
                self.stop()
                if self.playerGUI.try_next_player():
                    return True
            event = PLAY_END
            
        if event == AUDIO_SEND_MPLAYER_CMD:
            self.thread.app.write('%s\n' % event.arg)
            return True

        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        elif event == PAUSE or event == PLAY:
            self.thread.app.write('pause\n')
            return True

        elif event == SEEK:
            self.thread.app.write('seek %s\n' % event.arg)
            return True

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
            
            
# ======================================================================

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, (app, item, refresh)):
        self.item = item
        self.elapsed = 0
        childapp.ChildApp.__init__(self, app)
        self.RE_TIME = re.compile("^A: *([0-9]+)").match
	self.RE_TIME_NEW = re.compile("^A: *([0-9]+):([0-9]+)").match
        self.refresh = refresh
        self.stop_reason = 0 # 0 = ok, 1 = error


    def stopped(self):
        rc.post_event(Event(AUDIO_PLAY_END, self.stop_reason))

        
    def stdout_cb(self, line):
        if line.startswith("A:"):         # get current time
            m = self.RE_TIME_NEW(line)
            if m:
                self.stop_reason = 0
		timestrs = string.split(m.group(),":")
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
                self.refresh()
            self.elapsed = self.item.elapsed



    def stderr_cb(self, line):
        if line.startswith('Failed to open'):
            self.stop_reason = 1
