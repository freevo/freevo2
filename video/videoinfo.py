import os
import re

import config
import util
import mplayer

# XML support
from xml.utils import qp_xml

# Set to 1 for debug output
DEBUG = config.DEBUG

from menu import Info


class VideoInfo(Info):
    def __init__(self, files):
        Info.__init__(self)
        self.mode  = 'video'
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

        self.action = self.play
        self.video_player = mplayer.get_singleton()

    # ------------------------------------------------------------------------
    # actions:

    def play(self, arg=None, menuw=None):
        print "now playing %s" % self.files

    def eventhandler(self, event):
        print "eventhandler %s" % self.name

        

