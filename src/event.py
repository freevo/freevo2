class Event:
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



    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not other:
            return 1
        if isinstance(other, Event):
            return self.name != other.name
        return self.name != other


MIXER_VOLUP        = Event('MIXER_VOLUP')
MIXER_VOLDOWN      = Event('MIXER_VOLDOWN')
MIXER_MUTE         = Event('MIXER_MUTE')

PLAYLIST_NEXT      = Event('PLAYLIST_NEXT')
PLAYLIST_PREV      = Event('PLAYLIST_PREV')

EJECT              = Event('EJECT')

MENU_LEFT          = Event('MENU_LEFT')
MENU_RIGHT         = Event('MENU_RIGHT')
MENU_UP            = Event('MENU_UP')
MENU_DOWN          = Event('MENU_DOWN')
MENU_PAGEUP        = Event('MENU_PAGEUP')
MENU_PAGEDOWN      = Event('MENU_PAGEDOWN')

MENU_GOTO_MAINMENU = Event('MENU_GOTO_MAINMENU')
MENU_BACK_ONE_MENU = Event('MENU_BACK_ONE_MENU')

MENU_SELECT        = Event('MENU_SELECT')
MENU_PLAY_ITEM     = Event('MENU_PLAY_ITEM')
MENU_SUBMENU       = Event('MENU_SUBMENU')
MENU_CHANGE_STYLE  = Event('MENU_CHANGE_STYLE')

TV_START_RECORDING = Event('TV_START_RECORDING')
TV_CHANNEL_UP      = Event('TV_CHANNEL_UP')
TV_CHANNEL_DOWN    = Event('TV_CHANNEL_DOWN')

SEEK               = Event('SEEK')
PLAY               = Event('PLAY')
PAUSE              = Event('PAUSE')
STOP               = Event('STOP')
STORE_BOOKMARK     = Event('STORE_BOOKMARK')
MENU               = Event('MENU')
TOGGLE_OSD         = Event('TOGGLE_OSD')

GAMES_CONFIG       = Event('GAMES_CONFIG')
GAMES_RESET        = Event('GAMES_RESET')
GAMES_SNAPSHOT     = Event('GAMES_SNAPSHOT')

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

BUTTON                 = Event('BUTTON')

global_events = {
    'VOLUP'     : MIXER_VOLUP,
    'VOLDOWN'   : MIXER_VOLDOWN,
    'MUTE'      : MIXER_MUTE
    }

menu_events = {
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

input_events = {
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

tv_events = {
    'STOP'      : STOP,
    'MENU'      : STOP,
    'EXIT'      : STOP,
    'SELECT'    : STOP,
    'CH+'       : TV_CHANNEL_UP,
    'CH-'       : TV_CHANNEL_DOWN
    }

video_events = {
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
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
    }

audio_events = {
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
    
image_events = {
    'STOP'      : STOP,
    'EXIT'      : STOP,
    'PLAY'      : PLAY,
    'PAUSE'     : PAUSE,
    'LEFT'      : Event(IMAGE_ROTATE, arg='left'),
    'RIGHT'     : Event(IMAGE_ROTATE, arg='right'),
    'DISPLAY'   : TOGGLE_OSD,
    'REC'       : IMAGE_SAVE,
    'UP'        : PLAYLIST_PREV,
    'DOWN'      : PLAYLIST_NEXT,
    'CH+'       : PLAYLIST_PREV,
    'CH-'       : PLAYLIST_NEXT
    }

games_events = {
    'STOP'      : STOP,
    'SELECT'    : STOP,
    'MENU'      : MENU,
    'DISPLAY'   : GAMES_CONFIG,
    'ENTER'     : GAMES_RESET
    }

default_events = {
    'menu'    : menu_events,
    'input'   : input_events,
    'video'   : video_events,
    'audio'   : audio_events,
    'games'   : games_events,
    'image'   : image_events
    }


PLAY_END = Event('PLAY_END')
USER_END = Event('USER_END')
DVD_PROTECTED = Event('DVD_PROTECTED')
AUDIO_PLAY_END = Event('AUDIO_PLAY_END')
