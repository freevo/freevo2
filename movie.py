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

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# Create the remote control object
rc = rc.get_singleton()

# Create the OSD object
osd = osd.get_singleton()

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
    mplayer_options = ""
    if len(arg) > 3:
        mplayer_options = arg[3]
    mplayer.play(mode, filename, playlist, 0, mplayer_options)


#
# mplayer dummy
#
def eventhandler(event = None, menuw=None, arg=None):
    rom = arg[0]
    if event == rc.EJECT:

        # find the drive
        pos = 0
        for (dir, name, tray) in config.ROM_DRIVES:
            if rom == dir:
                tray_open = tray
                config.ROM_DRIVES[pos] = (dir, name, (tray + 1) % 2)
                break
            pos += 1

        if tray_open:
            if DEBUG: print 'Inserting %s' % rom

            # XXX FIXME: this doesn't look very good, we need
            # XXX some sort of a pop-up widget
            osd.drawbox(osd.width/2 - 180, osd.height/2 - 30, osd.width/2 + 180,\
                        osd.height/2+30, width=-1,
                        color=((60 << 24) | osd.COL_BLACK))
            osd.drawstring('mounting %s' % rom, \
                           osd.width/2 - 160, osd.height/2 - 10,
                           fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
            osd.update()
            
            # close the tray and mount the cd
            os.system('eject -t %s' % rom)
            os.system('mount %s' % rom)
            
            item = menuw.all_items[menuw.all_items.index(menuw.menustack[-1].selected)]
            
            (type, label, image) = util.identifymedia(rom)
            if type == 'DVD':
                item.name = label
                item.action = play_movie
                item.arg = ('dvd', 1, [])
            elif type == 'VCD':
                item.name = label
                item.action = play_movie
                item.arg = ('vcd', 1, [])
            elif type == 'SVCD':
                item.name = label
                item.action = play_movie
                item.arg = ('vcd', 1, [])
            elif type != None:
                item.name = 'CD [%s]' % label
                item.action = cwd
                item.arg = rom
            else:
                item.name = '%s (no disc)' % name

            item.image = ('movie', image)
            menuw.refresh()

        else:
            if DEBUG: print 'Ejecting %s' % rom
            os.system('eject %s' % rom)
            item = menuw.all_items[menuw.all_items.index(menuw.menustack[-1].selected)]
            item.name = '%s (no disc)' % name
            item.image = None
            
            menuw.refresh()
        

#
# The Movie module main menu
#
def main_menu(arg=None, menuw=None):

    items = []

    for (title, dir) in config.DIR_MOVIES:
        items += [menu.MenuItem('[%s]' % title, cwd, dir)]


    if config.ROM_DRIVES != None: 
        for (dir, name, tray) in config.ROM_DRIVES:
            (type, label, image ) = util.identifymedia(dir)
            if type == 'DVD':
                m = menu.MenuItem(label, play_movie, ('dvd', 1, []), eventhandler, (dir,))
            elif type == 'VCD':
                m = menu.MenuItem(label, play_movie, ('vcd', 1, []), eventhandler, (dir,))
            elif type == 'SVCD':
                m = menu.MenuItem(label, play_movie, ('vcd', 1, []), eventhandler, (dir,))
            elif type != None:
                m = menu.MenuItem('CD [%s]' % label, cwd, dir, eventhandler, (dir,))
            else:
                m = menu.MenuItem('%s (no disc)' % name, None, None, eventhandler, (dir,))
            m.setImage(('movie', image))
            items += [m]
            
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
    mplayer_options = ""
    
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
        if node.name == u'crop':
            try:
                crop = "-vop crop=%s:%s:%s:%s " % \
                       (node.attrs[('', "width")], node.attrs[('', "height")], \
                        node.attrs[('', "x")], node.attrs[('', "y")])
                mplayer_options += crop
            except KeyError:
                pass
    return ( mode, first_file, playlist, mplayer_options )


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
        m = menu.MenuItem(title, cwd, dirname)
        if os.path.isfile(dirname+'/cover.png'): 
            m.setImage(('movie', (dirname+'/cover.png')))
        if os.path.isfile(dirname+'/cover.jpg'): 
            m.setImage(('movie', (dirname+'/cover.jpg')))

        items += [m]

    
    files = []

    # xml files
    for file in util.match_files(dir, config.SUFFIX_FREEVO_FILES):
        playlist = []

        title = first_file = ""
        image = None

        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
        except:
            print "XML file %s corrupt" % file
        else:
            if box.children[0].name == 'movie':
                for node in box.children[0].children:
                    if node.name == u'title':
                        title = node.textof()
                    elif node.name == u'cover' and \
                         os.path.isfile(os.path.join(dir,node.textof())):
                        image = os.path.join(dir, node.textof())
                    elif node.name == u'video':
                        (mode, first_file, playlist, mplayer_options) = \
                               XML_parseVideo(dir, mplayer_files, node)
                    elif node.name == u'info':
                        XML_parseInfo(node)

        # only add movies when we have all needed informations
        if title != "" and first_file != "":
            files += [ ( title, mode, first_file, playlist, mplayer_options, image ) ]

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
        files += [ ( title, 'video', file, mplayer_files, None, image ) ]


    # sort "normal" files and xml files by title
    files.sort(lambda l, o: cmp(l[0].upper(), o[0].upper()))

    # add everything to the menu
    for (title, mode, file, playlist, mplayer_options, image) in files:
        m = menu.MenuItem(title, play_movie, (mode, file, playlist, mplayer_options))
        m.setImage(('movie', image))
        items += [m]
    
    moviemenu = menu.Menu('MOVIE MENU', items, dir=dir)
    menuw.pushmenu(moviemenu)
