#if 0 /*
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes: Use xine (or better fbxine) to play audio files. This requires
#        xine-ui > 0.9.22 (when writing this plugin this means cvs)
#
# Todo:  test it
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/11/22 15:30:55  dischi
# support more than one player
#
# Revision 1.8  2003/11/08 13:20:26  dischi
# support for AUDIOCD plugin type
#
# Revision 1.7  2003/11/08 10:00:59  dischi
# fix cd playback
#
# Revision 1.6  2003/10/21 21:17:41  gsbarbieri
# Some more i18n improvements.
#
# Revision 1.5  2003/09/19 22:09:16  dischi
# use new childapp thread function
#
# Revision 1.4  2003/09/01 19:46:02  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.3  2003/08/26 20:24:07  outlyer
# Apparently some files have spaces in them... D'oh :)
#
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
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
import signal
import popen2, re

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.

from event import *
import plugin


class PluginInterface(plugin.Plugin):
    """
    Xine plugin for the video player.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        try:
            config.CONF.fbxine
        except:
            print _( 'ERROR' ) + ': ' + \
                  _( "'fbxine' not found, plugin 'xine' deactivated" )
            return

        xine_version = 0
        xine_cvs     = 0
        
        child = popen2.Popen3('%s --version' % config.CONF.fbxine, 1, 100)
        while(1):
            data = child.fromchild.readline()
            if not data:
                break
            m = re.match('^.* v?([0-9])\.([0-9]+)\.([0-9]*).*', data)
            if m:
                if data.find('cvs') >= 0:
                    xine_cvs = 1
                xine_version =int('%02d%02d%02d' % (int(m.group(1)), int(m.group(2)),
                                                    int(m.group(3))))

        child.wait()

        if xine_cvs:
            xine_version += 1
            
        if xine_version < 923:
            print _( 'ERROR' ) + ': ' + \
                  _( "'fbxine' version too old, plugin 'xine' deactivated" )
            print _( 'You need software %s' ) % 'xine-ui > 0.9.22'
            return
            
        # create the xine object
        xine = util.SynchronizedObject(Xine(xine_version))

        # register it as the object to play
        plugin.register(xine, plugin.AUDIO_PLAYER, True)


# ======================================================================

class Xine:
    """
    the main class to control xine
    """
    
    def __init__(self, version):
        self.name = 'xine'
        self.thread = childapp.ChildThread()
        self.mode = None
        self.xine_version = version
        self.app_mode = 'audio'

        self.command = '%s -V none -A %s --stdctl' % (config.CONF.fbxine, config.XINE_AO_DEV)
        if rc.PYLIRC:
            self.command = '%s --no-lirc' % self.command

        
    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        return 2


    def play(self, item, playerGUI):
        """
        play an audio file with xine
        """

        self.item      = item
        self.playerGUI = playerGUI
        add_args       = ''
        
        if item.url:
            filename = item.url
        else:
            filename = item.filename

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        if filename.startswith('cdda://'):
            filename = filename.replace('//', '/')
            add_args += ' cfg:/input.cdda_device:%s' % item.media.devicename
            
        command = '%s %s "%s"' % (self.command, add_args, filename)
        _debug_('Xine.play(): Starting thread, cmd=%s' % command)

        self.thread.start(XineApp, (command, item, self.refresh))
    

    def is_playing(self):
        return self.thread.mode != 'idle'


    def refresh(self):
        self.playerGUI.refresh()
        

    def stop(self):
        """
        Stop xine and set thread to idle
        """
        self.thread.stop('quit\n')
            

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if event == AUDIO_PLAY_END:
            if event.arg:
                self.stop()
                if self.playerGUI.try_next_player():
                    return True
            event = PLAY_END

        if event in ( PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        if event == PAUSE or event == PLAY:
            self.thread.app.write('pause\n')
            return True

        if event == STOP:
            self.playerGUI.stop()
            return self.item.eventhandler(event)

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
            self.thread.app.write('%s%s\n' % (action, pos))
            return True

        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)

        

# ======================================================================

class XineApp(childapp.ChildApp):
    """
    class controlling the in and output from the xine process
    """

    def __init__(self, (app, item, refresh)):
        self.item = item
        childapp.ChildApp.__init__(self, app)
        self.elapsed = 0
        self.refresh = refresh
        self.stop_reason = 0 # 0 = ok, 1 = error

    def stopped(self):
        rc.post_event(Event(AUDIO_PLAY_END, self.stop_reason))


    def stdout_cb(self, line):
        if line.startswith("time: "):         # get current time
            self.item.elapsed = int(line[6:])

            if self.item.elapsed != self.elapsed:
                self.refresh()
            self.elapsed = self.item.elapsed


    def stderr_cb(self, line):
        if line.startswith('Unable to open MRL'):
            self.stop_reason = 1
            
