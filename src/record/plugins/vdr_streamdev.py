# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# vdr_streamdev.py - A plugin for recording from VDR using the streamdev-server
#                    plugin.
#
# -----------------------------------------------------------------------------
# $Id$
#
# VDR:  http://www.cadsoft.de/vdr/
# Streamdev:  http://www.magoa.net/linux/index.php?view=streamdev-unstable
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


class PluginInterface(Recorder):

    def __init__(self, device='dvb0', rating=7):
        self.name = device
        self.device = config.TV_CARDS[device]
        recorder.__init__(self)

        self.suffix = '.mpeg'

        channels = []
        for c in self.device.channels:
            channels.append([c])
        self.channels = [ device, rating, channels ]
        # activate the plugin
        self.activate()


    def config(self):
        return [ ( 'VDR_STREAMDEV_URL', 'http://localhost:3000/PS/', 
                   'Location of the streamdev server.' ), ]

        
    def get_cmd(self, rec):
        channel = self.device.channels[rec.channel]

        if rec.url.startswith('file:'):
            filename = rec.url[5:]
        else:
            filename = rec.url

        duration = int(rec.stop + rec.stop_padding - time.time())

        return [ '/usr/bin/env', 'python',
                 os.path.join(os.environ['FREEVO_HELPERS'], 'url_record.py'),
                 config.VDR_STREAMDEV_URL + String(channel),
                 filename, 
                 String(duration) ]

    
    def get_channel_list(self):
        return [ self.channels ]

