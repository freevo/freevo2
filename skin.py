#
# skin.py
#
# This is the Freevo top-level skin code.
#
# $Id$

# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os

# Various utilities
import util

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

###############################################################################

# Set up the mixer
mixer = mixer.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Create the OSD object
osd = osd.get_singleton()

 
# Module variable that contains an initialized Skin() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Skin()  # The Skin() class is defined in freevo_skin.py
        
    return _singleton


# This is the base skin class, it contains templates for the necessary
# functions etc.
class SkinBase:


    items_per_page = 10  # Used by the menu module
    
    def __init__(self):
       # Push main menu items
       pass


    # This function is called from the rc module and other places
    def HandleEvent(self, ev):
        # Handle event (remote control, timer, msg display...)
        # Some events are handled directly (volume control),
        # RC cmds are handled using the menu lib, and events
        # might be passed directly to a foreground application
        # that handles its' own graphics
        pass


    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        pass
    

    def DrawMP3(self, info):
        pass
    

# The actual skin code is imported from the skin dir (configurable)
# This has to be last in this file because of the dependencies
sys.path += config.OSD_SKIN_DIR
execfile(config.OSD_SKIN_DIR + '/freevo_skin.py', globals(), locals())
