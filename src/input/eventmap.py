__all__ = [ 'EVENTMAP' ]

from freevo.ui.event import *

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
    'ENTER'     : TV_SHOW_CHANNEL,
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
    'LEFT'      : Event(SEEK, -60),
    'RIGHT'     : Event(SEEK,  60),
    'REW'       : Event(SEEK, -10),
    'FFWD'      : Event(SEEK,  10),
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
    'LEFT'      : Event(SEEK, -60),
    'RIGHT'     : Event(SEEK,  60),
    'REW'       : Event(SEEK, -10),
    'FFWD'      : Event(SEEK,  10),
    'MENU'      : MENU,
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : STORE_BOOKMARK,
    '0'         : VIDEO_MANUAL_SEEK,
    'MENU'      : DVDNAV_MENU,
    'NEXT'      : NEXT,
    'PREV'      : PREV
    }

DVDNAV_EVENTS = {
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
    'MENU'      : DVDNAV_MENU,
    }

AUDIO_EVENTS = {
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'LEFT'      : Event(SEEK, -60),
    'RIGHT'     : Event(SEEK,  60),
    'REW'       : Event(SEEK, -10),
    'FFWD'      : Event(SEEK,  10),
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
    'LEFT'      : Event(IMAGE_ROTATE, 'left'),
    'RIGHT'     : Event(IMAGE_ROTATE, 'right'),
    '1'         : Event(ZOOM_IN, 0.2),
    '2'         : Event(ZOOM_OUT, -0.2),
    '3'         : Event(ZOOM, 1.0),
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
    'LEFT'      : Event(IMAGE_MOVE, -10,   0),
    'RIGHT'     : Event(IMAGE_MOVE,  10,   0),
    'UP'        : Event(IMAGE_MOVE,   0, -10),
    'DOWN'      : Event(IMAGE_MOVE,   0,  10),
    '1'         : ZOOM_IN,
    '2'         : ZOOM_OUT,
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : IMAGE_SAVE,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
    }

GAMES_EVENTS = {
    'EXIT'      : STOP,
    'STOP'      : STOP,
    'SELECT'    : STOP,
    'MENU'      : MENU,
}

GLOBAL_EVENTS = {
    'VOL+'             : MIXER_VOLUP,
    'VOL-'             : MIXER_VOLDOWN,
    'MUTE'             : MIXER_MUTE,
    'TOGGLE'           : TOGGLE_APPLICATION
    }
    

#
# GLOABL EVENTMAP
#

EVENTMAP = {
    'menu'       : MENU_EVENTS,
    'tvmenu'     : TVMENU_EVENTS,
    'input'      : INPUT_EVENTS,
    'tv'         : TV_EVENTS,
    'video'      : VIDEO_EVENTS,
    'dvdnav'     : DVDNAV_EVENTS,
    'audio'      : AUDIO_EVENTS,
    'games'      : GAMES_EVENTS,
    'image'      : IMAGE_EVENTS,
    'image_zoom' : IMAGE_ZOOM_EVENTS,
    'global'     : GLOBAL_EVENTS
    }

