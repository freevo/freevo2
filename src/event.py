#if 0 /*
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
# Revision 1.2  2003/05/28 15:01:24  dischi
# improved event handling
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


class Event:
    """
    an event is passed to the different eventhandlers in Freevo to
    activate some action.
    """
    def __init__(self, name, arg=None, context=None):
        if isinstance(name, Event):
            self.name    = name.name
            self.arg     = name.arg
            self.context = name.context
        else:
            self.name    = name
            self.arg     = None
            self.context = None
        
        if arg:
            self.arg = arg

        if context:
            self.context = context


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

MIXER_VOLUP            = Event('MIXER_VOLUP')
MIXER_VOLDOWN          = Event('MIXER_VOLDOWN')
MIXER_MUTE             = Event('MIXER_MUTE')
                       
PLAYLIST_NEXT          = Event('PLAYLIST_NEXT')
PLAYLIST_PREV          = Event('PLAYLIST_PREV')
                       
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
                       
MENU_GOTO_MAINMENU     = Event('MENU_GOTO_MAINMENU')
MENU_BACK_ONE_MENU     = Event('MENU_BACK_ONE_MENU')
                       
MENU_SELECT            = Event('MENU_SELECT')
MENU_PLAY_ITEM         = Event('MENU_PLAY_ITEM')
MENU_SUBMENU           = Event('MENU_SUBMENU')
MENU_CHANGE_STYLE      = Event('MENU_CHANGE_STYLE')
                       
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
STORE_BOOKMARK         = Event('STORE_BOOKMARK')
MENU                   = Event('MENU')


#
# Audio module
#

AUDIO_SEND_MPLAYER_CMD = Event('AUDIO_SEND_MPLAYER_CMD')


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
INPUT_ENTER            = Event('INPUT_EXIT')
INPUT_LEFT             = Event('INPUT_LEFT')
INPUT_RIGHT            = Event('INPUT_RIGHT')
INPUT_UP               = Event('INPUT_UP')
INPUT_DOWN             = Event('INPUT_DOWN')
INPUT_1                = Event('INPUT_1')
INPUT_2                = Event('INPUT_2')
INPUT_3                = Event('INPUT_3')
INPUT_4                = Event('INPUT_4')
INPUT_5                = Event('INPUT_5')
INPUT_6                = Event('INPUT_6')
INPUT_7                = Event('INPUT_7')
INPUT_8                = Event('INPUT_8')
INPUT_9                = Event('INPUT_9')
INPUT_0                = Event('INPUT_0')

INPUT_ALL_NUMBERS = (INPUT_0, INPUT_1, INPUT_2, INPUT_3, INPUT_4, INPUT_5,
                     INPUT_6, INPUT_7, INPUT_8, INPUT_9, INPUT_0 )


# Call the function specified in event.arg
FUNCTION_CALL          = Event('FUNCTION_CALL')

# All buttons which are not mapped to an event will be send as
# BOTTON event with the pressed button as arg
BUTTON                 = Event('BUTTON')



#
# Default key-event map
#

GLOBAL_EVENTS = {
    'VOLUP'     : MIXER_VOLUP,
    'VOLDOWN'   : MIXER_VOLDOWN,
    'MUTE'      : MIXER_MUTE
    }

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
    'ENTER'     : MENU_SUBMENU,
    'DISPLAY'   : MENU_CHANGE_STYLE,
    'EJECT'     : EJECT,
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
    }

TV_EVENTS = {
    'STOP'      : STOP,
    'MENU'      : STOP,
    'EXIT'      : STOP,
    'SELECT'    : STOP,
    'CH+'       : TV_CHANNEL_UP,
    'CH-'       : TV_CHANNEL_DOWN
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
    'REW'       : Event(SEEK, arg=10),
    'FFWD'      : Event(SEEK, arg=-10),
    'MENU'      : MENU,
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : STORE_BOOKMARK,
    '0'         : VIDEO_MANUAL_SEEK,
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
    }

AUDIO_EVENTS = {
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'LEFT'      : Event(SEEK, arg=-60),
    'RIGHT'     : Event(SEEK, arg=60),
    'REW'       : Event(SEEK, arg=10),
    'FFWD'      : Event(SEEK, arg=-10),
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
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

GAMES_EVENTS = {
    'STOP'      : STOP,
    'SELECT'    : STOP,
    'MENU'      : MENU,
    'DISPLAY'   : GAMES_CONFIG,
    'ENTER'     : GAMES_RESET
    }



#
# Internal events, don't map any button on them
#

PLAY_END        = Event('PLAY_END')
USER_END        = Event('USER_END')
DVD_PROTECTED   = Event('DVD_PROTECTED')
AUDIO_PLAY_END  = Event('AUDIO_PLAY_END')
