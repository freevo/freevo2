# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mplayer.py - implementation of a TV function using MPlayer
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.48  2005/07/16 09:28:18  dischi
# fix strange indend
#
# Revision 1.47  2005/07/16 09:18:28  dischi
# add modified version from Henrik aka KaarPo
#
# Revision 1.46  2005/06/26 10:53:00  dischi
# use kaa.epg instead of pyepg
#
# Revision 1.45  2005/01/08 15:40:54  dischi
# remove TRUE, FALSE, DEBUG and HELPER
#
# Revision 1.44  2004/10/28 19:43:52  dischi
# remove broken imports
#
# Revision 1.43  2004/10/06 19:01:33  dischi
# use new childapp interface
#
# Revision 1.42  2004/08/05 17:27:16  dischi
# Major (unfinished) tv update:
# o the epg is now taken from kaa.epg in lib
# o all player should inherit from player.py
# o VideoGroups are replaced by channels.py
# o the recordserver plugins are in an extra dir
#
# Bugs:
# o The listing area in the tv guide is blank right now, some code
#   needs to be moved to gui but it's not done yet.
# o The only player working right now is xine with dvb
# o channels.py needs much work to support something else than dvb
# o recording looks broken, too
#
# Revision 1.41  2004/07/26 18:10:19  dischi
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


# Modified by Henrik aka KaarPo
# Handles ONLY ivtv at the moment...

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config
from kaa.notifier import Process

import time, os

import util

import event as em
import childapp # Handle child applications
import tv.ivtv as ivtv
import plugin
import notifier

from config.tvcards import IVTVCard
from tv.freq import get_frequency
import kaa.epg

from tv.player import TVPlayer

import logging
log = logging.getLogger('tv')

class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with mplayer.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # create the mplayer object and register it
        plugin.register(MPlayer(), plugin.TV, True)


class MPlayer(TVPlayer):

    def __init__(self):
        TVPlayer.__init__(self, 'mplayer')
        
    def rate(self, channel, device, uri):
        """
        for now, just handle ivtv
        """
        log.info('MPlayer.rate(): channel=[%s] device=[%s] uri=[%s]' %
        (channel, device, uri))
        if device.startswith('ivtv'):
            log.info('MPlayer.rate(): Returning 2: MPlayer handles this!')
            return 2

        return 0

    def tune(self, uri):
        log.info('MPlayer.play(): Tuning [%s] to chan [%s]' %
        (self.device.vdev, uri))
        import tv.v4l2
        v = tv.v4l2.Videodev(device=self.device.vdev)
        v.setchannel(uri)
        del v


    def play(self, channel, device, uri):

        log.info('MPlayer.play(): channel=[%s] device=[%s] uri=[%s]' %
        (channel, device, uri))

        self.channel = channel
        self.device = config.TV_CARDS[device]
        if not isinstance(self.device, IVTVCard):
            self.reason = 'Device %s is not of class IVTVCard' % device
            log.error('MPlayer.play(): ' + self.reason)
            return

        log.debug('MPlayer.play(): driver=[%s] vdev=[%s] chanlist=[%s]' %
        (self.device.driver, self.device.vdev, self.device.chanlist))

        self.tune(uri)

        command = 'mplayer -nolirc -slave '
        command += config.MPLAYER_ARGS_DEF + ' '
        if config.MPLAYER_ARGS.has_key('ivtv'):
            command += config.MPLAYER_ARGS['ivtv'] + ' '
        command += '-ao ' + config.MPLAYER_AO_DEV + ' '
        command += '-vo ' + config.MPLAYER_VO_DEV + \
             config.MPLAYER_VO_DEV_OPTS + ' '
        command += self.device.vdev

        log.info('mplayer.play(): Starting cmd=%s' % command)

        self.show()
        self.app = Process( command )

        return


    def stop(self, channel_change=0):
        """
        Stop mplayer
        """
        log.info('MPlayer.stop(): Stopping mplayer')
        TVPlayer.stop(self)
        if self.app:
            self.app.stop('quit\n')

    def osd_channel(self):
        # Display the channel info message
        #tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
        now = time.strftime('%H:%M')
        program = self.channel[time.time()]
        #msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
        msg = '%s [%s]: %s' % ( self.channel.title, now, program.title)
        cmd = 'osd_show_text "%s"\n' % msg
        self.app.write(cmd)
        return False # this removes the timer...

    def osd_updown(self):
        cmd = 'osd_show_text "Changing to [%s]"\n' % self.channel.title
        self.app.write(cmd)
        # wait three seconds for the tuner to tune in...
        cb = notifier.Callback( self.osd_channel )
        notifier.addTimer( 3000, cb )
        return False

    def eventhandler(self, event, menuw=None):
        """
        MPlayer event handler.
        If an event is not bound in this
        function it will be passed over to the items eventhandler.
        """

        s_event = '%s' % event
        log.debug('MPlayer.eventhandler(): Got event [%s]' % s_event)

        if event == em.STOP or event == em.PLAY_END:
            self.stop()
            em.PLAY_END.post()
            return True

        if event == em.TV_CHANNEL_UP:
            self.channel = kaa.epg.get_channel(self.channel, 1)
            uri = self.channel.get_uri(self.channel, self.device)
            self.tune(String(uri))
            self.osd_updown()
            return True

        if event == em.TV_CHANNEL_DOWN:
            self.channel = kaa.epg.get_channel(self.channel, -1)
            uri = self.channel.get_uri(self.channel, self.device)
            self.tune(String(uri))
            self.osd_updown()
            return True

        elif event == em.OSD_MESSAGE:
            cmd = 'osd_show_text "%s"\n' % event.arg
            self.app.write(cmd)
            return True


        # not changed by HKP yet...
        elif False and s_event.startswith('INPUT_'):
            if event == em.TV_CHANNEL_UP:
                nextchan = self.fc.getNextChannel()
            elif event == em.TV_CHANNEL_DOWN:
                nextchan = self.fc.getPrevChannel()
            else:
                chan = int( s_event[6] )
                nextchan = self.fc.getManChannel(chan)

            nextvg = self.fc.getVideoGroup(nextchan)

            if self.current_vg != nextvg:
                self.Stop(channel_change=1)
                self.Play('tv', nextchan)
                return True

            if self.mode == 'vcr':
                return True
            
            elif self.current_vg.group_type == 'dvb':
                self.Stop(channel_change=1)
                self.Play('tv', nextchan)
                return True

            elif self.current_vg.group_type == 'ivtv':
                self.fc.chanSet(nextchan)
                self.app.write('seek 999999 0\n')

            else:
                freq_khz = self.fc.chanSet(nextchan, app=self.app)
                new_freq = '%1.3f' % (freq_khz / 1000.0)
                self.app.write('tv_set_freq %s\n' % new_freq)

            self.current_vg = self.fc.getVideoGroup(self.fc.getChannel())

            # Display a channel changed message
            tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
            now = time.strftime('%H:%M')
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'osd_show_text "%s"\n' % msg
            self.app.write(cmd)
            return True

        elif event == em.TOGGLE_OSD:
            self.osd_channel()
            return True

        log.debug('MPlayer.eventhandler(): No handler for event [%s]' % s_event)
        return False

