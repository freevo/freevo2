#if 0
# -----------------------------------------------------------------------
# skin_main.py - Freevo main skin no 1
# -----------------------------------------------------------------------
# $Id$
#
# Notes:   This is the default skin
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.14  2002/08/18 06:10:59  krister
# Converted tabs to spaces. Please use tabnanny in the future!
#
# Revision 1.13  2002/08/17 18:37:21  krister
# Changed to use ../xml/type1/xml_skin.py.
#
# Revision 1.12  2002/08/11 08:11:03  dischi
# moved the XML parsing to an extra file and the file 768x576.xml
# to the directory skins/xml
#
#
#
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
# -----------------------------------------------------------------------
#endif



# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os, copy, re

# Various utilities
import util

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# XML parser for skin informations
#
# If you copy the main1 skin and want to change the xml handling too,
# you can use 'import my_xml_skin as xml_skin' here and remove the
# sys.path.insert()
#
sys.path.append('skins/xml/type1')
import xml_skin

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


###############################################################################
# Skin main functions
###############################################################################

class Skin:

    settings = xml_skin.XMLSkin()
    settings.load(config.SKIN_XML_FILE)

    items_per_page = 13


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



    # Parse XML files with additional settings
    # TODO: parse also parent directories
    def LoadSettings(self, dir):
        if dir and os.path.isfile(os.path.join(dir, "skin.xml")):
            settings = copy.copy(self.settings)
            settings.load(os.path.join(dir, "skin.xml"), 1)
            return settings
        return None



    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        osd.clearscreen(osd.COL_WHITE)

        menu = menuw.menustack[-1]

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        # get the settings
        if menu.skin_settings:
            val = menu.skin_settings.menu
        else:
            val = self.settings.menu

        if val.bgbitmap[0]:
            apply(osd.drawbitmap, (val.bgbitmap, -1, -1))
        
        # Menu heading
        if val.title.visible:
            if val.title.text: menu.heading = val.title.text
            osd.drawstring(menu.heading, val.title.x, val.title.y, val.title.color,
                           font=val.title.font,
                           ptsize=val.title.size)

        # Draw the menu choices for the main selection
        x0 = val.items.x
        y0 = val.items.y
        selection_height = val.items.height
        icon_size = 75

        if len(menuw.menu_items) == 5:
            icon_size = 64

        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)

        # image to display
        image = None
        
        for choice in menuw.menu_items:
            if len(menuw.menustack) == 1:
                ptscale = 2.0
            else:
                ptscale = 1.0
            fontsize = val.items.size*ptscale
            w = 0
            h = 0
            if choice.icon != None: 
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size), x0, y0)
                w = icon_size + 20
                h = 5
                
            osd.drawstring(choice.name, (x0+w+10), y0+h, val.items.color,
                           font=val.items.font,
                           ptsize=fontsize)
            if menu.selected == choice:
                osd.drawbox(x0 - 8 + w, y0 - 3 + h, x0 - 8 + val.items.sel_length,\
                            y0 + fontsize*1.5 + h, width=-1,
                            color=((160 << 24) | val.items.sel_color))

                image = choice.image


            y0 += spacing


        # draw the image
        if image:
            (type, image) = image
        if image:
            if type == 'photo' and val.cover_image.visible:
                thumb = util.getExifThumbnail(image, val.cover_image.width, \
                                              val.cover_image.height)
                if thumb:
                    osd.drawbitmap(thumb, val.cover_image.x, val.cover_image.y)
            elif type == 'movie' and val.cover_movie.visible:
                osd.drawbitmap(\
                        util.resize(image, val.cover_movie.width, \
                                    val.cover_movie.height),\
                        val.cover_movie.x, val.cover_movie.y)
            elif type == 'music' and val.cover_music.visible:
                osd.drawbitmap(\
                        util.resize(image, val.cover_music.width, \
                                    val.cover_music.height),\
                        val.cover_music.x, val.cover_music.y)
            

        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y
        
        for item in menuw.nav_items:
            osd.drawstring(item.name, x0, y0, val.submenu.color,
                           font=val.submenu.font,
                           ptsize=val.submenu.size)
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.sel_length, \
                            y0 + val.submenu.size*1.5,
                            width=-1,
                            color=((160 << 24) | val.submenu.sel_color))
            x0 += 190

        osd.update()
        



    def DrawMP3(self, info):

        val = self.settings.mp3

        left = 170

        if info.drawall:
            osd.clearscreen()

            if val.bgbitmap[0]:
                apply(osd.drawbitmap, (val.bgbitmap, -1, -1))


            # Display the cover image file if it is present
            if info.image:
                # Check size to adjust image placement 
                (w, h) = util.pngsize(info.image)
                
                # Calculate best image placement
                logox = int(osd.width) - int(w) - 55
            
                # Draw border for image
                osd.drawbox(int(logox), 100, (int(logox) + int(w)), 100 + int(h),
                            width=6, color=0x000000)
                osd.drawbitmap(info.image, logox, 100)

            osd.drawstring(info.filename, 30, 520)

            osd.drawstring('Title:', 30, 100)
            osd.drawstring('%s ' % info.title, left, 100)
        
            osd.drawstring('Artist:', 30, 130)
            osd.drawstring('%s ' % info.artist, left, 130)
        
            osd.drawstring('Album:', 30, 160)
            osd.drawstring('%s ' % info.album, left, 160)
        
            osd.drawstring('Year:', 30, 190)
            osd.drawstring('%s ' % info.year, left, 190)
        
            osd.drawstring('Track:', 30, 220)
            osd.drawstring('%s ' % info.track, left, 220)


            osd.drawstring('Elapsed:', 30, 300, osd.default_fg_color)
            osd.drawstring('Remain:', 30, 340, osd.default_fg_color)
            osd.drawstring('Done:', 30, 380, osd.default_fg_color)

        else:
            # Erase the portion that will be redrawn
            if val.bgbitmap[0]:
                osd.drawbitmap( val.bgbitmap, left, 300, None, left,
                                300, 100, 100 )

        # XXX I changed this because round rounds up on 3.58 etc. instead
        # XXX of giving us the desired "round down modulo" effect.
        el_min  = int(info.elapsed)/60
        el_sec  = int(info.elapsed)%60
        rem_min = int(info.remain)/60
        rem_sec = int(info.remain)%60

        osd.drawstring('%s:%02d   ' % (el_min, el_sec), left, 300,
                       osd.default_fg_color)
        
        osd.drawstring('%s:%02d   ' % (rem_min,rem_sec), left, 340,
                       osd.default_fg_color)
        
        osd.drawstring('%0.1f%%   ' % info.done, left, 380,
                       osd.default_fg_color)

        # Draw the progress bar
        osd.drawbox(33, 440, 635, 460, width = 3)
        osd.drawbox(34, 441, 634, 459, width = -1, color = osd.default_bg_color)
        pixels = int(round((info.done) * 6.0))
        osd.drawbox(34, 441, 34 + pixels, 459, width = -1, color = osd.COL_BLUE)

        osd.update()
    
