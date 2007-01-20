__all__ = [ 'EVENTMAP' ]

from event import *

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
    'REW'       : Event(SEEK, -10),
    'FFWD'      : Event(SEEK,  10),
    'GUIDE'     : DVDNAV_TITLEMENU,
    'MENU'      : DVDNAV_MENU,
    'LANG'      : VIDEO_NEXT_AUDIOLANG,
    'ANGLE'     : VIDEO_NEXT_ANGLE,
    'CH+'       : NEXT,
    'CH-'       : PREV
    }

VCD_EVENTS = {
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'LEFT'      : Event(SEEK, -60),
    'RIGHT'     : Event(SEEK,  60),
    'REW'       : Event(SEEK, -10),
    'FFWD'      : Event(SEEK,  10),
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
    'LEFT'      : Event(IMAGE_MOVE, -10,   0),
    'RIGHT'     : Event(IMAGE_MOVE,  10,   0),
    'UP'        : Event(IMAGE_MOVE,   0, -10),
    'DOWN'      : Event(IMAGE_MOVE,   0,  10),
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
    'EXIT'      : STOP,
    'STOP'      : STOP,
    'SELECT'    : STOP,
    'MENU'      : MENU,
    'DISPLAY'   : GAMES_CONFIG,
    'ENTER'     : GAMES_RESET
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
    'dvd'        : DVD_EVENTS,             # only used by xine
    'vcd'        : VCD_EVENTS,             # only used by xine
    'audio'      : AUDIO_EVENTS,
    'games'      : GAMES_EVENTS,
    'image'      : IMAGE_EVENTS,
    'image_zoom' : IMAGE_ZOOM_EVENTS,
    'global'     : GLOBAL_EVENTS
    }

