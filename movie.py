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



#
# parse <video> tag    
#
def XML_parseVideo(dir, mplayer_files, video_node):
    first_file = ""
    playlist = []
    mode = 'video'
    add_to_path = dir
    
    for node in video_node.children:
        if node.name == u'dvd':
            mode = 'dvd'
            first_file = "1"
        if node.name == u'vcd':
            mode = 'vcd'
            first_file = "1"
        if node.name == u'cd':
            add_to_path = config.CD_MOUNT_POINT
        if node.name == u'files':
            for file_nodes in node.children:
                if file_nodes.name == u'filename':
                    if first_file == "":
                        first_file = os.path.join(add_to_path, file_nodes.textof())
                try: mplayer_files.remove(os.path.join(add_to_path,file_nodes.textof()))
                except ValueError: pass
                playlist += [os.path.join(add_to_path, file_nodes.textof())]

    return ( mode, first_file, playlist)

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
                     os.path.isfile(os.path.join(dir,node.textof())):
                    image = os.path.join(dir, node.textof())
                elif node.name == u'video':
                    (mode, first_file, playlist) = XML_parseVideo(dir, mplayer_files, node)
                elif node.name == u'info':
                    XML_parseInfo(node)

        # only add movies when we have all needed informations
        if title != "" and first_file != "":
            files += [ ( title, mode, first_file, playlist, image ) ]

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
        files += [ ( title, 'video', file, mplayer_files, image ) ]


    # sort "normal" files and xml files by title
    files.sort(lambda l, o: cmp(l[0].upper(), o[0].upper()))

    # add everything to the menu
    for (title, mode, file, playlist, image) in files:
        m = menu.MenuItem(title, play_movie, (mode, file, playlist))
        m.setImage(('cover', image))
        items += [m]
    
    moviemenu = menu.Menu('MOVIE MENU', items)

    if os.path.isfile(os.path.join(dir, "background.jpg")):
        moviemenu.setBackgroundImage(os.path.join(dir, "background.jpg"))
    elif os.path.isfile(os.path.join(dir, "background.png")):
        moviemenu.setBackgroundImage(os.path.join(dir, "background.png"))

    menuw.pushmenu(moviemenu)
