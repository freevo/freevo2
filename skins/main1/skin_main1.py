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
# Revision 1.18  2002/09/01 04:31:35  krister
# Removed the 'text' on an empty line, looks like Dischis cat walked over the clicked the paste-button on his mouse...
#
# Revision 1.17  2002/08/31 17:33:49  dischi
# The selection will be shorten if there is a image for an item to avoid
# overlapping. If the item name is too long it will be shorten, too and "..."
# will be added at the end.
#
# Revision 1.16  2002/08/19 05:52:08  krister
# Changed to Gustavos new XML code for more settings in the skin. Uses columns for the TV guide.
#
# Revision 1.2  2002/08/18 06:12:30  krister
# Converted tabs to spaces. Please use tabnanny in the future!
#
# Revision 1.1  2002/08/17 02:55:45  krister
# Submitted by Gustavo Barbieri.
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

    if DEBUG: print 'Skin: Loading XML file %s' % config.SKIN_XML_FILE
    
    settings = xml_skin.XMLSkin()
    settings.load(config.SKIN_XML_FILE)

    items_per_page = 12

    hold = 0


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


    def DrawText(self, text, x, y, color, shadow_color = 0x000000,
                 bgcolor = None, font = None, ptsize = None,
                 drop_shadow=None, shadow_mode=None, shadow_pad_x=2,
                 shadow_pad_y=2):
        
        if drop_shadow:
            if shadow_mode == 'translucent':
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y,
                               (160 << 24) | shadow_color, bgcolor,
                               font, ptsize)
            elif shadow_mode == 'solid':
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y,
                               shadow_color, bgcolor, font, ptsize)
            else: # solid
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y,
                               shadow_color, bgcolor, font, ptsize)
                
        osd.drawstring(text, x, y, color, None, font, ptsize)


    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        if self.hold:
            print 'skin.drawmenu() hold!'
            return
        
        osd.clearscreen(osd.COL_WHITE)

        menu = menuw.menustack[-1]

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        # XXX Kludge to draw the TV Guide using the old code. 
        if menu.heading.find('TV MENU') != -1:
            self._DrawTVGuide(menuw)
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

            # x == -1 is a magic value for center alignment
            if val.title.x == -1:
                al = 'center'
                tx = osd.width / 2
            else:
                al = 'left'
                tx = val.title.x

            if DEBUG: print 'XXX x=%s, al=%s' % (val.title.x, al)
            osd.drawstring(menu.heading, tx, val.title.y, val.title.color,
                           font=val.title.font,
                           ptsize=val.title.size, align=al)
            
        # Draw the menu choices for the main selection
        y0 = val.items.y
        selection_height = val.items.height
        icon_size = 75

        if len(menuw.menu_items) == 5:
            icon_size = 64

        if DEBUG:
            print 'DrawMenu() y0: %s, selh: %s, iconsize: %s' % (y0,
                                                                 selection_height,
                                                                 icon_size)
        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)

        image_x = 0

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

        
        for choice in menuw.menu_items:

            if menu.selected == choice:
                image = choice.image

            # Pick the settings for this kind of item
            valign = 0 # Vertical aligment to the icon
            if choice.eventhandler_args:

                if choice.eventhandler_args[0] == 'dir':
                    item = val.item_dir
                elif choice.eventhandler_args[0] == 'list':
                    item = val.item_pl
                elif choice.eventhandler_args[0] == 'main':
                    item = val.item_main
                    valign = 1 # Only for the main menu
                else:
                    item = val.items
            else:
                item = val.items

            # And then pick the selected or non-selected settings for
            # that object
            if menu.selected == choice:
                obj = item.selection
            else:
                obj = item

            # Get the rendered string height. Not totally correct if
            # shadows are used. 'Ajg' is just a way to get the full height.
            str_w, str_h = osd.stringsize('Ajg', font=obj.font,
                                          ptsize=obj.size)

            # Try and center the text to the middle of the icon
            if valign:
                top = y0 + (icon_size - str_h) / 2
            else:
                top = y0

            # if there is an image and the selection will be cover the image
            # shorten the selection

            selection_length = item.selection.length

            if image_x and item.x - 8 + selection_length > image_x - 30:
                selection_length = image_x - 30 - val.items.x + 8


            # Draw the selection bar for selected items
            if menu.selected == choice:
                osd.drawbox(item.x - 8, top - 2,
                            item.x - 8 + selection_length,
                            top + str_h + 2,
                            width = -1,
                            color = ((160 << 24) |
                                     obj.bgcolor))

            # Draw the menu item text, shorten the text before to fit
            # the selection length
            text = choice.name

            font_w, font_h = osd.stringsize(text, font=obj.font, ptsize=obj.size)
            if font_w + 26 > selection_length:
                text = text + "..."
                    
            while font_w + 26 > selection_length:
                text = text[0:-4] + "..."
                font_w, font_h = osd.stringsize(text, font=obj.font, ptsize=obj.size)
                
            self.DrawText(text, item.x, top,
                          obj.color, 
                          obj.shadow_color, None,
                          obj.font,
                          obj.size,
                          obj.shadow_visible,
                          obj.shadow_mode,
                          obj.shadow_pad_x,
                          obj.shadow_pad_y)

            if choice.icon != None:
                icon_x = item.x - icon_size - 15
                osd.drawbitmap(util.resize(choice.icon,
                                           icon_size, icon_size), icon_x, y0)

            y0 += spacing


        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y
        
        for item in menuw.nav_items:
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.selection.length, 
                            y0 + val.submenu.selection.size*1.5,
                            width=-1,
                            color=((160 << 24) | val.submenu.selection.bgcolor))
                
                self.DrawText(item.name, x0, y0, val.submenu.selection.color, 
                              val.submenu.selection.shadow_color, None,
                              val.submenu.selection.font,
                              val.submenu.selection.size,
                              val.submenu.selection.shadow_visible,
                              val.submenu.selection.shadow_mode,
                              val.submenu.selection.shadow_pad_x,
                              val.submenu.selection.shadow_pad_y)
                
            else:
                self.DrawText(item.name, x0, y0, val.submenu.color, 
                              val.submenu.shadow_color, None, val.submenu.font,
                              val.submenu.size, val.submenu.shadow_visible,
                              val.submenu.shadow_mode,
                              val.submenu.shadow_pad_x, val.submenu.shadow_pad_y)
            x0 += 190

        osd.update()
        


    # XXX Super-kludge warning!
    # I (Krister) don't have time to integrate Gustavo's new stuff with my
    # column menu drawing, so I'll just include my old DrawMenu() and
    # call that for the TV menu only for now.
    #
    # Called from DrawMenu to draw the TV Guide menu page
    def _DrawTVGuide(self, menuw):
        if self.hold:
            print 'skin.drawmenu() hold!'
            return

        if DEBUG: print 'Skin.drawmenu()'
        
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
            osd.drawstring(menu.heading, osd.width/2, val.title.y,
                           val.title.color, font=val.title.font,
                           ptsize=val.title.size, align='center')

        # Sub menus
        icon_size = 25

        x0 = val.items.x
        y0 = val.items.y
        selection_height = val.items.height

        if menu.packrows:
            spacing = selection_height / menuw.items_per_page
        else:
            spacing = selection_height / max(len(menuw.menu_items),1)

        # image to display
        image = None
        
        fontsize = val.items.size
        
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
                icon_x = x0 - icon_size - 10
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size),
                               icon_x, y0)

            # Draw the selection
            osd.drawstring(rows[row][0], x0, y0, val.items.color,
                           font=val.items.font,
                           ptsize=fontsize)
            
            if menu.selected == choice:
                osd.drawbox(x0 - 3, y0 - 3,
                            x0 + maxwidth + 3,
                            y0 + fontsize*1.5 + 1, width=-1,
                            color=((160 << 24) | val.items.selection.bgcolor))

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

        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y
        
        for item in menuw.nav_items:
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.selection.length, 
                            y0 + val.submenu.selection.size*1.5,
                            width=-1, color=((160 << 24) |
                                             val.submenu.selection.bgcolor))
                
                self.DrawText(item.name, x0, y0, val.submenu.selection.color, 
                              val.submenu.selection.shadow_color, None,
                              val.submenu.selection.font,
                              val.submenu.selection.size,
                              val.submenu.selection.shadow_visible,
                              val.submenu.selection.shadow_mode,
                              val.submenu.selection.shadow_pad_x,
                              val.submenu.selection.shadow_pad_y)
                
            else:
                self.DrawText(item.name, x0, y0, val.submenu.color, 
                              val.submenu.shadow_color, None, val.submenu.font,
                              val.submenu.size, val.submenu.shadow_visible,
                              val.submenu.shadow_mode,
                              val.submenu.shadow_pad_x, val.submenu.shadow_pad_y)
            x0 += 190

        osd.update()


    def DrawMP3(self, info):

        val = self.settings.mp3

        left = 120

        if info.drawall:
            osd.clearscreen()

            if val.bgbitmap[0]:
                apply(osd.drawbitmap, (val.bgbitmap, -1, -1))
            
            if val.title.visible:
                # x == -1 is a magic value for center alignment
                if val.title.x == -1:
                    al = 'center'
                    tx = osd.width / 2
                else:
                    al = 'left'
                    tx = val.title.x

                osd.drawstring('Playing Music', tx, val.title.y,
                               val.title.color, font=val.title.font,
                               ptsize=val.title.size, align=al)


            # Display the cover image file if it is present
            if info.image:
                osd.drawbox(465,190, 755, 480, width=1, color=0x000000)   
                osd.drawbitmap(util.resize(info.image, 289, 289), 466, 191)
               
            file_name = info.filename.split('/')
            dir_name = ''
            for i in range(len(file_name)-1):
                dir_name += file_name[i] + '/'

            file_name = file_name[i+1]
            py = val.progressbar.y
            self.DrawText('Dir: '+dir_name, 5, py + 20, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
            self.DrawText('File: '+file_name, 5, py + 40, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
                
            self.DrawText('Title:', 30, 100, val.font.color, val.shadow.color,
                          None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
            self.DrawText('%s ' % info.title, left, 100, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
 
            self.DrawText('Artist:', 30, 130, val.font.color, val.shadow.color,
                          None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
            self.DrawText('%s ' % info.artist, left, 130, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)

            self.DrawText('Album:', 30, 160, val.font.color, val.shadow.color,
                          None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
            self.DrawText('%s ' % info.album, left, 160, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
        
            self.DrawText('Year:', 30, 190, val.font.color, val.shadow.color,
                          None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
            self.DrawText('%s ' % info.year, left, 190, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)

            self.DrawText('Track:', 30, 220, val.font.color, val.shadow.color,
                          None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)
            self.DrawText('%s ' % info.track, left, 220, val.font.color,
                          val.shadow.color, None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)

            self.DrawText('Time:', 30, 250, val.font.color, val.shadow.color,
                          None, val.font.font, val.font.size,
                          val.shadow.visible, val.shadow.mode, val.shadow.x,
                          val.shadow.y)

                
        else:
            # Erase the portion that will be redrawn
            if val.bgbitmap[0]:
                osd.drawbitmap( val.bgbitmap, left, 250, None, left,
                                250, 250, 30 )

        # XXX I changed this because round rounds up on 3.58 etc. instead
        # XXX of giving us the desired "round down modulo" effect.
        el_min  = int(info.elapsed)/60
        el_sec  = int(info.elapsed)%60
        rem_min = int(info.remain)/60
        rem_sec = int(info.remain)%60

        str = '%s:%02d/-%s:%02d (%0.1f%%) ' % (el_min, el_sec, rem_min,
                                               rem_sec, info.done)
        self.DrawText(str, left, 250, val.font.color, val.shadow.color, None,
                      val.font.font, val.font.size, val.shadow.visible,
                      val.shadow.mode, val.shadow.x, val.shadow.y)

        # Draw the progress bar
        if val.progressbar.visible:
            # margin:
            osd.drawbox(val.progressbar.x,
                        val.progressbar.y,
                        val.progressbar.x + val.progressbar.width,
                        val.progressbar.y + val.progressbar.height,
                        width = val.progressbar.border_size,
                        color = val.progressbar.border_color)
            
            # the progress indicator background:
            osd.drawbox(val.progressbar.x +1,
                        val.progressbar.y +1,
                        val.progressbar.x + val.progressbar.width -1,
                        val.progressbar.y + val.progressbar.height -1,
                        width = -1,
                        color = val.progressbar.bgcolor)
            pixels = int(round((info.done)/100 * val.progressbar.width))

            # the progress indicator:
            osd.drawbox(val.progressbar.x +1,
                        val.progressbar.y +1,
                        val.progressbar.x + pixels,
                        val.progressbar.y + val.progressbar.height -1,
                        width = -1,
                        color = val.progressbar.color)
            
        osd.update()
    
