# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xmms.py - the Freevo XMMS plugin for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo: make audio cd's work
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/07/26 18:10:17  dischi
# move global event handling to eventhandler.py
#
# Revision 1.4  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.3  2004/01/31 12:39:47  dischi
# delete unused audio variables
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


# regular python imports
import os
import re
import sys
import time
import thread

# pyxmms import
try:
    import xmms
except ImportError:
    print
    print
    print 'pyxmms is not (properly?) installed!'
    print
    sys.exit(1)

# freevo imports
import config     # Configuration handler. reads config file.
import childapp   # Handle child applications
import plugin
from event import *
import util


class PluginInterface(plugin.Plugin):
    """
    XMMS plugin for the audio player. Use xmms to play audio
    files. by default it will only play mp3, mod, ogg and wav. It will
    also play cdroms too. You can extend the number of file extensions
    by setting a custom FXMMS_SUFFIX variable. The variable was introduced
    since freevo uses mplayer by default which supports many more
    sound formats.
    I have also added a variable (FXMMS_NETRADIO) which allows you to
    turn off xmms for netradio. I have had limited succes with netradio
    with xmms so i turn it off but other people wanted it.
    I also have a variable for where xmms is. I have set it to the Gentoo
    default of /usr/bin/xmms.
    There are two ways to get this plugin to work. The first is to remove the
    audio.mplayer plugin and then activate this plugin. This is not reccomended
    since xmms supports many less formats than mplayer. but here is how to 
    activate it in local_conf.py:
    plugin.remove('audio.mplayer')
    plugin.activate('audio.fxmms')
    The second better option is to set fxmms to your AUDIO_PREFERED_PLAYER and
    then activate the plugin in local_conf.py:
    plugin.activate('audio.fxmms')
    AUDIO_PREFERED_PLAYER = 'fxmms'
    
    """
    def __init__(self):
        # create the plugin object
        plugin.Plugin.__init__(self)

        # register xmms as the object to play audio
        plugin.register(FXMMS(), plugin.AUDIO_PLAYER, True)

    def config(self):
        return [ ('FXMMS_CMD', '/usr/bin/xmms', 'location of xmms.'),
	         ('FXMMS_NETRADIO', 1, 'Whether to use xmms for netradio'),
		 ('FXMMS_SUFFIX', ['mp3','wav','ogg', 'mod'], 'xmms suffixes to play')]


class FXMMS:
    """
    the main class to control xmms
    """
    
    def __init__(self):
        self.name     = 'fxmms'
        self.app_mode = 'audio'
        self.app      = None
        self.is_alive = False  #flag for osd update thread
        self.idle     = 0      #timer for osd update thread
        self.last_event = PLAY_END #keep track of last event for osd thread

    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.url and item.url.startswith('radio://'):
            return 0
        if item.url and item.url.startswith('mms://'):
            return 0
        if item.url and item.url.startswith('rtsp://'):
            return 0
	if item.url and not config.FXMMS_NETRADIO and item.url.startswith('https://'):
            return 0
	if item.url and not config.FXMMS_NETRADIO and item.url.startswith('http://'):
            return 0
	if item.filename and not util.match_suffix(item.filename, config.FXMMS_SUFFIX):
	    return 0
        return 2

    def play(self, item, playerGUI):
        """
        play an audioitem with xmms
        """
        if item.url:
            filename = item.url
        else:
            filename = item.filename
	    
        self.playerGUI = playerGUI
        
        # Do we care if the file streamed over the network?

        if not os.path.isfile(filename) and filename.find('://') == -1:
            return _('%s\nnot found!') % filename

        # need to convert filename for cds to /mnt/cdrom/Track??.cda
	# the /mnt/cdrom is supposed to be where you mount your cd
        if filename.startswith('cdda://'):
	    filename = '%s/Track%.2d.cda' % (item.parent.media.mountdir, int(item.url[7:])) 
            
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item

        #reset idle timeout so update thread doesn't kill xmms after I start a song
        self.idle = 0
        if not xmms.is_running():
            xmms.enqueue_and_play_launch_if_session_not_started([(filename)],xmms_prg=config.FXMMS_CMD)
            time.sleep(0.2)
	    self.hide_windows()
            # turn off repeat mode
            if (xmms.is_repeat()):
                xmms.toggle_repeat()
        else:
            xmms.playlist_clear()
            xmms.enqueue_and_play([(filename)])
        
        # restart OSD update thread if neccessary
        if (not self.is_alive):
            thread.start_new_thread(self.__update_thread, ())
        
        return None 

    def hide_windows(self):
        #hide windows
        xmms.main_win_toggle(0)
        xmms.pl_win_toggle(0)
        xmms.eq_win_toggle(0)
        xmms.toggle_aot(0)

    def stop(self):
        """
        Stop xmms
        """
        xmms.stop()
        

    def is_playing(self):
        return xmms.is_playing()

    def __update_thread(self):
        """
        OSD update thread for Xmms
        """
        self.is_alive = True
        self.idle = 0
        
        while self.is_alive:
	    if xmms.is_main_win():
	        self.hide_windows()
        
            if self.is_playing():
                
                # update OSD while playing
                while self.is_playing():
                    self.refresh()
                    time.sleep(0.3)  # is this too short???
                
                # trigger end of song event if song ended naturally
                if not (self.last_event in (PLAYLIST_NEXT, STOP)):
                    self.eventhandler(PLAY_END)
                
                # reset idle time out
                self.idle = 0

            elif (self.idle > 2):
                # let thread expire if idle more than 2 sec
                self.is_alive=False

            else:
                # increment idle timer
                time.sleep(0.5)
                self.idle+=.5

        xmms.quit()

    def refresh(self):
        curtime = xmms.get_output_time()
        curtime = int(curtime / 1000)
        self.elapsed = self.item.elapsed = curtime
        self.playerGUI.refresh()

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xmms. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        # save this event so update_thread doesn't get fooled
        self.last_event = event

        if event == PLAY_END and event.arg:
            self.stop()
            if self.playerGUI.try_next_player():
                return True
        
        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)
            
        elif event == PAUSE or event == PLAY:
            xmms.pause()
            return True
            
        elif event == SEEK:
            curtime = xmms.get_output_time()
            nexttime = curtime + (event.arg * 1000)
            
            # trim down seek time if it past end of the song
            while nexttime > xmms.get_playlist_time(xmms.get_playlist_pos()):
                event.arg/=2
                nexttime = curtime + (event.arg * 1000)
            xmms.jump_to_time(nexttime)
            return True
            
        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
