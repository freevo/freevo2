# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# tiny_xosd.py - Implementation of an OSD function using PyOSD
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.3  2004/10/08 20:19:35  dischi
# register to OSD_MESSAGE only
#
# Revision 1.2  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.1  2004/01/07 02:03:10  rshortt
# An osd plugin by Cyril Lacoux that uses pyosd and therefore libxosd.
# This will display over Freevo and child applications while running in X.
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


"""
Plugin for PyOSDd which facilitates controling Freevo
"""

import time, re, string, pyosd

import config, plugin
from event import *

import logging
log = logging.getLogger()

OSD_MESSAGE_FONT    = '-*-helvetica-medium-r-normal-*-*-260-*-*-p-*-*-*'
OSD_MESSAGE_COLOR   = '#D3D3D3'  # LightGray
OSD_MESSAGE_TIMEOUT = 3          # 3 seconds
OSD_MESSAGE_OFFSET  = 20 + config.OSD_OVERSCAN_Y  # Offset of 20 pixels

# Labels which are displayed with percent
PERCENT = [ 'Volume', 
            'Volume - unmuted',
            'Bass',
            'Treble',
            'Synth',
            'Pcm',
            'Speaker',
            'Line',
            'Microphone',
            'CD',
            'Mix',
            'Pcm 2',
            'Record',
            'Input Gain',
            'Output Gain',
            'Line 1',
            'Line 2',
            'Line 3',
            'Digital 1',
            'Digital 2',
            'Digital 3',
            'Phone In',
            'Phone Out',
            'Video',
            'Radio',
            'Monitor' ]

# Labels which are displayed with Slider
SLIDER  = [ 'Balance',
            'Volume - muted' ]

class PluginInterface(plugin.DaemonPlugin):
    """
    Xosd plugin.

    This plugin shows messages sent from other parts of Freevo on
    the screen for 3 seconds.
    This is a replacement for tiny_osd which works with PyOSD (XOsd)

    activate with :
    plugin.remove('tiny_osd')
    plugin.activate('tiny_xosd')
    
    """
    def __init__(self):
        """
        init the osd
        """
        plugin.DaemonPlugin.__init__(self)
        self.events = [ 'OSD_MESSAGE' ]
        self.plugin_name = 'OSD_MESSAGE'

        # Initializing the screen
        self.osd = pyosd.osd()
        self.osd.set_font(OSD_MESSAGE_FONT)
        self.osd.set_colour(OSD_MESSAGE_COLOR)
        self.osd.set_timeout(OSD_MESSAGE_TIMEOUT)
        self.osd.set_offset(OSD_MESSAGE_OFFSET)

        self.message = ''
        # (0%) -> (100%)
        self.re_percent = re.compile(r' [0-9][0-9]?[0-9]?%')

    def draw_osd(self):
        """
        Display a message on the screen.
        """

        if not self.message == '' :
            re_percent = self.re_percent.search(self.message)

            if re_percent :
                # A percentage was sent
                label   = self.message[0:re_percent.start() - 1]
                percent = int(self.message[re_percent.start() + 1:re_percent.end() - 1])

                if label in SLIDER :
                    type = pyosd.TYPE_SLIDER
                else :
                    type = pyosd.TYPE_PERCENT
                
                if percent < 0 :
                    percent = 0
                elif percent > 100 :
                    percent = 100

                # Display it on the bottom of the screen
                self.osd.set_pos(pyosd.POS_BOT)
                # First line is the label with the value
                self.osd.display('%s (%d%%)' % (_(label), percent), pyosd.TYPE_STRING, line=0)
                # Second line is the progress bar
                self.osd.display(percent, type, line=1)

            else :
                # This is text, display it on top
                self.osd.set_pos(pyosd.POS_TOP)
                if re.search('\n', self.message) :
                    # If message contains one or more \n, display two first lines.
                    s_msg = self.message.split('\n')
                    self.osd.display(s_msg[0], pyosd.TYPE_STRING, line=0)
                    self.osd.display(s_msg[1], pyosd.TYPE_STRING, line=1)
                else :
                    # If not, display only the first line
                    self.osd.display(self.message, pyosd.TYPE_STRING, line=0)
                    self.osd.display('', pyosd.TYPE_STRING, line=1)

    def eventhandler(self, event, menuw=None):
        """
        Do something when receiving an event
        """

        log.info('%s: %s app got %s event' % ( time.time(),
                                               self.plugin_name,
                                               event))
        if event == OSD_MESSAGE :
            self.message = event.arg
            self.draw_osd()
