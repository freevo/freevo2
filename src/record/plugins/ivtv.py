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


    def config(self):
        return [ ( 'IVTV_ENCODER', '/usr/local/bin/encoder', 
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

        return [ config.IVTV_ENCODER, 
                 '-vport',    String(vport),
                 '-frate',    String(self.device.framerate),
                 '-fpgop',    String(self.device.framespergop),
                 '-bmode',    String(self.device.bitrate_mode),
                 '-brate',    String(self.device.bitrate),
                 '-bpeak',    String(self.device.bitrate_peak),
                 '-audio',    String(self.device.audio_bitmask),
                 '-dnrmode',  String(self.device.dnr_mode),
                 '-dnrtype',  String(self.device.dnr_type),
                 '-dnrspat',  String(self.device.dnr_spatial),
                 '-dnrtemp',  String(self.device.dnr_temporal),
                 '-stream',   String(self.device.stream_type),
                 '-pulldown', String(self.device.pulldown),
                 '-input',    String(self.device.input),
                 '-f',        String(frequency), 
                 String(duration), 
                 filename ]

    
    def get_channel_list(self):
        return [ self.channels ]

