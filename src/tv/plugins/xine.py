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
# Revision 1.12  2005/06/26 10:53:00  dischi
# use kaa.epg instead of pyepg
#
# Revision 1.11  2004/12/28 18:07:34  dischi
# fix for missing pyvdr
#
# Revision 1.10  2004/12/28 00:35:19  rshortt
# Further vdr-xine for DVB and df_xine tweaks, still planning on smoothing things
# over and also add ivtv (input_pvr) support.
#
# Revision 1.9  2004/11/20 18:23:04  dischi
# use python logger module for debug
#
# Revision 1.8  2004/10/06 19:13:42  dischi
# use config auto detection for xine version
#
# Revision 1.7  2004/10/06 19:01:33  dischi
# use new childapp interface
#
# Revision 1.6  2004/09/15 20:45:13  dischi
# fix to stop event
#
# Revision 1.5  2004/08/05 17:27:17  dischi
# Major (unfinished) tv update:
# o the epg is now taken from kaa.epg in lib
# o all player should inherit from player.py
# o VideoGroups are replaced by channels.py
# o the recordserver plugins are in an extra dir
#
# Bugs:
# o The listing area in the tv guide is blank right now, some code
#   needs to be moved to gui but it's not done yet.
# o The only player working right now is xine with dvb
# o channels.py needs much work to support something else than dvb
# o recording looks broken, too
#
# Revision 1.4  2004/07/26 18:10:19  dischi
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


import time, os, re
import copy

import config     # Configuration handler. reads config file.
from util.popen import Process
import util
import plugin

from event import *
from tv.player import TVPlayer

import kaa.epg
if config.XINE_USE_VDR:
    from vdr.vdr import VDR

import logging
log = logging.getLogger('tv')

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
        try:
            config.XINE_COMMAND
        except:
            self.reason = '\'XINE_COMMAND\' not defined'
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
            if config.FBXINE_VERSION < '0.99.1' and \
                   config.FBXINE_VERSION < '0.9.23':
                self.reason = "'fbxine' version too old"
                return
        elif config.XINE_COMMAND.find('df_xine') >= 0:
            type = 'df'
        else:
            type = 'X'
            if config.XINE_VERSION < '0.99.1' and \
                   config.XINE_VERSION < '0.9.23':
                self.reason = "'xine' version too old"
                return

        plugin.Plugin.__init__(self)

        # register xine as the object to play
        plugin.register(Xine(type, config.XINE_VERSION), plugin.TV, True)



class Xine(TVPlayer):
    """
    the main class to control xine
    """
    def __init__(self, type, version):
        TVPlayer.__init__(self, 'xine')
        self.xine_type = type
        self.version   = version
        self.app       = None
        self.device    = None
        self.command = config.XINE_COMMAND.split(' ') + \
                       [ '--stdctl', '-V', config.XINE_VO_DEV,
                         '-A', config.XINE_AO_DEV ] + \
                       config.XINE_ARGS_DEF.split(' ')

        if config.XINE_USE_VDR:
            self.vdr = VDR(host=config.VDR_HOST, 
                           port=config.VDR_PORT, 
                           videopath=config.VDR_DIR, 
                           channelsfile=config.VDR_CHANNELS, 
                           epgfile=config.VDR_EPG,
                           close_connection=1)
            self.vdr.getsvdrp()


    def rate(self, channel, device, uri):
        """
        xine can only play dvb
        """
        log.debug('xine tv asked to rate: %s %s %s' % (channel, device, uri))
        if device.startswith('dvb'):
            return 2
        elif device.startswith('ivtv'):
            return 2

        return 0

    
    def play(self, channel, device, uri):
        """
        play with xine
        """
        self.channel = channel
        self.device  = device

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        command = copy.copy(self.command)

        if config.XINE_COMMAND.startswith(config.CONF.xine) and \
               config.XINE_USE_LIRC:
            command.append('--no-lirc')

        if config.XINE_COMMAND.startswith(config.CONF.fbxine) and \
               config.FBXINE_USE_LIRC:
            command.append('--no-lirc')

        if device.startswith('dvb'):
            if config.XINE_USE_VDR:
                command.append('vdr://tmp/vdr-xine/stream#demux:mpeg_pes')
                log.debug('want to play %s' % uri)
                self.vdr.svdrp.chan(String(uri))
            else:
                command.append('dvb://' + uri)
        elif device.startswith('ivtv'):
            command.append('pvr://' + uri)
            
        log.info('Xine.play(): Starting cmd=%s' % command)

        self.show()
        self.app = Process( command )
    

    def stop(self, channel_change=0):
        """
        Stop xine
        """
        TVPlayer.stop(self)
        if self.app:
            self.app.stop('quit\n')
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if TVPlayer.eventhandler(self, event, menuw):
            return True
        
        # OSD_MESSAGE to vdr-xine is hanging VDR on me, investigating
        #if event == OSD_MESSAGE:
        #    if config.XINE_USE_VDR:
        #        self.vdr.svdrp.osd_message(String(event.arg))
        #        return True
        
        if event == PAUSE or event == PLAY:
            self.app.write('pause\n')
            return True

        if event == TOGGLE_OSD:
            self.app.write('PartMenu\n')
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            self.app.write('ToggleInterleave\n')
            return True

        if event == TV_CHANNEL_UP:
            if config.XINE_USE_VDR:
                self.channel = kaa.epg.get_channel(self.channel, 1)
                uri = self.channel.get_uri(self.channel, self.device)
                self.vdr.svdrp.chan(String(uri))
                return True

        if event == TV_CHANNEL_DOWN:
            if config.XINE_USE_VDR:
                self.channel = kaa.epg.get_channel(self.channel, -1)
                uri = self.channel.get_uri(self.channel, self.device)
                self.vdr.svdrp.chan(String(uri))
                return True

        if event in INPUT_ALL_NUMBERS:
            digit = str(event).split('_')[1]
            self.vdr.svdrp.hitk(digit)
            log.debug('xine: user pressed digit %s' % digit)

        # nothing found
        return False
