#if 0
# -----------------------------------------------------------------------
# skin_dischi1.py - Test skin from Dischi
# -----------------------------------------------------------------------
# $Id$
#
# Notes:   This skin is for the OSD_SDL interface. The idea is copied from
#          krister1. The selection has the length definied in the XML file
#          but if the text is to long, it will be shorten to fit the
#          selection / the screen. One change to the rows with \t: if there
#          is an item without \t it is ignored by the calculations. This is
#          needed for \t in series names and a mix between nornale files and
#          series.
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2002/08/11 10:36:23  dischi
# bugfix
#
# Revision 1.3  2002/08/11 09:37:04  dischi
# A test skin for the pyGame interface. Some code is taken from
# krister1:
#
# o \t aligns like krister1 but when there is an item without a \t it is
#   ignored by the generation of the row width. This is needed when you
#   mix series and other movies or directories in the movie browser.
#
# o The selection is not as long as the longest text, the text is
#   shorten to the length of the selection. Usefull for long movie
#   titles. If a title is shorten, ... will be added.
#
# o If there is one item with an image in the directory, the selection
#   will be shorten to avoid an overlapping from image and
#   selection/text
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

# Needed stuff from main1
sys.path += ['skins/main1']
import skin_main1
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

class Skin(skin_main1.Skin):

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

        if len(menuw.menustack) == 1:
            ptscale = 2.0
        else:
            ptscale = 1.0

        # Draw the menu choices for the main selection
        x0 = val.items.x
        y0 = val.items.y
        selection_height = val.items.height
        icon_size = 75

        fontsize = val.items.size*ptscale
        
        if len(menuw.menu_items) == 5:
            icon_size = 64

        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)


        image_x = 0
        selection_length = val.items.sel_length

        # display the image and store the x0 position of the image
        for item in menuw.menu_items:
            image = item.image
            if image:
                (type, image) = image
            if image:
                if type == 'photo' and val.cover_image.visible:
                    image_x = val.cover_image.x
                    if menu.selected == item:
                        thumb = util.getExifThumbnail(image, val.cover_image.width, \
                                                      val.cover_image.height)
                        if thumb:
                            osd.drawbitmap(thumb, val.cover_image.x, val.cover_image.y)
                elif type == 'movie' and val.cover_movie.visible:
                    image_x = val.cover_movie.x
                    if menu.selected == item:
                        osd.drawbitmap(util.resize(image, val.cover_movie.width, \
                                                   val.cover_movie.height),\
                                       val.cover_movie.x, val.cover_movie.y)

                elif type == 'music' and val.cover_music.visible:
                    image_x = val.cover_music.x
                    if menu.selected == item:
                        osd.drawbitmap(util.resize(image, val.cover_music.width, \
                                                   val.cover_music.height),\
                                       val.cover_music.x, val.cover_music.y)

            
        # if there is an image and the selection will be cover the image
        # shorten the selection
        if image_x and x0 - 8 + selection_length > image_x - 30:
            selection_length = image_x - 30 - x0 + 8

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
            if len(row) > 1: # ignore items without \t
                w, h = osd.stringsize(row[0], font=val.items.font,
                                      ptsize=fontsize)
                maxwidth = max(maxwidth, w)


        # Draw the first row
        row = 0
        for choice in menuw.menu_items:
	    w = 0
	    h = 0

	    if choice.icon != None: 
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size), x0, y0)
                w = icon_size + 20
                h = 5
                
	    if menu.selected == choice:
                osd.drawbox(x0 - 8 + w, y0 - 3 + h, x0 - 8 + selection_length,\
                            y0 + fontsize*1.5 + h, width=-1,
                            color=((160 << 24) | val.items.sel_color))

                image = choice.image

            # if there is only one col in this row, shorten the entry
            # to fit the selection
            if len(rows[row]) == 1:
                font_w, font_h = osd.stringsize(rows[row][0], font=val.items.font,
                                                ptsize=fontsize)
                if font_w + x0 - val.items.x + 26 > selection_length:
                    rows[row][0] = rows[row][0] + "..."
                    
                while font_w + x0 - val.items.x + 26 > selection_length:
                    rows[row][0] = rows[row][0][0:-4] + "..."
                    font_w, font_h = osd.stringsize(rows[row][0], font=val.items.font,
                                                    ptsize=fontsize)

            osd.drawstring(rows[row][0], (x0+w+10), y0+h, val.items.color,
                           font=val.items.font,
                           ptsize=fontsize)
                
            y0 += spacing
            row += 1



        x0 += maxwidth + 8 + 10
        
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
                if col < len(row) - 1: 
                    osd.drawstring(row[col], x0, y0, val.items.color,
                                   font=val.items.font,
                                   ptsize=fontsize)

                # the last col may be too long
                if col == len(row) - 1:
                    w, h = osd.stringsize(row[col], font=val.items.font,
                                          ptsize=fontsize)
                    if w + x0 - val.items.x + 16 > selection_length:
                        row[col] += "..."
                    while w + x0 - val.items.x + 16 > selection_length:
                        row[col] = row[col][0:-4] + "..."
                        w, h = osd.stringsize(row[col], font=val.items.font,
                                              ptsize=fontsize)

                    osd.drawstring(row[col], x0, y0, val.items.color,
                                   font=val.items.font,
                                   ptsize=fontsize)

                y0 += spacing

            # Update x for the next column
            x0 += maxwidth + 8


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
        



