# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# event.py - Global events for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

import kaa.notifier

class Event(kaa.notifier.Event):
    """
    an event is passed to the different eventhandlers in Freevo to
    activate some action.
    """
    def __init__(self, name, *args, **kwargs):
        kaa.notifier.Event.__init__(self, name, *args)
        self.handler = None
        if 'handler' in kwargs:
            self.handler = kwargs['handler']


    def set_handler(self, handler):
        """
        Set a specific handler for the event.
        """
        self.handler = handler


    def __int__(self):
        """
        Return the event as int (the last char of the name will be returned
        as integer value. FIXME: remove this function!
        """
        return int(self.name[-1])




#
# Default actions Freevo knows
#

MIXER_VOLUP            = Event('MIXER_VOLUP', 5)
MIXER_VOLDOWN          = Event('MIXER_VOLDOWN', 5)
MIXER_MUTE             = Event('MIXER_MUTE')

# To change the step size, but the following code in your
# local_conf.py (setting VOL+ step size to 2)
#
# EVENTS['global']['VOL+'] = Event('MIXER_VOLUP', 2)


PLAYLIST_NEXT          = Event('PLAYLIST_NEXT')
PLAYLIST_PREV          = Event('PLAYLIST_PREV')
PLAYLIST_TOGGLE_REPEAT = Event('PLAYLIST_TOGGLE_REPEAT')

EJECT                  = Event('EJECT')
TOGGLE_APPLICATION     = Event('TOGGLE_APPLICATION')

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
MENU_GOTO_MEDIA        = Event('MENU_GOTO_MEDIA')
MENU_BACK_ONE_MENU     = Event('MENU_BACK_ONE_MENU')

MENU_SELECT            = Event('MENU_SELECT')
MENU_CHANGE_SELECTION  = Event('MENU_CHANGE_SELECTION')
MENU_PLAY_ITEM         = Event('MENU_PLAY_ITEM')
MENU_SUBMENU           = Event('MENU_SUBMENU')
MENU_CALL_ITEM_ACTION  = Event('MENU_CALL_ITEM_ACTION')
MENU_CHANGE_STYLE      = Event('MENU_CHANGE_STYLE')


DIRECTORY_CHANGE_DISPLAY_TYPE = Event('DIRECTORY_CHANGE_DISPLAY_TYPE')
DIRECTORY_TOGGLE_HIDE_PLAYED  = Event('DIRECTORY_TOGGLE_HIDE_PLAYED')

#
# TV module
#

TV_START_RECORDING     = Event('TV_START_RECORDING')
TV_CHANNEL_UP          = Event('TV_CHANNEL_UP')
TV_CHANNEL_DOWN        = Event('TV_CHANNEL_DOWN')
TV_SHOW_CHANNEL        = Event('TV_SHOW_CHANNEL')

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
INPUT_1                = Event('INPUT_1', 1)
INPUT_2                = Event('INPUT_2', 2)
INPUT_3                = Event('INPUT_3', 3)
INPUT_4                = Event('INPUT_4', 4)
INPUT_5                = Event('INPUT_5', 5)
INPUT_6                = Event('INPUT_6', 6)
INPUT_7                = Event('INPUT_7', 7)
INPUT_8                = Event('INPUT_8', 8)
INPUT_9                = Event('INPUT_9', 9)
INPUT_0                = Event('INPUT_0', 0)

INPUT_ALL_NUMBERS = (INPUT_0, INPUT_1, INPUT_2, INPUT_3, INPUT_4, INPUT_5,
                     INPUT_6, INPUT_7, INPUT_8, INPUT_9, INPUT_0 )


# Call the function specified in event.arg
FUNCTION_CALL          = Event('FUNCTION_CALL')

#
# Internal events, don't map any button on them
#

PLAY_END         = Event('PLAY_END')
PLAY_START       = Event('PLAY_START')
OSD_MESSAGE      = Event('OSD_MESSAGE')

# FIXME: delete this
RECORD           = Event('RECORD')
