#
# rc.py - Remote control handling
# 
# This is the class for setting a up the remote control server.
# It accepts simple text commands from the remote control client over UDP/IP.
#
# $Id$

import socket, time, sys

# Set to 1 for debug output
DEBUG = 0

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

    
    # Application generated codes
    PLAY_END = 'PLAY_END'     # Reached end of song, movie, etc
    IDENTIFY_MEDIA = 'IDENTIFY_MEDIA'

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

