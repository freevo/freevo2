# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes: Use xine (or better fbxine) to play audio files. This requires
#        xine-ui > 0.9.22 (when writing this plugin this means cvs)
#
# Todo:
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.18  2004/09/29 18:47:36  dischi
# fix xine lirc handling
#
# Revision 1.17  2004/08/01 10:42:23  dischi
# update to new application/eventhandler code
#
# Revision 1.16  2004/07/10 12:33:38  dischi
# header cleanup
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


import re

import config     # Configuration handler. reads config file.
import childapp   # Handle child applications
import rc         # The RemoteControl class.
import util.popen3
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
            print String(_( 'ERROR' )) + ': ' + \
                  String(_( "'fbxine' not found, plugin 'xine' deactivated" ))
            return

        if not hasattr(config, 'FBXINE_VERSION'):
            config.FBXINE_VERSION = 0
            for data in util.popen3.stdout('%s --version' % config.CONF.fbxine):
                m = re.match('^.* v?([0-9])\.([0-9]+)\.([0-9]*).*', data)
                if m:
                    config.FBXINE_VERSION = int('%02d%02d%02d' % (int(m.group(1)),
                                                                  int(m.group(2)),
                                                                  int(m.group(3))))
                    if data.find('cvs') >= 0:
                        config.FBXINE_VERSION += 1

            _debug_('detect fbxine version %s' % config.FBXINE_VERSION)

        
        if config.FBXINE_VERSION < 923:
            print String(_( 'ERROR' )) + ': ' + \
                  String(_( "'fbxine' version too old, plugin 'xine' deactivated" ))
            print String(_( 'You need software %s' )) % 'xine-ui > 0.9.22'
            return
            
        # register xine as the object to play
        plugin.register(Xine(), plugin.AUDIO_PLAYER, True)


# ======================================================================

class Xine:
    """
    the main class to control xine
    """
    
    def __init__(self):
        self.name         = 'xine'
        self.app_mode     = 'audio'
        self.app          = None
        self.command = '%s -V none -A %s --stdctl' % (config.CONF.fbxine, config.XINE_AO_DEV)
        if conf.FBXINE_USE_LIRC:
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
            add_args.append('cfg:/input.cdda_device:%s' % item.media.devicename)
            
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

class XineApp(childapp.ChildApp2):
    """
    class controlling the in and output from the xine process
    """

    def __init__(self, app, player):
        self.item        = player.item
        self.player      = player
        self.elapsed     = 0
        self.stop_reason = 0 # 0 = ok, 1 = error
        childapp.ChildApp2.__init__(self, app, stop_osd=0)


    def stop_event(self):
        return Event(PLAY_END, self.stop_reason, handler=self.player.eventhandler)


    def stdout_cb(self, line):
        if line.startswith("time: "):         # get current time
            self.item.elapsed = int(line[6:])

            if self.item.elapsed != self.elapsed:
                self.player.refresh()
            self.elapsed = self.item.elapsed


    def stderr_cb(self, line):
        if line.startswith('Unable to open MRL'):
            self.stop_reason = 1
            
