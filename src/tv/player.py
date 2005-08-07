# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# player.py - template a for tv player plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2005/08/07 13:00:22  dischi
# remove all menuw in eventhandler and remove fallback for old code in menu
#
# Revision 1.7  2005/07/16 08:41:12  dischi
# move context handling from eventhandler to input
#
# Revision 1.6  2005/06/26 10:53:00  dischi
# use kaa.epg instead of pyepg
#
# Revision 1.5  2004/12/13 01:46:33  rshortt
# remove old channel changing code and add some logging
#
# Revision 1.4  2004/09/15 20:45:31  dischi
# remove unneeded events functions
#
# Revision 1.3  2004/08/25 12:51:45  dischi
# moved Application for eventhandler into extra dir for future templates
#
# Revision 1.2  2004/08/22 20:12:12  dischi
# class application doesn't change the display (screen) type anymore
#
# Revision 1.1  2004/08/05 17:27:16  dischi
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


import time
import os
import logging

import config
import util
import plugin

from event import *
from application import Application

log = logging.getLogger('tv')

class TVPlayer(Application):
    """
    template for tv player application
    """
    def __init__(self, name, eventmap='tv', fullscreen=True):
        """
        init the player
        """
        Application.__init__(self, name, eventmap, fullscreen)


    def rate(self, type):
        """
        rating how good this player can show 'mode' video groups
        """
        return 0

    
    def play(self):
        """
        start playing
        """
        raise Exception('not implemented in template')


    def set_channel(self, channel):
        """
        tune to a new channel
        """
        raise Exception('not implemented in template')
    

    def eventhandler(self, event):
        """
        handle some basic events
        """
        if event == STOP or event == PLAY_END:
            self.stop()
            return True

        if event in [ TV_CHANNEL_UP, TV_CHANNEL_DOWN] or str(event).startswith('INPUT_'):
            log.warning('channel events not implemented here yet')

        return False
    
