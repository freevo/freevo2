#
# mp3.py
#
# This is the Freevo MP3 module. 
#

import sys
import random
import time, os, glob
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
# Get all mp3 files in the directory
#
#
def getsoundfiles(dir):
    files = glob.glob(dir + '/*.[mM][pP]3')
    files.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return files


#
# Get all playlists in the directory
#
#
def getplaylists(dir):
    files = glob.glob(dir + '/*.[mM]3[uU]')
    files.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return files


#
# Get all subdirectories in the given directory
#
#
def getdirnames(dir):
    files = glob.glob(dir + '/*')
    dirnames = filter(lambda d: os.path.isdir(d), files)
    dirnames.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return dirnames

        

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

    dirnames = getdirnames(dir)
    playlists = getplaylists(dir)
    files = getsoundfiles(dir)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
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

    #
    # XXX local stuff to convert from playlist generated from a
    # XXX network mapped drive on a Win98 box with winamp
    #
    playlist_filenames = []
    for line in playlist_lines:
        line2 = line.replace('\\', '/')
        line3 = line2.replace('/Music/', '/hdc/mary/')
        playlist_filenames += [line3]
    
    items = []

    for filename in playlist_filenames:
        songname = util.strip_suffix(os.path.basename(filename))
        items += [menu.MenuItem(songname, play_mp3, (filename, playlist_filenames))]

    title = os.path.basename(arg)[:-4]
    
    mp3menu = menu.Menu('MP3 PLAYLIST: %s' % title, items)
    menuw.pushmenu(mp3menu)
