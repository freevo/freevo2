# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer plugin for audio
# -----------------------------------------------------------------------
# $Id$
#
# This contains plugin, control and childapp classes for using mplayer as
# audio player.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.44  2005/01/01 15:06:19  dischi
# add MPLAYER_RESAMPLE_AUDIO
#
# Revision 1.43  2004/10/17 02:45:19  outlyer
# Small changes...
#
# * Support AC3 raw audio
# * Sync mplayervbr with mplayer plugins...
#
# Note that recent mplayer versions do not have the bug in hr-mp3-seek that
# requires the 'seek -1' at the beginning of execution, but I'll leave it in
# here at least till it's in a released version of mplayer.
#
# Revision 1.42  2004/10/06 19:01:33  dischi
# use new childapp interface
#
# Revision 1.41  2004/09/29 18:58:17  dischi
# cleanup
#
# Revision 1.40  2004/08/01 10:42:23  dischi
# update to new application/eventhandler code
#
# Revision 1.39  2004/07/26 18:10:17  dischi
# move global event handling to eventhandler.py
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
import os
import re
import logging

# freevo imports
import config
import childapp
import plugin
from event import *

# the logging object
log = logging.getLogger('audio')

class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the audio player.
    """
    def __init__(self):
        # create the mplayer object
        plugin.Plugin.__init__(self)

        # register mplayer as the object to play audio
        plugin.register(MPlayer(), plugin.AUDIO_PLAYER, True)


class MPlayer:
    """
    The main class to control mplayer for audio playback
    """
    def __init__(self):
        self.name = 'mplayer'
        self.app  = None


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
        """
        get the correct demuxer for mp3 or ogg
        """
        DEMUXER_MP3 = 17
        DEMUXER_OGG = 18
        rest, extension     = os.path.splitext(filename)
        if extension.lower() == '.mp3':
            return "-demuxer " + str(DEMUXER_MP3)
        if extension.lower() == '.ogg':
            return "-demuxer " + str(DEMUXER_OGG)
        if extension.lower() == '.ac3':
            return "-ac hwac3 -rawaudio on:format=0x2000"
        else:
            return ''


    def play(self, item, playerGUI):
        """
        play a audioitem with mplayer
        """
        filename       = item.filename

        if filename and not os.path.isfile(filename):
            return _('%s\nnot found!') % Unicode(item.url)
            
        if not filename:
            filename = item.url
            
        # Build the MPlayer command
        mpl = '%s -slave %s' % ( config.MPLAYER_CMD, config.MPLAYER_ARGS_DEF )

        if not item.network_play:
            demux = ' %s ' % self.get_demuxer(filename)
        else:
            # Don't include demuxer for network files
            demux = ''

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
                  (mpl, config.MPLAYER_AO_DEV, demux, extra_opts)
        if command.find('-playlist') > 0:
            command = command.replace('-playlist', '')
        command = command.replace('\n', '').split(' ')

        if is_playlist:
            command.append('-playlist')

        if config.MPLAYER_RESAMPLE_AUDIO and item.info['samplerate'] and \
           item.info['samplerate'] < 40000:
            srate = max(41000, min(item.info['samplerate'] * 2, 48000))
            log.info('resample audio from %s to %s', item.info['samplerate'], srate)
            command += [ '-srate', str(srate) ]

        command.append(filename)

        for p in plugin.get('mplayer_audio'):
            command = p.play(command, self)
            
        self.item = item
        self.app  = MPlayerApp(command, playerGUI )

    
    def stop(self):
        """
        Stop mplayer
        """
        self.app.stop('quit\n')
        for p in plugin.get('mplayer_audio'):
            command = p.stop()


    def is_playing(self):
        return self.app.isAlive()


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        for p in plugin.get('mplayer_audio'):
            if p.eventhandler(event):
                return True

        if event == AUDIO_SEND_MPLAYER_CMD:
            self.app.write('%s\n' % event.arg)
            return True

        if event == PAUSE or event == PLAY:
            self.app.write('pause\n')
            return True

        if event == SEEK:
            self.app.write('seek %s\n' % event.arg)
            return True

        return False
            
            
# ======================================================================

class MPlayerApp( childapp.Instance ):
    """
    class controlling the in and output from the mplayer process
    """
    def __init__(self, app, player):
        self.item        = player.item
        self.player      = player
        self.elapsed     = 0
        self.stop_reason = ''
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
        childapp.Instance.__init__( self, app, stop_osd = 0,
                                    prio = config.MPLAYER_NICE )


    def stop_event(self):
        return Event(PLAY_END, self.stop_reason,
                     handler=self.player.eventhandler)

        
    def stdout_cb(self, line):
        if line.startswith("A:"):         # get current time
            m = self.RE_TIME_NEW(line)
            if m:
                self.stop_reason = ''
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
                    self.stop_reason  = ''
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
            self.stop_reason = line
        for p in self.stdout_plugins:
            p.stdout(line)
