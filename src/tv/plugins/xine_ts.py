# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xine.py - xine tv plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import time
import os
import copy
import logging
import mbus

# kaa imports
import kaa.epg

# freevo imports
import config
import plugin
import mcomm

from event import *
from application import ChildApp
from config.tvcards import DVBCard, IVTVCard

# get logging object
log = logging.getLogger('tv')

class PluginInterface(plugin.Plugin):
    """
    Xine plugin for tv. The plugin is beta and only works with dvb.

    Your channel list must contain the identifier from the xine
    channels.conf as frequence
    """
    def __init__(self):
        # detect xine and it's version
        config.detect('xine')

        try:
            config.XINE_COMMAND
        except:
            self.reason = '\'XINE_COMMAND\' not defined'
            return

        if config.XINE_VERSION < '0.99.1' and \
               config.XINE_VERSION < '0.9.23':
            self.reason = "'xine' version too old"
            return

        if config.FBXINE_VERSION < '0.99.1' and \
               config.FBXINE_VERSION < '0.9.23':
            self.reason = "'fbxine' version too old"
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
        elif config.XINE_COMMAND.find('df_xine') >= 0:
            type = 'df'
        else:
            type = 'X'

        plugin.Plugin.__init__(self)

        # register xine as the object to play
        plugin.register(Xine(type), plugin.TV, True)



class Xine(ChildApp):
    """
    the main class to control xine
    """
    def __init__(self, type):
        ChildApp.__init__(self, 'xine', 'video', True, False, True)
        self.name = 'xine'
        self.xine_type = type
        self.id = None

    def rate(self, channel, device, uri):
        """
        FIXME: remove this function, every player can play everything
        through the recordserver
        """
        return 2

    
    def play(self, channel, device, uri):
        """
        Play with xine
        """
        self.channel = channel
        self.device  = config.TV_CARDS[device]
        self.item    = uri

        # FIMXE: dynamic url handling
        destip = '224.224.244.200:12345'

        # request record on server
        rs = mcomm.find('recordserver', 0)
        if not rs:
            print 'no rs'
            # FIXME: handle error
            return
                
        print 'start'
        rs.call('watch.start', self.__receive_url, channel, destip)

        self.show()

        return None
    

    def __receive_url(self, result):
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            self.stop()
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            self.stop()
            return

        self.id, url = result.arguments
        # create command
        command = config.XINE_COMMAND.split(' ') + \
                  [ '--stdctl', '-V', config.XINE_VO_DEV, '-A',
                    config.XINE_AO_DEV ] + config.XINE_ARGS_DEF.split(' ')

        if config.XINE_COMMAND.startswith(config.CONF.xine) and \
               config.XINE_USE_LIRC:
            command.append('--no-lirc')

        if config.XINE_COMMAND.startswith(config.CONF.fbxine) and \
               config.FBXINE_USE_LIRC:
            command.append('--no-lirc')

        command.append('%s#demux:mpeg_pes' % url)

        # start child
        log.info('Xine.play(): Starting cmd=%s' % command)
        self.child_start(command, config.MPLAYER_NICE, 'quit\n')

        log.info('live recording started')


    def __stop_done(self, result):
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return
        return

    
    def eventhandler(self, event):
        """
        Eventhandler for xine control.
        """
        if event == PLAY_END:
            # stop recordserver live recording
            print 'x'
            rs = mcomm.find('recordserver', 0)
            if rs and self.id != None:
                print 'stop'
                rs.call('watch.stop', self.__stop_done, self.id)
                self.id = None
                
        ChildApp.eventhandler(self, event)

        if not self.has_child():
            return True

        if event == PLAY_END:
            return True

        if event == STOP:
            self.stop()
            return True

        if event == TOGGLE_OSD:
            self.child_stdin('PartMenu\n')
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            self.child_stdin('ToggleInterleave\n')
            return True

        # nothing found
        return False
