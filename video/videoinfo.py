import os
import re

import config
import util
import mplayer

# XML support
from xml.utils import qp_xml

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import menu
import rc
rc         = rc.get_singleton()

from menu import Info


class VideoInfo(Info):
    def __init__(self, files):
        Info.__init__(self)
        self.type  = 'video'            # fix value
        self.mode  = 'file'             # file, dvd or vcd
        self.files = files

        if isinstance(files, list):
            file = files[0]
        elif not files:
            file = "unknown"
        else:
            file = files
            
        self.xml_file = None

        self.name    = os.path.splitext(os.path.basename(file))[0]
        # find image for tv show and build new title
        if config.TV_SHOW_REGEXP_MATCH(self.name):
            show_name = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(self.name))
            self.name = show_name[0] + " " + show_name[1] + "x" + show_name[2] +\
                         " - " + show_name[3] 

            if os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()):
                self.image = (config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()
            elif os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()):
                self.image = (config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()

        # find image for this file
        if os.path.isfile(os.path.splitext(file)[0] + ".png"):
            self.image = os.path.splitext(file)[0] + ".png"
        elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
            self.image = os.path.splitext(file)[0] + ".jpg"


        self.mplayer_options = None

        self.url     = ''
        self.genre   = ''
        self.tagline = ''
        self.plot    = ''
        self.runtime = ''
        self.year    = ''
        self.rating  = ''

        self.rom_id    = []
        self.rom_label = []

        # interactive stuff, parsed my mplayer
        self.current_playtime = 0
        self.available_audio_tracks = []
        self.available_subtitles = []
        self.available_chapters = 0

        self.action = self.play
        self.video_player = mplayer.get_singleton()

    # ------------------------------------------------------------------------
    # actions:

    def play(self, arg=None, menuw=None):
        print "now playing %s" % self.files

        if isinstance(self.files, list):
            self.current_file = self.files[0]
        else:
            self.current_file = self.files

        self.video_player.play(self.current_file, self.mplayer_options, self)

        
    def eventhandler(self, event):
        print "event %s for %s" % (event , self.name)

        # PLAY_END: do have have to play another file?
        if event == rc.PLAY_END:
            if isinstance(self.files, list):
                pos = self.files.index(self.current_file)
                if pos < len(self.files)-1:
                    self.current_file = self.files[pos+1]
                    print "playing next file"
                    self.video_player.play(self.current_file, self.mplayer_options, self)
                    return TRUE

            menuwidget = menu.get_singleton()
            menuwidget.refresh()
            return TRUE
            
        return FALSE
        

