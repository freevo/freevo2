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
# Revision 1.14  2003/04/27 17:43:30  dischi
# secure RemoteControl against different threads
#
# Revision 1.13  2003/04/27 15:28:24  rshortt
# Adding back support for using a network remote.  If ENABLE_NETWORK_REMOTE is
# set to 1 in local_conf.py then rc.py will also listen for commands over UDP.
#
# Revision 1.12  2003/04/24 19:55:54  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.11  2003/04/20 12:43:32  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.10  2003/04/19 21:28:39  dischi
# identifymedia.py is now a plugin and handles everything related to
# rom drives (init, autostarter, items in menus)
#
# Revision 1.9  2003/04/06 21:12:56  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.7  2003/02/20 18:31:02  dischi
# except on IOError if config.LIRCRC doesn't exists
#
# Revision 1.6  2003/02/19 17:15:15  outlyer
# The idletool needs to know what function we're running so it doesn't try
# to draw when a movie is playing, however, if music is playing, it can still
# draw the information, so we need to distinguish between 'video' and 'audio'
#
# The rc.func will contain the function being used (i.e. 'video' 'audio' etc.)
#
# Currently, this does nothing, so ignore it.
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

import socket
import config
import util

PYLIRC = 1
try:
    import pylirc
except ImportError:
    print 'WARNING: PyLirc not found, lirc remote control disabled!'
    PYLIRC = 0

# Set to 1 for debug output
DEBUG = config.DEBUG


TRUE = 1
FALSE = 0

# Module variable that contains an initialized RemoteControl() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = util.SynchronizedObject(RemoteControl())
        
    return _singleton


def post_event(event):
    return get_singleton().post_event(event)

def app(application=0, func=None):
    if not application == 0:
        if hasattr(application, 'app_mode') and not func:
            func = application.app_mode
        if hasattr(application, 'eventhandler'):
            application = application.eventhandler
        get_singleton().app = application
        get_singleton().func = func
        
    return get_singleton().app


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
USER_END = 'USER_END'     # User ended the song, etc

REFRESH_SCREEN = 'REFRESH_SCREEN'
REBUILD_SCREEN = 'REBUILD_SCREEN'
DVD_PROTECTED  = 'DVD_PROTECTED' # Cannot play prot. DVDs


class RemoteControl:

    def __init__(self, port=config.REMOTE_CONTROL_PORT):
        self.pylirc = PYLIRC
        
        if self.pylirc:
            try:
                pylirc.init('freevo', config.LIRCRC)
                pylirc.blocking(0)
            except RuntimeError:
                print 'WARNING: Could not initialize PyLirc!'
                self.pylirc = 0
            except IOError:
                print 'WARNING: %s not found!' % config.LIRCRC
                self.pylirc = 0
        if config.ENABLE_NETWORK_REMOTE:
            self.port = port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(0)
            self.sock.bind(('', self.port))

        self.app = None
        self.func = None
        self.queue = []
        
    def post_event(self, event):
        self.queue += [event]

        
    def poll(self):
        if len(self.queue):
            ret = self.queue[0]
            del self.queue[0]
            return ret
        if self.pylirc:
            list = pylirc.nextcode()
            if list:
                for code in list:
                    data = code
                    return data
        if config.ENABLE_NETWORK_REMOTE:
            try:
                data = self.sock.recv(100)
                if data == '':
                    print 'Lost the connection'
                    self.conn.close()
                else:
                    return data
            except:
                # No data available
                pass

        return None
