# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# dvb.py - plugin for recording one program for dvb
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin will use mplayer with the dumpstream option for recording the
# program. For DVB-T it can also use tzap for recording.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
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
import os
import logging
import time

# freevo imports
import config

# utils
from util.fileops import find_file_in_path
from util.popen import Process
from util.callback import *

# basic recorder
from record.process import Recorder

# get logging object
log = logging.getLogger('record')

class PluginInterface(Recorder):
    """
    Plugin for dvb recording
    """
    def __init__(self, device='dvb0', rating=0):
        self.name = device
        self.device = config.TV_CARDS[device]

	home = os.environ[ 'HOME' ]
	pathes = [ os.path.join( home, '.freevo' ),
		   os.path.join( home, '.mplayer' ),
		   os.path.join( home, '.xine' ) ]
        self.program = 'mplayer'
        if self.device.type == 'DVB-T':
            rating = rating or 8
	    self.program = 'tzap'
            self.program_file = find_file_in_path( self.program )
            if self.program_file:
                pathes.insert( 0, os.path.join( home, '.tzap' ) )
        elif self.device.type == 'DVB-C':
            rating = rating or 10
        else:
            rating = rating or 9

        if not self.program_file:
	    self.program = 'mplayer'
	    self.program_file = config.CONF.mplayer

	self.configfile = find_file_in_path( 'channels.conf', pathes )
	if not self.configfile:
	    self.reason = 'no channels configuration found'
	    return

        Recorder.__init__(self)
        self.suffix = '.ts'

        channels = []
        for c in self.device.channels:
            channels.append([c])
        self.channels = [ device, rating, channels ]
        # activate the plugin
        self.activate()


    def get_cmd(self, rec):
        """
        Return a command for recording.
        """
        channel = self.device.channels[rec.channel]
        if rec.url.startswith('file:'):
            filename = rec.url[5:]
        else:
            filename = rec.url

        if self.program == 'mplayer':
            # use mplayer -dumpstream
            return [ self.program_file, '-dumpstream', '-dumpfile',
                     filename, 'dvb://' + String(channel) ]

        elif self.program == 'tzap':
            # use tzap
	    return [ self.program_file, '-o', filename, '-c', self.configfile,
	             '-a', self.device.number, String( channel ) ]


    def get_channel_list(self):
        """
        Return list of possible channels for this plugin.
        """
        return [ self.channels ]
