# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for tv
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# This plugin is beta and only working with dvb
#
# Todo:        
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/07/26 18:10:19  dischi
# move global event handling to eventhandler.py
#
# Revision 1.3  2004/07/25 19:47:40  dischi
# use application and not rc.app
#
# Revision 1.2  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.1  2004/06/20 12:01:19  dischi
# basic xine dvb plugin
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


import time, os, re
import copy

import config     # Configuration handler. reads config file.
import childapp   # Handle child applications
import rc         # The RemoteControl class.
import util
import osd
import eventhandler

from tv.channels import FreevoChannels

from event import *
import plugin


class PluginInterface(plugin.Plugin):
    """
    Xine plugin for tv. The plugin is beta and only works with dvb.

    Your channel list must contain the identifier from the xine channels.conf
    as frequence, e.g.

    TV_CHANNELS = [
        ( 'ard.de', 'ARD', 'Das Erste RB' ), 
        ( 'zdf.de', 'ZDF', 'ZDF' ),
        ( 'ndr.de', 'NDR', 'NDR RB' ), 
        ( 'rtl.de', 'RTL', 'RTL Television' ), 
        ( 'sat1.de', 'SAT.1', 'SAT.1' ), 
        ( 'rtl2.de', 'RTL 2', 'RTL2' ), 
        ( 'prosieben.de', 'PRO 7', 'ProSieben' ), 
        ( 'kabel1.de', 'KABEL 1', 'KABEL1' ), 
        ( 'vox.de', 'VOX', 'VOX' ), 
        ( 'n24.de', 'N24', 'N24' ), 
        ( 'arte-tv.com', 'ARTE', 'arte' ), 
        ( 'C3sat.de', '3SAT', 'Info/3sat' ), 
        ( 'superrtl.de', 'Super RTL', 'Super RTL' ), 
        ( 'kika.de', 'Kika', 'Doku/KiKa' ) ]
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        try:
            config.XINE_COMMAND
        except:
            print String(_( 'ERROR' )) + ': ' + \
                  String(_("'XINE_COMMAND' not defined, plugin 'xine' deactivated.\n" \
                           'please check the xine section in freevo_config.py' ))
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
        else:
            type = 'X'

        if not hasattr(config, 'XINE_VERSION'):
            config.XINE_VERSION = 0
            for data in util.popen3.stdout('%s --version' % config.XINE_COMMAND):
                m = re.match('^.* v?([0-9])\.([0-9]+)\.([0-9]*).*', data)
                if m:
                    config.XINE_VERSION = int('%02d%02d%02d' % (int(m.group(1)),
                                                                  int(m.group(2)),
                                                                  int(m.group(3))))
                    if data.find('cvs') >= 0:
                        config.XINE_VERSION += 1

            _debug_('detect xine version %s' % config.XINE_VERSION)
            
        if config.XINE_VERSION < 922:
            print String(_( 'ERROR' )) + ': ' + \
                  String(_( "'xine-ui' version too old, plugin 'xine' deactivated" ))
            print String(_( 'You need software %s' )) % 'xine-ui > 0.9.21'
            return
            
        # register xine as the object to play
        plugin.register(Xine(type, config.XINE_VERSION), plugin.TV, False)



class Xine:
    """
    the main class to control xine
    """
    def __init__(self, type, version):
        self.name      = 'xine'

        self.app_mode  = 'tv'
        self.xine_type = type
        self.version   = version
        self.app       = None

        self.fc = FreevoChannels()

        self.command = [ '--prio=%s' % config.MPLAYER_NICE ] + \
                       config.XINE_COMMAND.split(' ') + \
                       [ '--stdctl', '-V', config.XINE_VO_DEV,
                         '-A', config.XINE_AO_DEV ] + \
                       config.XINE_ARGS_DEF.split(' ')


    def Play(self, mode, tuner_channel=None):
        """
        play with xine
        """
        if not tuner_channel:
            tuner_channel = self.fc.getChannel()

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        command = copy.copy(self.command)

        if not rc.PYLIRC and '--no-lirc' in command:
            command.remove('--no-lirc')

        command.append('dvb://' + tuner_channel)
            
        _debug_('Xine.play(): Starting cmd=%s' % command)

        eventhandler.append(self)

        self.app = childapp.ChildApp2(command)
        return None
    

    def stop(self, channel_change=0):
        """
        Stop xine
        """
        if self.app:
            self.app.stop('quit\n')
            eventhandler.remove(self)

            if not channel_change:
                pass
            

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if event in ( PLAY_END, USER_END, STOP ):
            self.stop()
            eventhandler.post(PLAY_END)
            return True

        if event == PAUSE or event == PLAY:
            self.app.write('pause\n')
            return True

        elif event in [ TV_CHANNEL_UP, TV_CHANNEL_DOWN] or str(event).startswith('INPUT_'):
            if event == TV_CHANNEL_UP:
                nextchan = self.fc.getNextChannel()
            elif event == TV_CHANNEL_DOWN:
                nextchan = self.fc.getPrevChannel()
            else:
                nextchan = self.fc.getManChannel(int(event.arg))

            self.stop(channel_change=1)
            self.fc.chanSet(nextchan)
            self.Play('tv', nextchan)
            return True

        if event == TOGGLE_OSD:
            self.app.write('PartMenu\n')
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            self.app.write('ToggleInterleave\n')
            return True

        # nothing found
        return False
