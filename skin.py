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

# The actual skin implementation is imported from the file
# as defined in freevo_config.py
sys.path += [os.path.dirname(config.OSD_SKIN)]
modname = os.path.basename(config.OSD_SKIN)[:-3]
exec('import ' + modname  + ' as skinimpl')

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

# Create the skin implementation object
impl = skinimpl.Skin()

OSD_DEFAULT_FONTNAME = impl.OSD_FONTNAME
OSD_DEFAULT_FONTSIZE = impl.OSD_FONTSIZE
items_per_page = impl.items_per_page


# This function is called from the rc module and other places
def HandleEvent(ev):
    # Handle event (remote control, timer, msg display...)
    # Some events are handled directly (volume control),
    # RC cmds are handled using the menu lib, and events
    # might be passed directly to a foreground application
    # that handles its' own graphics
    impl.HandleEvent(ev)


# Load special settings for this menu
def ParseXML(file):
    return impl.ParseXML(file)


# Called from the MenuWidget class to draw a menu page on the
# screen
def DrawMenu(menuw):
    impl.DrawMenu(menuw)


# Called from the MP3 player to update the MP3 info
def DrawMP3(info):
    impl.DrawMP3(info)
