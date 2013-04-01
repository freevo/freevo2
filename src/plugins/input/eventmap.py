__all__ = [ 'EVENTMAP' ]

from ... import core as freevo

#
# Default key-event map
#

MENU_EVENTS = {
    'LEFT'      : freevo.MENU_LEFT,
    'RIGHT'     : freevo.MENU_RIGHT,
    'UP'        : freevo.MENU_UP,
    'DOWN'      : freevo.MENU_DOWN,
    'CH+'       : freevo.MENU_PAGEUP,
    'CH-'       : freevo.MENU_PAGEDOWN,
    'MENU'      : freevo.MENU_GOTO_MAINMENU,
    'EXIT'      : freevo.MENU_BACK_ONE_MENU,
    'SELECT'    : freevo.MENU_SELECT,
    'PLAY'      : freevo.MENU_PLAY_ITEM,
    'ENTER'     : freevo.MENU_SUBMENU,
    'DISPLAY'   : freevo.MENU_CHANGE_STYLE,
    'EJECT'     : freevo.EJECT
    } 

TVMENU_EVENTS = {
    'LEFT'      : freevo.MENU_LEFT,
    'RIGHT'     : freevo.MENU_RIGHT,
    'UP'        : freevo.MENU_UP,
    'DOWN'      : freevo.MENU_DOWN,
    'CH+'       : freevo.MENU_PAGEUP,
    'CH-'       : freevo.MENU_PAGEDOWN,
    'MENU'      : freevo.MENU_GOTO_MAINMENU,
    'EXIT'      : freevo.MENU_BACK_ONE_MENU,
    'SELECT'    : freevo.MENU_SELECT,
    'DISPLAY'   : freevo.MENU_CHANGE_STYLE,
    'ENTER'     : freevo.TV_SHOW_CHANNEL,
    'REC'       : freevo.TV_START_RECORDING
    } 

INPUT_EVENTS = {
    'EXIT'      : freevo.INPUT_EXIT,
    'ENTER'     : freevo.INPUT_ENTER,
    'SELECT'    : freevo.INPUT_ENTER,
    'LEFT'      : freevo.INPUT_LEFT,
    'RIGHT'     : freevo.INPUT_RIGHT,
    'UP'        : freevo.INPUT_UP,
    'DOWN'      : freevo.INPUT_DOWN,
    '1'         : freevo.INPUT_1,
    '2'         : freevo.INPUT_2,
    '3'         : freevo.INPUT_3,
    '4'         : freevo.INPUT_4,
    '5'         : freevo.INPUT_5,
    '6'         : freevo.INPUT_6,
    '7'         : freevo.INPUT_7,
    '8'         : freevo.INPUT_8,
    '9'         : freevo.INPUT_9,
    '0'         : freevo.INPUT_0,
    'CH+'       : freevo.MENU_PAGEUP,
    'CH-'       : freevo.MENU_PAGEDOWN
    }

TV_EVENTS = {
    'STOP'      : freevo.STOP,
    'MENU'      : freevo.STOP,
    'EXIT'      : freevo.STOP,
    'SELECT'    : freevo.STOP,
    'PAUSE'     : freevo.PAUSE,
    'CH+'       : freevo.TV_CHANNEL_UP,
    'CH-'       : freevo.TV_CHANNEL_DOWN,
    'LEFT'      : freevo.Event(freevo.SEEK, -60),
    'RIGHT'     : freevo.Event(freevo.SEEK,  60),
    'REW'       : freevo.Event(freevo.SEEK, -10),
    'FFWD'      : freevo.Event(freevo.SEEK,  10),
    'DISPLAY'   : freevo.TOGGLE_OSD,
    '0'         : freevo.INPUT_0,
    '1'         : freevo.INPUT_1,
    '2'         : freevo.INPUT_2,
    '3'         : freevo.INPUT_3,
    '4'         : freevo.INPUT_4,
    '5'         : freevo.INPUT_5,
    '6'         : freevo.INPUT_6,
    '7'         : freevo.INPUT_7,
    '8'         : freevo.INPUT_8,
    '9'         : freevo.INPUT_9,
    }

VIDEO_EVENTS = {
    'PLAY'      : freevo.PLAY,
    'PAUSE'     : freevo.PAUSE,
    'STOP'      : freevo.STOP,
    'EXIT'      : freevo.STOP,
    'UP'        : freevo.PLAYLIST_PREV,
    'DOWN'      : freevo.PLAYLIST_NEXT,
    'CH+'       : freevo.PLAYLIST_PREV,
    'CH-'       : freevo.PLAYLIST_NEXT,
    'LEFT'      : freevo.Event(freevo.SEEK, -60),
    'RIGHT'     : freevo.Event(freevo.SEEK,  60),
    'REW'       : freevo.Event(freevo.SEEK, -10),
    'FFWD'      : freevo.Event(freevo.SEEK,  10),
    'ENTER'     : freevo.MENU,
    'DISPLAY'   : freevo.TOGGLE_OSD,
    'REC'       : freevo.STORE_BOOKMARK,
    '0'         : freevo.VIDEO_MANUAL_SEEK,
    'MENU'      : freevo.DVDNAV_MENU,
    'NEXT'      : freevo.NEXT,
    'PREV'      : freevo.PREV,
    '8'         : freevo.VIDEO_NEXT_AUDIOLANG,
    '9'         : freevo.VIDEO_NEXT_SUBTITLE,
    }

DVDNAV_EVENTS = {
    'PLAY'      : freevo.PLAY,
    'PAUSE'     : freevo.PAUSE,
    'STOP'      : freevo.STOP,
    'EXIT'      : freevo.STOP,
    'UP'        : freevo.DVDNAV_UP,
    'DOWN'      : freevo.DVDNAV_DOWN,
    'LEFT'      : freevo.DVDNAV_LEFT,
    'RIGHT'     : freevo.DVDNAV_RIGHT,
    'ENTER'     : freevo.DVDNAV_SELECT,
    'SELECT'    : freevo.DVDNAV_SELECT,
    'DISPLAY'   : freevo.TOGGLE_OSD,
    'MENU'      : freevo.DVDNAV_MENU,
    }

AUDIO_EVENTS = {
    'STOP'      : freevo.STOP,
    'EXIT'      : freevo.STOP,
    'PLAY'      : freevo.PLAY,
    'PAUSE'     : freevo.PAUSE,
    'LEFT'      : freevo.Event(freevo.SEEK, -60),
    'RIGHT'     : freevo.Event(freevo.SEEK,  60),
    'REW'       : freevo.Event(freevo.SEEK, -10),
    'FFWD'      : freevo.Event(freevo.SEEK,  10),
    'UP'        : freevo.PLAYLIST_PREV,
    'DOWN'      : freevo.PLAYLIST_NEXT,
    'CH+'       : freevo.PLAYLIST_PREV,
    'CH-'       : freevo.PLAYLIST_NEXT,
    '1'         : freevo.INPUT_1,
    '2'         : freevo.INPUT_2,
    '3'         : freevo.INPUT_3,
    '4'         : freevo.INPUT_4,
    '5'         : freevo.INPUT_5,
    '6'         : freevo.INPUT_6,
    '7'         : freevo.INPUT_7,
    '8'         : freevo.INPUT_8,
    '9'         : freevo.INPUT_9,
    }
    
IMAGE_EVENTS = {
    'STOP'      : freevo.STOP,
    'EXIT'      : freevo.STOP,
    'PLAY'      : freevo.PLAY,
    'PAUSE'     : freevo.PAUSE,
    'LEFT'      : freevo.Event(freevo.IMAGE_ROTATE, 'left'),
    'RIGHT'     : freevo.Event(freevo.IMAGE_ROTATE, 'right'),
    '1'         : freevo.Event(freevo.ZOOM_IN, 1.2),
    '2'         : freevo.Event(freevo.ZOOM_OUT, -1.2),
    '3'         : freevo.Event(freevo.ZOOM, 1.0),
    'DISPLAY'   : freevo.TOGGLE_OSD,
    'REC'       : freevo.IMAGE_SAVE,
    'UP'        : freevo.PLAYLIST_PREV,
    'DOWN'      : freevo.PLAYLIST_NEXT,
    'CH+'       : freevo.PLAYLIST_PREV,
    'CH-'       : freevo.PLAYLIST_NEXT
    }

IMAGE_ZOOM_EVENTS = {
    'STOP'      : freevo.STOP,
    'EXIT'      : freevo.STOP,
    'PLAY'      : freevo.PLAY,
    'PAUSE'     : freevo.PAUSE,
    'LEFT'      : freevo.Event(freevo.IMAGE_MOVE, -50,   0),
    'RIGHT'     : freevo.Event(freevo.IMAGE_MOVE,  50,   0),
    'UP'        : freevo.Event(freevo.IMAGE_MOVE,   0, -50),
    'DOWN'      : freevo.Event(freevo.IMAGE_MOVE,   0,  50),
    '1'         : freevo.Event(freevo.ZOOM_IN, 1.2),
    '2'         : freevo.Event(freevo.ZOOM_OUT, -1.2),
    '3'         : freevo.Event(freevo.ZOOM, 1.0),
    'DISPLAY'   : freevo.TOGGLE_OSD,
    'REC'       : freevo.IMAGE_SAVE,
    'CH+'       : freevo.PLAYLIST_PREV,
    'CH-'       : freevo.PLAYLIST_NEXT
    }

GAMES_EVENTS = {
    'EXIT'      : freevo.STOP,
    'STOP'      : freevo.STOP,
    'SELECT'    : freevo.STOP,
    'MENU'      : freevo.MENU,
}

GLOBAL_EVENTS = {
    'VOL+'             : freevo.MIXER_VOLUP,
    'VOL-'             : freevo.MIXER_VOLDOWN,
    'MUTE'             : freevo.MIXER_MUTE,
    'TOGGLE'           : freevo.TOGGLE_APPLICATION
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

