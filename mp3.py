#
# mp3.py
#
# This is the Freevo MP3 module. 
#
# $Id$

import sys
import random
import time, os
import string, popen2, fcntl, select, struct

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The mpg123 application
import mpg123

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


# Create the mpg123 object
mpg123 = mpg123.get_singleton()


#
# Play an MP3 file using the slave mode interface in the mpg123 application.
# The argument is a tuple containing the file to be played and a list of the
# entire playlist so that the player can start on the next one.
def play_mp3(menuw=None, arg=None):
    file = arg[0]
    playlist = arg[1]
    mpg123.play(file, playlist)
    

#
# The MP3 module main menu
#
def main_menu(arg=None, menuw=None):

    items = []

    for (title, dir) in config.DIR_MP3:
        items += [menu.MenuItem('[%s]' % title, cwd, dir)]
    
    mp3menu = menu.Menu('MP3 MAIN MENU', items)
    menuw.pushmenu(mp3menu)


#
# The MP3 module change directory handling function
#
def cwd(arg=None, menuw=None):
    dir = arg

    dirnames = util.getdirnames(dir)
    playlists = util.match_files(dir, config.SUFFIX_MPG123_PLAYLISTS)
    files = util.match_files(dir, config.SUFFIX_MPG123_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        if os.path.isfile(dirname+'/cover.png'): 
        	items += [menu.MenuItem(title, cwd, dirname,(dirname+'/cover.png'),1,1)]
	else:
		items += [menu.MenuItem(title, cwd, dirname)]
    
    for playlist in playlists:
        title = 'PL: ' + os.path.basename(playlist)[:-4]
        items += [menu.MenuItem(title, m3u_playlist, playlist)]
    
    for file in files:
        title = os.path.basename(file)[:-4]
        items += [menu.MenuItem(title, play_mp3, (file, files))]
    
    mp3menu = menu.Menu('MP3 MENU', items)
    menuw.pushmenu(mp3menu)


#
# The MP3 module playlist handling
#
def m3u_playlist(arg=None, menuw=None):

    playlist_lines_dos = map(lambda l: l.strip(), open(arg).readlines())

    playlist_lines = filter(lambda l: l[0] != '#', playlist_lines_dos)

    items = []

    for filename in playlist_lines:
        songname = util.strip_suffix(os.path.basename(filename))
        items += [menu.MenuItem(songname, play_mp3, (filename, playlist_lines))]

    title = os.path.basename(arg)[:-4]
    
    mp3menu = menu.Menu('MP3 PLAYLIST: %s' % title, items)
    menuw.pushmenu(mp3menu)
