#if 0 /*
# -----------------------------------------------------------------------
# skin_krister1.py - This is the Freevo krister skin no 1
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2002/08/17 18:36:53  krister
# Changed to use ../xml/type1/xml_skin.py.
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
# ----------------------------------------------------------------------- */
#endif


# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os, copy

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
sys.path.append('skins/xml/type1')
import xml_skin

# Set to 1 for debug output
DEBUG = 0

TRUE = 1
FALSE = 0

if not 'OSD_SDL' in dir(config): # XXX kludge
    raise 'SDL OSD Server required for this skin!'

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
            if val.title.text:
                menu.heading = val.title.text
            osd.drawstring(menu.heading, osd.width/2, val.title.y, val.title.color,
                           font=val.title.font,
                           ptsize=val.title.size, align='center')

        # Draw the menu choices for the main selection
        if len(menuw.menustack) == 1:
            is_main = 1 # Is main menu, kludge
        else:
            is_main = 0

        if is_main:
            # Main menu items
            ptscale = 2.0
            dx = 150 # Extra x indent, kludge
            icon_size = 75

            if len(menuw.menu_items) == 5:
                icon_size = 64
        else:
            # Sub menus
            ptscale = 1.0
            dx = 0
            icon_size = 25

        x0 = val.items.x + dx
        y0 = val.items.y
        selection_height = val.items.height

        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)

        # image to display
        image = None
        
        fontsize = val.items.size*ptscale
        
        # Handle multiple columns in the menu widget.
        # Only the first column is highlighted, and all columns have
        # their left edges vertically aligned
        rows = []
        maxcols = 0  # Largest number of columns in any row
        for item in menuw.menu_items:
            row = item.name.split('\t')
            rows += [row]
            maxcols = max(maxcols, len(row))
            
        # Determine the width of the widest column string
        maxwidth = 0
        for row in rows:
            w, h = osd.stringsize(row[0], font=val.items.font,
                                  ptsize=fontsize)
            maxwidth = max(maxwidth, w)
            
        # Draw the menu items, with icons if any
        row = 0
        for choice in menuw.menu_items:
	    if choice.icon != None:
                icon_x = x0 - icon_size - 10 - 25*is_main
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size),
                               icon_x, y0)

            # Draw the selection
            osd.drawstring(rows[row][0], x0, y0, val.items.color,
                           font=val.items.font,
                           ptsize=fontsize)
            
	    if menu.selected == choice:
                osd.drawbox(x0 - 3 - 5*is_main, y0 - 3,
                            x0 + maxwidth + 3 + 5*is_main,
                            y0 + fontsize*1.5 + 1 + 2*is_main, width=-1,
                            color=((160 << 24) | val.items.sel_color))

                image = choice.image

            y0 += spacing
            row += 1

        x0 += maxwidth + 8
        
        # Draw the additional text columns with vertical alignment
        for col in range(1, maxcols):

            y0 = val.items.y  # Start over from the top
            
            # Determine the width of the widest column string
            maxwidth = 0
            for row in rows:
                if col >= len(row): continue # Not all rows are same length
                
                w, h = osd.stringsize(row[col], font=val.items.font,
                                      ptsize=fontsize)
                maxwidth = max(maxwidth, w)

            # Draw the column strings for all rows
            for row in rows:
                if col < len(row): 
                    osd.drawstring(row[col], x0, y0, val.items.color,
                                   font=val.items.font,
                                   ptsize=fontsize)
                y0 += spacing

            # Update x for the next column
            x0 += maxwidth + 8


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
