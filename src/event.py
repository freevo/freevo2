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
# Revision 1.61  2005/07/16 08:56:07  dischi
# add function to set the handler
#
# Revision 1.60  2005/07/15 20:40:44  dischi
# base Event on kaa.notifier.Event
#
# Revision 1.59  2005/07/08 14:45:35  dischi
# add some extra events for mouse support
#
# Revision 1.58  2005/06/25 08:52:24  dischi
# switch to new style python classes
#
# Revision 1.57  2005/06/24 20:54:55  dischi
# remove USER_END
#
# Revision 1.56  2005/06/12 18:51:59  dischi
# remove old event
#
# Revision 1.55  2004/09/27 18:42:10  dischi
# move default event mapping to input/
#
# Revision 1.54  2004/09/25 05:20:15  rshortt
# Move the default keymap into src/gui/displays/sdl.py at least until it goes
# into a plugin and there is a magical new Freevo keymap that hasn't been
# thought up yet.
#
# Also removed a duplicate SUBTITLE entry from one of the dicts.
#
# Revision 1.53  2004/09/15 19:37:42  dischi
# add control toggle key
#
# Revision 1.52  2004/08/26 15:28:20  dischi
# add event for switching tv guide look
#
# Revision 1.51  2004/08/24 16:42:39  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.50  2004/08/08 18:56:37  rshortt
# Add some quick recordserver events.  I'm planning on reviewing them and
# adding more with names that make sense.
#
# Revision 1.49  2004/08/01 10:56:17  dischi
# add SCREEN_CONTENT_CHANGE
#
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

import kaa.notifier

class Event(kaa.notifier.Event):
    """
    an event is passed to the different eventhandlers in Freevo to
    activate some action.
    """
    def __init__(self, name, arg=None, handler=None):
        if isinstance(name, Event):
            self.name    = name.name
            self.arg     = name.arg
            self.handler = name.handler
        else:
            self.name    = name
            self.arg     = None
            self.handler = None
        
        if arg or arg == 0:
            self.arg = arg

        if handler:
            self.handler = handler


    def set_handler(self, handler):
        """
        Set a specific handler for the event.
        """
        self.handler = handler

        
    def __int__(self):
        """
        return the event as int (the last char of the name will be returned
        as integer value
        """
        return int(self.name[-1])




#
# Default actions Freevo knows
#

MIXER_VOLUP            = Event('MIXER_VOLUP', arg=5)
MIXER_VOLDOWN          = Event('MIXER_VOLDOWN', arg=5)
MIXER_MUTE             = Event('MIXER_MUTE')
TOGGLE_CONTROL         = Event('TOGGLE_CONTROL')

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
                       
MENU_GOTO_MAINMENU     = Event('MENU_GOTO_MAINMENU')
MENU_BACK_ONE_MENU     = Event('MENU_BACK_ONE_MENU')
                       
MENU_SELECT            = Event('MENU_SELECT')
MENU_CHANGE_SELECTION  = Event('MENU_CHANGE_SELECTION')
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
# Internal events, don't map any button on them
#

PLAY_END         = Event('PLAY_END')
DVD_PROTECTED    = Event('DVD_PROTECTED')
PLAY_START       = Event('PLAY_START')

OSD_MESSAGE      = Event('OSD_MESSAGE')

VIDEO_START      = Event('VIDEO_START')
VIDEO_END        = Event('VIDEO_END')

OS_EVENT_POPEN2  = Event('OS_EVENT_POPEN2')
OS_EVENT_WAITPID = Event('OS_EVENT_WAITPID')
OS_EVENT_KILL    = Event('OS_EVENT_KILL')

RECORD           = Event('RECORD')
STOP_RECORDING   = Event('STOP_RECORDING')
RECORD_START     = Event('RECORD_START')
RECORD_STOP      = Event('RECORD_STOP')


SCREEN_CONTENT_CHANGE = Event('SCREEN_CONTENT_CHANGE')
THEME_CHANGE          = Event('THEME_CHANGE')
