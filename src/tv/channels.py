# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# channels.py - Freevo module to handle channel changing.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.22  2004/08/10 19:37:22  dischi
# better pyepg integration
#
# Revision 1.21  2004/08/09 21:19:47  dischi
# make tv guide working again (but very buggy)
#
# Revision 1.20  2004/08/05 17:27:16  dischi
# Major (unfinished) tv update:
# o the epg is now taken from pyepg in lib
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
# Revision 1.19  2004/07/11 12:33:29  dischi
# no tuner id is ok for dvb
#
# Revision 1.18  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.17  2004/03/05 04:04:10  rshortt
# Only call setChannel on an external tuner plugin if we really have one.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import os
import time
import stat

import config
import tv.freq, tv.v4l2
import util
import plugin

# The Electronic Program Guide
import pyepg

class Channel:
    """
    information about one specific channel, also containing
    epg informations
    """
    def __init__(self, name, freq, epg):
        self.name = name
        self.freq = []
        self.epg  = epg
        if isinstance(freq, list) or isinstance(freq, tuple):
            for f in freq:
                self.__add_freq__(f)
        else:
            self.__add_freq__(freq)

        # variables from the epg
        self.id   = self.epg.id

        # functions from the epg
        self.next = self.epg.next
        self.prev = self.epg.prev
        self.get  = self.epg.get


    def __add_freq__(self, freq):
        """
        add a frequence to the internal list where to find that channel
        """
        if freq.find(':') == -1:
            # FIXME: but this into the config file
            freq = 'dvb:%s' % freq
        self.freq.append(freq)


    def player(self):
        """
        return player object for playing this channel
        """
        for f in self.freq:
            device, freq = f.split(':')
            print device, freq
            # try all internal frequencies
            for p in plugin.getbyname(plugin.TV, True):
                # FIXME: better handling for rate == 1 or 2
                if p.rate(self, device, freq):
                    return p, device, freq
        return None

                    


class ChannelList:

    def __init__(self):
        self.selected = 0
        self.channels = []

        source = config.XMLTV_FILE
        pickle = os.path.join(config.FREEVO_CACHEDIR, 'epg')

        epg = pyepg.load(source, pickle)

        for c in config.TV_CHANNELS:
            self.channels.append(Channel(c[1], c[2], epg.get(c[0])))
        

    def down(self):
        """
        go one channel up
        """
        self.selected = (self.selected + 1) % len(self.channels)


    def up(self):
        """
        go one channel down
        """
        self.selected = (self.selected + len(self.channels) - 1) % len(self.channels)


    def set(self, pos):
        """
        set channel
        """
        self.selected = pos
        

    def get(self):
        """
        return selected channel information
        """
        return self.channels[self.selected]


    def get_all(self):
        """
        return all channels
        """
        return self.channels
    
