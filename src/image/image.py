#if 0 /*
# -----------------------------------------------------------------------
# image.py - This is the Freevo Image module. 
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

import os
import util

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The menu widget class
import menu

# The Skin
import skin

import mediamenu
import playlist
import imageitem
import traceback

# Extended Menu
import ExtendedMenu
import ExtendedMenu_Image

import interface

from item import Item

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

menuwidget = menu.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

skin = skin.get_singleton()

# Set up the extended menu
view = ExtendedMenu_Image.ExtendedMenuView_Image()
info = ExtendedMenu_Image.ExtendedMenuInfo_Image()
listing = ExtendedMenu_Image.ExtendedMenuListing_Image()
em = ExtendedMenu_Image.ExtendedMenu_Image(view, info, listing)

def refresh():
     em.refresh()


def eventhandler(event):
    if em.eventhandler(event) == 1:
         rc.app = None
         menuwidget.refresh()
    

def main_menu(arg, menuw):

    skin.PopupBox('Preparing the image browser') 

    rc.app = eventhandler

    files = config.DIR_IMAGES
    item = mediamenu.DirItem('', None, name = 'Root', display_type = 'dir')
    items = [ ]
    # add default items
    dirs = [ ]
    pls = [ ]
    imgs = [ ]
    for i in files:
        try:
            (title, file) = i
            if os.path.isdir(file) and os.path.basename(file) != '.xvpics':
                 dirs += [  mediamenu.DirItem(file, item, name = title,
                                              display_type = 'image') ]
                 
            elif util.match_suffix(file, config.SUFFIX_IMAGE_SSHOW):
                 pl = playlist.Playlist(file, item)
                 pl.name = title
                 pls += [ pl ]
                 
                 
            elif util.match_suffix(file, config.SUFFIX_IMAGE_FILES):                 
                 imgs += [ imageitem.ImageItem(file, item, name = title) ]
        except:
            traceback.print_exc()

    dirs.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))
    pls.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))
    imgs.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))

    items += dirs + pls + imgs

    if len(items) > 0:
        listing.ToListing([items, 0, 0, None])
    else:
        listing.ToListing([items, None, None, None])

    em.eventhandler(rc.UP)
    

    em.refresh()


