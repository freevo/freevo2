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

# XML support
from xml.utils import qp_xml

# RegExp
import re



# compile the regexp
TV_SHOW_REGEXP_MATCH = re.compile("^.*" + config.TV_SHOW_REGEXP).match
TV_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + config.TV_SHOW_REGEXP + "[\.\- ]*").split


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


# FIXME: MAYBE THIS SHOULD MOVE TO UTILS

def make_filename(dir, file):
    if file[0] == '/':
        return file
    elif file[-1] == '/':
        return dir + file
    else:
        return dir + '/' + file

#
# parse <video> tag    
#
def XML_parseVideo(dir, mplayer_files, video_node):
    first_file = ""
    playlist = []

    for node in video_node.children:
        if node.name == u'files':
            for file_nodes in node.children:
                if file_nodes.name == u'filename':
                    if first_file == "":
                        first_file = make_filename(dir, file_nodes.textof())
                try: mplayer_files.remove(make_filename(dir,file_nodes.textof()))
                except ValueError: pass
                playlist += [make_filename(dir, file_nodes.textof())]

    return ( first_file, playlist)

#
# parse <info> tag (not implemented yet)
#
def XML_parseInfo(info_node):
    for node in info_node.children:
        pass

        
#
# The change directory handling function
#
def cwd(arg=None, menuw=None):
    dir = arg

    dirnames = util.getdirnames(dir)
    mplayer_files = util.match_files(dir, config.SUFFIX_MPLAYER_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        items += [menu.MenuItem(title, cwd, dirname)]
    
    files = []

    # xml files
    for file in util.match_files(dir, config.SUFFIX_FREEVO_FILES):
        playlist = []

        parser = qp_xml.Parser()
        box = parser.parse(open(file).read())
        title = first_file = ""
        image = None

        if box.children[0].name == 'movie':
            for node in box.children[0].children:
                if node.name == u'title':
                    title = node.textof()
                elif node.name == u'cover' and \
                     os.path.isfile(make_filename(dir,node.textof())):
                    image = make_filename(dir, node.textof())
                elif node.name == u'video':
                    (first_file, playlist) = XML_parseVideo(dir, mplayer_files, node)
                elif node.name == u'info':
                    XML_parseInfo(node)

        # only add movies when we have all needed informations
        if title != "" and first_file != "":
            files += [ ( title, first_file, playlist, image ) ]

    # "normal" movie files
    for file in mplayer_files:
        title = os.path.splitext(os.path.basename(file))[0]
        image = None

        # find image for tv show and build new title
        if TV_SHOW_REGEXP_MATCH(title):
            show_name = TV_SHOW_REGEXP_SPLIT(os.path.basename(title))
            title = show_name[0] + " " + show_name[1] + "x" + show_name[2] + " - " + \
                    show_name[3] 

            if os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()):
                image = (config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()
            elif os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()):
                image = (config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()


        # find image for this file
        if os.path.isfile(os.path.splitext(file)[0] + ".png"):
            image = os.path.splitext(file)[0] + ".png"
        elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
            image = os.path.splitext(file)[0] + ".jpg"

        # add file to list
        files += [ ( title, file, mplayer_files, image ) ]


    # sort "normal" files and xml files by title
    files.sort(lambda l, o: cmp(l[0].upper(), o[0].upper()))

    # add everything to the menu
    for (title, file, playlist, image) in files:
        m = menu.MenuItem(title, play_movie, ('video', file, playlist))
        m.setImage(image)
        items += [m]
    
    moviemenu = menu.Menu('MOVIE MENU', items)

    if os.path.isfile(make_filename(dir, "background.jpg")):
        moviemenu.setBackgroundImage(make_filename(dir, "background.jpg"))
    elif os.path.isfile(make_filename(dir, "background.png")):
        moviemenu.setBackgroundImage(make_filename(dir, "background.png"))

    menuw.pushmenu(moviemenu)
