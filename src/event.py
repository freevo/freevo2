# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# event.py - Global events for Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.48  2004/07/21 11:32:31  dischi
# fix dvd events for language settings
#
# Revision 1.47  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.46  2004/06/28 15:55:10  dischi
# angle switching
#
# Revision 1.45  2004/06/17 23:16:05  rshortt
# Add events for RECORD_START/STOP. (forgot to check in this file earlier).
#
# Revision 1.44  2004/05/12 18:56:36  dischi
# add keys to move inside a zoom image in image viewer
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


class Event:
    """
    an event is passed to the different eventhandlers in Freevo to
    activate some action.
    """
    def __init__(self, name, arg=None, context=None, handler=None):
        if isinstance(name, Event):
            self.name    = name.name
            self.arg     = name.arg
            self.context = name.context
            self.handler = name.handler
        else:
            self.name    = name
            self.arg     = None
            self.context = None
            self.handler = None
        
        if arg or arg == 0:
            self.arg = arg

        if context:
            self.context = context

        if handler:
            self.handler = handler


    def __str__(self):
        """
        return the event as string
        """
        return self.name


    def __int__(self):
        """
        return the event as int (the last char of the name will be returned
        as integer value
        """
        return int(self.name[-1])

    
    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not other:
            return 1
        if isinstance(other, Event):
            return self.name != other.name
        return self.name != other




#
# Default actions Freevo knows
#

MIXER_VOLUP            = Event('MIXER_VOLUP', arg=5)
MIXER_VOLDOWN          = Event('MIXER_VOLDOWN', arg=5)
MIXER_MUTE             = Event('MIXER_MUTE')

# To change the step size, but the following code in your
# local_conf.py (setting VOL+ step size to 2)
#
# EVENTS['global']['VOL+'] = Event('MIXER_VOLUP', arg=2)


PLAYLIST_NEXT          = Event('PLAYLIST_NEXT')
PLAYLIST_PREV          = Event('PLAYLIST_PREV')
PLAYLIST_TOGGLE_REPEAT = Event('PLAYLIST_TOGGLE_REPEAT')
                       
EJECT                  = Event('EJECT')
                       
#
# Menu
#

MENU_LEFT              = Event('MENU_LEFT')
MENU_RIGHT             = Event('MENU_RIGHT')
MENU_UP                = Event('MENU_UP')
MENU_DOWN              = Event('MENU_DOWN')
MENU_PAGEUP            = Event('MENU_PAGEUP')
MENU_PAGEDOWN          = Event('MENU_PAGEDOWN')
MENU_REBUILD           = Event('MENU_REBUILD')
                       
MENU_GOTO_MAINMENU     = Event('MENU_GOTO_MAINMENU')
MENU_BACK_ONE_MENU     = Event('MENU_BACK_ONE_MENU')
                       
MENU_SELECT            = Event('MENU_SELECT')
MENU_PLAY_ITEM         = Event('MENU_PLAY_ITEM')
MENU_SUBMENU           = Event('MENU_SUBMENU')
MENU_CALL_ITEM_ACTION  = Event('MENU_CALL_ITEM_ACTION')
MENU_CHANGE_STYLE      = Event('MENU_CHANGE_STYLE')


DIRECTORY_CHANGE_DISPLAY_TYPE = Event('DIRECTORY_CHANGE_DISPLAY_TYPE')

#
# TV module
#

TV_START_RECORDING     = Event('TV_START_RECORDING')
TV_CHANNEL_UP          = Event('TV_CHANNEL_UP')
TV_CHANNEL_DOWN        = Event('TV_CHANNEL_DOWN')
                       
#
# Global playing events
#

SEEK                   = Event('SEEK')
PLAY                   = Event('PLAY')
PAUSE                  = Event('PAUSE')
STOP                   = Event('STOP')
TOGGLE_OSD             = Event('TOGGLE_OSD')

#
# Video module
#

VIDEO_SEND_MPLAYER_CMD = Event('VIDEO_SEND_MPLAYER_CMD')
VIDEO_MANUAL_SEEK      = Event('VIDEO_MANUAL_SEEK')
VIDEO_NEXT_AUDIOLANG   = Event('VIDEO_NEXT_AUDIOLANG')
VIDEO_NEXT_SUBTITLE    = Event('VIDEO_NEXT_SUBTITLE')
VIDEO_TOGGLE_INTERLACE = Event('VIDEO_TOGGLE_INTERLACE')
VIDEO_NEXT_ANGLE       = Event('VIDEO_NEXT_ANGLE')
STORE_BOOKMARK         = Event('STORE_BOOKMARK')
MENU                   = Event('MENU')

DVDNAV_LEFT            = Event('DVDNAV_LEFT')
DVDNAV_RIGHT           = Event('DVDNAV_RIGHT')
DVDNAV_UP              = Event('DVDNAV_UP')
DVDNAV_DOWN            = Event('DVDNAV_DOWN')
DVDNAV_SELECT          = Event('DVDNAV_SELECT')
DVDNAV_TITLEMENU       = Event('DVDNAV_TITLEMENU')
DVDNAV_MENU            = Event('DVDNAV_MENU')
NEXT                   = Event('NEXT')
PREV                   = Event('PREV')


#
# Audio module
#

AUDIO_SEND_MPLAYER_CMD = Event('AUDIO_SEND_MPLAYER_CMD')
AUDIO_LOG              = Event('AUDIO_LOG')


#
# Image module
#

IMAGE_ZOOM_GRID1       = Event('IMAGE_ZOOM_GRID1')
IMAGE_ZOOM_GRID2       = Event('IMAGE_ZOOM_GRID2')
IMAGE_ZOOM_GRID3       = Event('IMAGE_ZOOM_GRID3')
IMAGE_ZOOM_GRID4       = Event('IMAGE_ZOOM_GRID4')
IMAGE_ZOOM_GRID5       = Event('IMAGE_ZOOM_GRID5')
IMAGE_ZOOM_GRID6       = Event('IMAGE_ZOOM_GRID6')
IMAGE_ZOOM_GRID7       = Event('IMAGE_ZOOM_GRID7')
IMAGE_ZOOM_GRID8       = Event('IMAGE_ZOOM_GRID8')
IMAGE_ZOOM_GRID9       = Event('IMAGE_ZOOM_GRID9')

IMAGE_NO_ZOOM          = Event('IMAGE_NO_ZOOM')

IMAGE_ROTATE           = Event('IMAGE_ROTATE')
IMAGE_SAVE             = Event('IMAGE_SAVE')

IMAGE_MOVE             = Event('IMAGE_MOVE')

#
# Games module
#

GAMES_CONFIG           = Event('GAMES_CONFIG')
GAMES_RESET            = Event('GAMES_RESET')
GAMES_SNAPSHOT         = Event('GAMES_SNAPSHOT')


#
# Input boxes
#

INPUT_EXIT             = Event('INPUT_EXIT')
INPUT_ENTER            = Event('INPUT_ENTER')
INPUT_LEFT             = Event('INPUT_LEFT')
INPUT_RIGHT            = Event('INPUT_RIGHT')
INPUT_UP               = Event('INPUT_UP')
INPUT_DOWN             = Event('INPUT_DOWN')
INPUT_1                = Event('INPUT_1', arg=1)
INPUT_2                = Event('INPUT_2', arg=2)
INPUT_3                = Event('INPUT_3', arg=3)
INPUT_4                = Event('INPUT_4', arg=4)
INPUT_5                = Event('INPUT_5', arg=5)
INPUT_6                = Event('INPUT_6', arg=6)
INPUT_7                = Event('INPUT_7', arg=7)
INPUT_8                = Event('INPUT_8', arg=8)
INPUT_9                = Event('INPUT_9', arg=9)
INPUT_0                = Event('INPUT_0', arg=0)

INPUT_ALL_NUMBERS = (INPUT_0, INPUT_1, INPUT_2, INPUT_3, INPUT_4, INPUT_5,
                     INPUT_6, INPUT_7, INPUT_8, INPUT_9, INPUT_0 )


# Call the function specified in event.arg
FUNCTION_CALL          = Event('FUNCTION_CALL')

# All buttons which are not mapped to an event will be send as
# BOTTON event with the pressed button as arg
BUTTON                 = Event('BUTTON')
RATING                 = Event('RATING')



#
# Default key-event map
#

MENU_EVENTS = {
    'LEFT'      : MENU_LEFT,
    'RIGHT'     : MENU_RIGHT,
    'UP'        : MENU_UP,
    'DOWN'      : MENU_DOWN,
    'CH+'       : MENU_PAGEUP,
    'CH-'       : MENU_PAGEDOWN,
    'MENU'      : MENU_GOTO_MAINMENU,
    'EXIT'      : MENU_BACK_ONE_MENU,
    'SELECT'    : MENU_SELECT,
    'PLAY'      : MENU_PLAY_ITEM,
    'ENTER'     : MENU_SUBMENU,
    'DISPLAY'   : MENU_CHANGE_STYLE,
    'EJECT'     : EJECT
    } 

TVMENU_EVENTS = {
    'LEFT'      : MENU_LEFT,
    'RIGHT'     : MENU_RIGHT,
    'UP'        : MENU_UP,
    'DOWN'      : MENU_DOWN,
    'CH+'       : MENU_PAGEUP,
    'CH-'       : MENU_PAGEDOWN,
    'MENU'      : MENU_GOTO_MAINMENU,
    'EXIT'      : MENU_BACK_ONE_MENU,
    'SELECT'    : MENU_SELECT,
    'DISPLAY'   : MENU_CHANGE_STYLE,
    'REC'       : TV_START_RECORDING
    } 

INPUT_EVENTS = {
    'EXIT'      : INPUT_EXIT,
    'ENTER'     : INPUT_ENTER,
    'SELECT'    : INPUT_ENTER,
    'LEFT'      : INPUT_LEFT,
    'RIGHT'     : INPUT_RIGHT,
    'UP'        : INPUT_UP,
    'DOWN'      : INPUT_DOWN,
    '1'         : INPUT_1,
    '2'         : INPUT_2,
    '3'         : INPUT_3,
    '4'         : INPUT_4,
    '5'         : INPUT_5,
    '6'         : INPUT_6,
    '7'         : INPUT_7,
    '8'         : INPUT_8,
    '9'         : INPUT_9,
    '0'         : INPUT_0,
    'CH+'       : MENU_PAGEUP,
    'CH-'       : MENU_PAGEDOWN
    }

TV_EVENTS = {
    'STOP'      : STOP,
    'MENU'      : STOP,
    'EXIT'      : STOP,
    'SELECT'    : STOP,
    'PAUSE'     : PAUSE,
    'CH+'       : TV_CHANNEL_UP,
    'CH-'       : TV_CHANNEL_DOWN,
    'LEFT'      : Event(SEEK, arg=-60),
    'RIGHT'     : Event(SEEK, arg=60),
    'REW'       : Event(SEEK, arg=-10),
    'FFWD'      : Event(SEEK, arg=10),
    'DISPLAY'   : TOGGLE_OSD,
    '0'         : INPUT_0,
    '1'         : INPUT_1,
    '2'         : INPUT_2,
    '3'         : INPUT_3,
    '4'         : INPUT_4,
    '5'         : INPUT_5,
    '6'         : INPUT_6,
    '7'         : INPUT_7,
    '8'         : INPUT_8,
    '9'         : INPUT_9,
    }

VIDEO_EVENTS = {
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT,
    'LEFT'      : Event(SEEK, arg=-60),
    'RIGHT'     : Event(SEEK, arg=60),
    'REW'       : Event(SEEK, arg=-10),
    'FFWD'      : Event(SEEK, arg=10),
    'MENU'      : MENU,
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : STORE_BOOKMARK,
    '0'         : VIDEO_MANUAL_SEEK
    }

DVD_EVENTS = {
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'UP'        : DVDNAV_UP,
    'DOWN'      : DVDNAV_DOWN,
    'LEFT'      : DVDNAV_LEFT,
    'RIGHT'     : DVDNAV_RIGHT,
    'ENTER'     : DVDNAV_SELECT,
    'SELECT'    : DVDNAV_SELECT,
    'DISPLAY'   : TOGGLE_OSD,
    'SUBTITLE'  : VIDEO_NEXT_SUBTITLE,
    'REW'       : Event(SEEK, arg=-10),
    'FFWD'      : Event(SEEK, arg=10),
    'GUIDE'     : DVDNAV_TITLEMENU,
    'MENU'      : DVDNAV_MENU,
    'LANG'      : VIDEO_NEXT_AUDIOLANG,
    'SUBTITLE'  : VIDEO_NEXT_SUBTITLE,
    'ANGLE'     : VIDEO_NEXT_ANGLE,
    'CH+'       : NEXT,
    'CH-'       : PREV
    }

VCD_EVENTS = {
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'LEFT'      : Event(SEEK, arg=-60),
    'RIGHT'     : Event(SEEK, arg=60),
    'REW'       : Event(SEEK, arg=-10),
    'FFWD'      : Event(SEEK, arg=10),
    'MENU'      : MENU,
    'DISPLAY'   : TOGGLE_OSD,
    'LANG'      : VIDEO_NEXT_AUDIOLANG,
    'SUBTITLE'  : VIDEO_NEXT_SUBTITLE,
    'ANGLE'     : VIDEO_NEXT_ANGLE,
    '1'         : INPUT_1,
    '2'         : INPUT_2,
    '3'         : INPUT_3,
    '4'         : INPUT_4,
    '5'         : INPUT_5,
    '6'         : INPUT_6,
    '7'         : INPUT_7,
    '8'         : INPUT_8,
    '9'         : INPUT_9
    }

AUDIO_EVENTS = {
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'LEFT'      : Event(SEEK, arg=-60),
    'RIGHT'     : Event(SEEK, arg=60),
    'REW'       : Event(SEEK, arg=-10),
    'FFWD'      : Event(SEEK, arg=10),
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT,
    '1'         : INPUT_1,
    '2'         : INPUT_2,
    '3'         : INPUT_3,
    '4'         : INPUT_4,
    '5'         : INPUT_5,
    '6'         : INPUT_6,
    '7'         : INPUT_7,
    '8'         : INPUT_8,
    '9'         : INPUT_9,
    }
    
IMAGE_EVENTS = {
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'LEFT'      : Event(IMAGE_ROTATE, arg='left'),
    'RIGHT'     : Event(IMAGE_ROTATE, arg='right'),
    '1'         : IMAGE_ZOOM_GRID1,
    '2'         : IMAGE_ZOOM_GRID2,
    '3'         : IMAGE_ZOOM_GRID3,
    '4'         : IMAGE_ZOOM_GRID4,
    '5'         : IMAGE_ZOOM_GRID5,
    '6'         : IMAGE_ZOOM_GRID6,
    '7'         : IMAGE_ZOOM_GRID7,
    '8'         : IMAGE_ZOOM_GRID8,
    '9'         : IMAGE_ZOOM_GRID9,
    '0'         : IMAGE_NO_ZOOM,
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : IMAGE_SAVE,
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
    }

IMAGE_ZOOM_EVENTS = {
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'LEFT'      : Event(IMAGE_MOVE, arg=(-10,  0)),
    'RIGHT'     : Event(IMAGE_MOVE, arg=( 10,  0)),
    'UP'        : Event(IMAGE_MOVE, arg=(  0,-10)),
    'DOWN'      : Event(IMAGE_MOVE, arg=(  0, 10)),
    '1'         : IMAGE_ZOOM_GRID1,
    '2'         : IMAGE_ZOOM_GRID2,
    '3'         : IMAGE_ZOOM_GRID3,
    '4'         : IMAGE_ZOOM_GRID4,
    '5'         : IMAGE_ZOOM_GRID5,
    '6'         : IMAGE_ZOOM_GRID6,
    '7'         : IMAGE_ZOOM_GRID7,
    '8'         : IMAGE_ZOOM_GRID8,
    '9'         : IMAGE_ZOOM_GRID9,
    '0'         : IMAGE_NO_ZOOM,
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : IMAGE_SAVE,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
    }

GAMES_EVENTS = {
    'STOP'      : STOP,
    'SELECT'    : STOP,
    'MENU'      : MENU,
    'DISPLAY'   : GAMES_CONFIG,
    'ENTER'     : GAMES_RESET
}

GLOBAL_EVENTS = {
    'VOL+'      : MIXER_VOLUP,
    'VOL-'      : MIXER_VOLDOWN,
    'MUTE'      : MIXER_MUTE
    }
    

import pygame.locals as key

DEFAULT_KEYMAP = {
    key.K_F1          : 'SLEEP',
    key.K_HOME        : 'MENU',
    key.K_g           : 'GUIDE',
    key.K_ESCAPE      : 'EXIT',
    key.K_UP          : 'UP',
    key.K_DOWN        : 'DOWN',
    key.K_LEFT        : 'LEFT',
    key.K_RIGHT       : 'RIGHT',
    key.K_SPACE       : 'SELECT',
    key.K_RETURN      : 'SELECT',
    key.K_F2          : 'POWER',
    key.K_F3          : 'MUTE',
    key.K_KP_MINUS    : 'VOL-',
    key.K_n           : 'VOL-',
    key.K_KP_PLUS     : 'VOL+',
    key.K_m           : 'VOL+',
    key.K_c           : 'CH+',
    key.K_v           : 'CH-',
    key.K_1           : '1',
    key.K_2           : '2',
    key.K_3           : '3',
    key.K_4           : '4',
    key.K_5           : '5',
    key.K_6           : '6',
    key.K_7           : '7',
    key.K_8           : '8',
    key.K_9           : '9',
    key.K_0           : '0',
    key.K_d           : 'DISPLAY',
    key.K_e           : 'ENTER',
    key.K_UNDERSCORE  : 'PREV_CH',
    key.K_o           : 'PIP_ONOFF',
    key.K_w           : 'PIP_SWAP',
    key.K_i           : 'PIP_MOVE',
    key.K_F4          : 'TV_VCR',
    key.K_r           : 'REW',
    key.K_p           : 'PLAY',
    key.K_f           : 'FFWD',
    key.K_u           : 'PAUSE',
    key.K_s           : 'STOP',
    key.K_F6          : 'REC',
    key.K_PERIOD      : 'EJECT',
    key.K_l           : 'SUBTITLE',
    key.K_a           : 'LANG'
    }



#
# Internal events, don't map any button on them
#

PLAY_END         = Event('PLAY_END')
USER_END         = Event('USER_END')
DVD_PROTECTED    = Event('DVD_PROTECTED')
PLAY_START       = Event('PLAY_START')

OSD_MESSAGE      = Event('OSD_MESSAGE')

VIDEO_START      = Event('VIDEO_START')
VIDEO_END        = Event('VIDEO_END')

OS_EVENT_POPEN2  = Event('OS_EVENT_POPEN2')
OS_EVENT_WAITPID = Event('OS_EVENT_WAITPID')
OS_EVENT_KILL    = Event('OS_EVENT_KILL')

RECORD_START     = Event('RECORD_START')
RECORD_STOP      = Event('RECORD_STOP')

