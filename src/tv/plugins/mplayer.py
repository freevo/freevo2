# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayer.py - mplayer tv plugin
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
import logging

# kaa imports
import kaa.notifier
import kaa.epg

# freevo imports
import config
import plugin

from application import mplayer
from config.tvcards import IVTVCard, DVBCard
from event import *

import tv.ivtv as ivtv
import tv.v4l2

# get logging object
log = logging.getLogger('tv')


class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with mplayer.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # create the mplayer object and register it
        plugin.register(MPlayer(), plugin.TV, True)


class MPlayer(mplayer.Application):

    def __init__(self):
        mplayer.Application.__init__(self, 'video', True)

        
    def rate(self, channel, device, uri):
        """
        For now, just handle ivtv and dvb
        """
        if device.startswith('ivtv'):
            return 2
        if device.startswith('dvb'):
            return 2
        return 0


    def tune(self, uri):
        log.info('Tuning [%s] to chan [%s]' % (self.device.vdev, uri))
        v = tv.v4l2.Videodev(device=self.device.vdev)
        v.setchannel(uri)
        del v


    def play(self, channel, device, uri):
        self.channel = channel
        self.device = config.TV_CARDS[device]

        # Build the MPlayer command
        command = [ config.MPLAYER_CMD ] + \
                  config.MPLAYER_ARGS_DEF.split(' ') + \
                  [ '-slave', '-ao'] + \
                  config.MPLAYER_AO_DEV.split(' ')

        if isinstance(self.device, IVTVCard):
            self.tune(uri)

            if config.MPLAYER_ARGS.has_key('ivtv'):
                command += config.MPLAYER_ARGS['ivtv'].split(' ')
            command += [ self.device.vdev ]

        if isinstance(self.device, DVBCard):
            if config.MPLAYER_ARGS.has_key('dvb'):
                command += config.MPLAYER_ARGS['dvb'].split(' ')
            command += [ 'dvb://' + uri ]

        log.info('mplayer.play(): Starting cmd=%s' % command)

        self.show()
        mplayer.Application.play(self, command)


    def osd_channel(self):
        # Display the channel info message
        #tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
        now = time.strftime('%H:%M')
        program = self.channel[time.time()]
        #msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
        msg = '%s [%s]: %s' % ( self.channel.title, now, program.title)
        cmd = 'osd_show_text "%s"\n' % msg
        self.send_command(cmd)
        return False # this removes the timer...


    def osd_updown(self):
        cmd = 'osd_show_text "Changing to [%s]"\n' % self.channel.title
        self.send_command(cmd)
        # wait three seconds for the tuner to tune in...
        cb = kaa.notifier.OneShotTimer(self.osd_channel).start(3)
        return False


    def eventhandler(self, event):
        """
        eventhandler for mplayer control.
        """
        mplayer.Application.eventhandler(self, event)

        if event == STOP:
            self.stop()
            return True
        
        if event == PLAY_END:
            return True

        if not self.has_child():
            return True

        if event == TV_CHANNEL_UP:
            if isinstance(self.device, IVTVCard):
                self.channel = kaa.epg.get_channel(self.channel, 1)
                uri = self.channel.get_uri(self.channel, self.device)
                self.tune(String(uri))
                self.osd_updown()
            else:
                self.send_command('osd_show_text unable to switch channel\n')
            return True

        if event == TV_CHANNEL_DOWN:
            if isinstance(self.device, IVTVCard):
                self.channel = kaa.epg.get_channel(self.channel, -1)
                uri = self.channel.get_uri(self.channel, self.device)
                self.tune(String(uri))
                self.osd_updown()
            else:
                self.send_command('osd_show_text unable to switch channel\n')
            return True

        elif event == OSD_MESSAGE:
            self.send_command('osd_show_text "%s"\n' % event.arg)
            return True

        elif event == TOGGLE_OSD:
            self.osd_channel()
            return True

        return False
