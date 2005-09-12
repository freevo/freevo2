# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# ivtv.py - A plugin for recording from an ivtv card supported by the drivers
#           found at http://ivtv.sf.net.
#
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin requires the "encoder" utility that comes with the CK series of
# ivtv drivers found at http://67.18.1.101/~ckennedy/ivtv/.  You neeed at least
# version 0.2.0-rc2w from the stable branch or 0.3.1t from the unstable branch
# because we rely on a paramerter for passing the channel frequency as well as
# support for multiple cards and PAL settings that were introduced in those 
# versions.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
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

import os
import time
import config
from record.process import Recorder

from tv.freq import get_frequency
from config.tvcards import IVTVCard


class PluginInterface(Recorder):

    def __init__(self, device='ivtv0', rating=7):
        self.name = device
        self.device = config.TV_CARDS[device]
        Recorder.__init__(self)

        if not isinstance(self.device, IVTVCard):
            self.reason = 'Device %s is not of class IVTVCard'
            return

        self.suffix = '.mpeg'

        channels = []
        for c in self.device.channels:
            channels.append([c])
        self.channels = [ device, rating, channels ]
        # activate the plugin
        self.activate()


    def config(self):
        return [ ( 'IVTV_ENCODER', '/usr/local/bin/ivtv-encoder', 
                   'Location of the encoder utility.' ), ]

        
    def get_cmd(self, rec):
        channel = self.device.channels[rec.channel]
        frequency = get_frequency(channel, self.device.chanlist)

        if rec.url.startswith('file:'):
            filename = rec.url[5:]
        else:
            filename = rec.url

        duration = int(rec.stop + rec.stop_padding - time.time())

        try:
            vport = self.device.vdev[-1:]
        except:
            vport = 0

        cmd = [ config.IVTV_ENCODER, '-vport', String(vport) ]
        
        if self.device.codec.get('framerate'):
            cmd += [ '-frate', String(self.device.codec.get('framerate')), ]

        if self.device.codec.get('framespergop'):
            cmd += [ '-fpgop', String(self.device.codec.get('framespergop')), ]

        if self.device.codec.get('bitrate_mode'):
            cmd += [ '-bmode', String(self.device.codec.get('bitrate_mode')), ]

        if self.device.codec.get('bitrate'):
            cmd += [ '-brate', String(self.device.codec.get('bitrate')), ]

        if self.device.codec.get('bitrate_peak'):
            cmd += [ '-bpeak', String(self.device.codec.get('bitrate_peak')), ]

        if self.device.codec.get('audio_bitmask'):
            cmd += [ '-audio', String(self.device.codec.get('audio_bitmask')), ]

        if self.device.codec.get('dnr_mode'):
            cmd += [ '-dnrmode', String(self.device.codec.get('dnr_mode')), ]

        if self.device.codec.get('dnr_type'):
            cmd += [ '-dnrtype', String(self.device.codec.get('dnr_type')), ]

        if self.device.codec.get('dnr_spatial'):
            cmd += [ '-dnrspat', String(self.device.codec.get('dnr_spatial')), ]

        if self.device.codec.get('dnr_temporal'):
            cmd += [ '-dnrtemp', String(self.device.codec.get('dnr_temporal')), ]

        if self.device.codec.get('stream_type'):
            cmd += [ '-stream', String(self.device.codec.get('stream_type')), ]

        if self.device.codec.get('pulldown'):
            cmd += [ '-pulldown', String(self.device.codec.get('pulldown')), ]

        cmd += [ '-input',    String(self.device.input),
                 '-f',        String(frequency), 
                 String(duration), filename ]

        return cmd

    
    def get_channel_list(self):
        return [ self.channels ]

