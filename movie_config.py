# The menu widget class
import menu

# The mplayer class
import mplayer

# XML support
import movie_xml

# RegExp
import re

from datatypes import *

menuw = menu.get_singleton()

class MplayerMovieInfo:
    def __init__(self):
        self.time = ""
        self.audio = []
        self.subtitles = []
        self.audio_selected = None
        self.subtitle_selected = None

        self.re_audio = re.compile("^\[open\] audio stream: [0-9] audio format:"+\
                                   "(.*)aid: ([0-9]*)").match
        self.re_subtitle = re.compile("^\[open\] subtitle.*: ([0-9]) language: "+\
                                      "([a-z][a-z])").match

    def parse(self, str):
        m = self.re_audio(str)
        if m:
            self.audio += [ (m.group(2), m.group(1)) ]
        m = self.re_subtitle(str)
        if m:
            self.subtitles += [ (m.group(1), m.group(2)) ]


    def to_string(self):
        ret = ""
        if self.audio_selected:
            ret += " -aid %s" % self.audio_selected
        if self.subtitle_selected:
            ret += " -sid %s" % self.subtitle_selected
        return ret

#
# Dummy for playing the movie
#

def play_movie(arg=None, menuw=None):
    (mode, file, playlist, repeat, start_time, mpinfo) = arg
    if not isinstance(file, FileInformation):
        file = FileInformation(mode, file)
    file.mplayer_config = mpinfo
    menuw.delete_menu()
    mplayer.get_singleton().play(mode, file, playlist, repeat, start_time)



#
# Audio menu and selection
#

def audio_selection(arg=None, menuw=None):
    (mpinfo, language) = arg
    mpinfo.audio_selected = language
    menuw.back_one_menu()

def audio_selection_menu(arg=None, menuw=None):
    items = []
    mpinfo = arg
    for a in mpinfo.audio:
        items += [ menu.MenuItem(a[1], audio_selection, (mpinfo, a[0])) ]
    moviemenu = menu.Menu('AUDIO MENU', items)
    menuw.pushmenu(moviemenu)
        

#
# Subtitle menu and selection
#

def subtitle_selection(arg=None, menuw=None):
    (mpinfo, language) = arg
    mpinfo.subtitle_selected = language
    menuw.back_one_menu()

def subtitle_selection_menu(arg=None, menuw=None):
    items = []
    mpinfo = arg
    items += [ menu.MenuItem("no subtitles", subtitle_selection, (mpinfo, None)) ]
    for s in mpinfo.subtitles:
        items += [ menu.MenuItem(s[1], subtitle_selection, (mpinfo, s[0])) ]
    moviemenu = menu.Menu('SUBTITLE MENU', items)
    menuw.pushmenu(moviemenu)
        


#
# config main menu
#

def config_main_menu(mode, file, playlist, repeat, mpinfo):
    next_start = 0
    items = []

    if mpinfo.audio:
        items += [ menu.MenuItem("Audio selection", audio_selection_menu, mpinfo) ]
        
    if mpinfo.subtitles:
        items += [ menu.MenuItem("Subtitle selection", subtitle_selection_menu, mpinfo) ]
        

    if mpinfo.time:
        m = re.compile("^A[: -]*([0-9]+)\.").match(mpinfo.time)
        if m:
            next_start = max(0, int(m.group(1)) - 1)
        if next_start:
            # XXX continue doesn't work good. We save the position where we stopped
            # XXX mplayer, but -ss seems to start on the next i-frame or so :-(
            items += [ menu.MenuItem("play: continue", play_movie,
                                     (mode, file, playlist, repeat, next_start, mpinfo)) ]
    
            items += [ menu.MenuItem("play: restart", play_movie,
                                     (mode, file, playlist, repeat, 0, mpinfo)) ]
    else:
        items += [ menu.MenuItem("play", play_movie,
                                 (mode, file, playlist, repeat, 0, mpinfo)) ]
        
    moviemenu = menu.Menu('CONFIG MENU', items)
    menuw.pushmenu(moviemenu)
    
