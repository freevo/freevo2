#
# movie.py
#
# This is the Freevo Movie module. 
#
# $Id$

import sys
import random
import time, os

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The mplayer class
import mplayer


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the mplayer object
mplayer = mplayer.get_singleton()


#
# mplayer dummy
#
def play_movie(menuw=None, arg=None):
    mode = arg[0]
    filename = arg[1]
    playlist = arg[2]
    mplayer.play(mode, filename, playlist)


#
# The Movie module main menu
#
def main_menu(arg=None, menuw=None):

    items = []

    for (title, dir) in config.DIR_MOVIES:
        items += [menu.MenuItem('[%s]' % title, cwd, dir)]
    
    moviemenu = menu.Menu('MOVIE MAIN MENU', items)
    menuw.pushmenu(moviemenu)


#
# The change directory handling function
#
def cwd(arg=None, menuw=None):
    dir = arg

    dirnames = util.getdirnames(dir)
    files = util.match_files(dir, config.SUFFIX_MPLAYER_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        items += [menu.MenuItem(title, cwd, dirname)]
    
    for file in files:
        title = util.strip_suffix(os.path.basename(file))
        items += [menu.MenuItem(title, play_movie, ('video', file, files))]
    
    moviemenu = menu.Menu('MOVIE MENU', items)
    menuw.pushmenu(moviemenu)


