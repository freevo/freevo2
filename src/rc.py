#if 0 /*
# -----------------------------------------------------------------------
# rc.py - Remote control handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/02/11 06:10:03  krister
# Display an error if the DVD is protected and cannot be played.
#
# Revision 1.3  2003/01/11 10:37:48  dischi
# added event to reload a menu
#
# Revision 1.2  2002/11/26 22:02:10  dischi
# Added key to enable/disable subtitles. This works only with mplayer pre10
# (maybe pre9). Keyboard: l (for language) or remote SUBTITLE
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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
#endif

import socket, time, sys
import config

# Set to 1 for debug output
DEBUG = config.DEBUG

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

TRUE = 1
FALSE = 0

# Module variable that contains an initialized RemoteControl() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = RemoteControl()
        
    return _singleton


class RemoteControl:

    # Remote control buttons. This is taken from a universal remote
    # that has a large (but not ridiculous) number of buttons.
    # Try to use a common subset for the common operations, and
    # don't add buttons that only exist on a specific remote since
    # no-one else will be able to use it.
    NONE     = ''
    SLEEP    = 'SLEEP'
    MENU     = 'MENU'
    GUIDE    = 'GUIDE'
    EXIT     = 'EXIT'
    UP       = 'UP'
    DOWN     = 'DOWN'
    LEFT     = 'LEFT'
    RIGHT    = 'RIGHT'
    SELECT   = 'SELECT'
    POWER    = 'POWER'
    MUTE     = 'MUTE'
    VOLUP    = 'VOL+'
    VOLDOWN  = 'VOL-'
    CHUP     = 'CH+'
    CHDOWN   = 'CH-'
    K1       = '1'
    K2       = '2'
    K3       = '3'
    K4       = '4'
    K5       = '5'
    K6       = '6'
    K7       = '7'
    K8       = '8'
    K9       = '9'
    K0       = '0'
    DISPLAY  = 'DISPLAY'
    ENTER    = 'ENTER'
    PREV_CH  = 'PREV_CH'
    PIP_ONOFF= 'PIP_ONOFF'
    PIP_SWAP = 'PIP_SWAP'
    PIP_MOVE = 'PIP_MOVE'
    TV_VCR   = 'TV_VCR'
    REW      = 'REW'
    PLAY     = 'PLAY'
    FFWD     = 'FFWD'
    PAUSE    = 'PAUSE'
    STOP     = 'STOP'
    REC      = 'REC'      
    EJECT    = 'EJECT'
    SUBTITLE = 'SUBTITLE'

    
    # Application generated codes
    PLAY_END = 'PLAY_END'     # Reached end of song, movie, etc
    IDENTIFY_MEDIA = 'IDENTIFY_MEDIA'
    REFRESH_SCREEN = 'REFRESH_SCREEN'
    REBUILD_SCREEN = 'REBUILD_SCREEN'
    DVD_PROTECTED = 'DVD_PROTECTED' # Cannot play prot. DVDs

    def __init__(self, port=config.REMOTE_CONTROL_PORT):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind(('', self.port))
        self.app = None
        self.queue = []
        

    def post_event(self, event):
        self.queue += [event]

        
    def poll(self):
        if len(self.queue):
            ret = self.queue[0]
            del self.queue[0]
            return ret
        try:
            data = self.sock.recv(100)
            if data == '':
                print 'Lost the connection'
                self.conn.close()
            else:
                return data
        except:
            # No data available
            return self.NONE

