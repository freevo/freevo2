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
# Revision 1.3  2002/09/18 22:46:22  gsbarbieri
# Skin updated to use new features of menu.py
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
import xml_skin


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


ICON_SIZE=64
PADDING=5   # Padding/spacing between items

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


    # This function calculates how many menu items fit in one page
    def ItemsPerMenuPage(self, menu):
        
        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        # get the settings
        if menu.skin_settings:
            val = menu.skin_settings.menu
        else:
            val = self.settings.menu

        used_height = 0;
        height = val.items.height
        n_items = 0;

        for item in menu.choices[menu.page_start : len(menu.choices)]:
            if item.type:
                if item.type == 'dir':
                    pref_item = val.item_dir
                elif item.type == 'list':
                    pref_item = val.item_pl
                elif item.type == 'main':
                    pref_item = val.item_main
                else:
                    pref_item = val.items;
            else:
                pref_item = val.items;


            # Size of the non-selected item
            ns_str_w, ns_str_h = osd.stringsize('Ajg', font=pref_item.font,
                                                ptsize=pref_item.size)            
            # Size of the selected item
            s_str_w, s_str_h = osd.stringsize('Ajg', font=pref_item.font,
                                              ptsize=pref_item.selection.size)

            item_icon_size_x = item_icon_size_y = 0
            if item.icon != None:
                item_icon_size_x, item_icon_size_y = osd.bitmapsize(item.icon)
            

            # the size used will be:
            str_h = max(ns_str_h, s_str_h, item_icon_size_y)
            str_h += 2*PADDING
            str_h += max(pref_item.shadow_pad_y, pref_item.selection.shadow_pad_y)
        
            used_height += str_h;
            if used_height < height:
                n_items+=1
            else:
                return n_items

        return n_items



    

    # Parse XML files with additional settings
    # TODO: parse also parent directories
    def LoadSettings(self, dir):
        if dir and os.path.isfile(os.path.join(dir, "skin.xml")):
            settings = copy.copy(self.settings)
            settings.load(os.path.join(dir, "skin.xml"), 1)
            return settings
        return None





    def DrawText(self, text, x, y, color, shadow_color = 0x000000, bgcolor = None,
                 font = None, ptsize = None,
                 drop_shadow=None, shadow_pad_x=2, shadow_pad_y=2,
                 align='left'):
        if drop_shadow:
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y, shadow_color, bgcolor, font, ptsize, align)
        osd.drawstring(text, x, y, color, None, font, ptsize, align)


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
            self.DrawText(menu.heading, val.title.x, val.title.y,
                          val.title.color, val.title.shadow_color, None,
                          val.title.font, val.title.size,
                          val.title.shadow_visible,
                          val.title.shadow_pad_x, val.title.shadow_pad_y,
                          val.title.align)
            
        # Draw the menu choices for the main selection
        x0 = val.items.x + PADDING
        y0 = val.items.y + PADDING

        # image to display
        image = None

        for choice in menuw.menu_items:
            w = 0
            h = 0

            pref_item = None
            if choice.type:
                if choice.type == 'dir':
                    pref_item = val.item_dir
                elif choice.type == 'list':
                    pref_item = val.item_pl                    
                elif choice.type == 'main':
                    pref_item = val.item_main                    
                else:
                    pref_item = val.items                    
            else:
                pref_item = val.items                    


            # Size of the non-selected item
            ns_str_w, ns_str_h = osd.stringsize(choice.name, font=pref_item.font,
                                                ptsize=pref_item.size)            
            # Size of the selected item
            s_str_w, s_str_h = osd.stringsize(choice.name, font=pref_item.selection.font,
                                              ptsize=pref_item.selection.size)

            
            # the size used will be:
            str_h = max(ns_str_h, s_str_h)
            str_h += max(pref_item.shadow_pad_y, pref_item.selection.shadow_pad_y)

            str_w = max(ns_str_w, s_str_w, pref_item.selection.length)
            str_w += max(pref_item.shadow_pad_x, pref_item.selection.shadow_pad_x)


            pref_item_use = pref_item
            icon = choice.icon

            if menu.selected == choice:
                image = choice.image
                if choice.selected_icon != None:
                    icon = choice.selected_icon

            item_icon_size_x = item_icon_size_y = 0            
            if icon != None:
                item_icon_size_x, item_icon_size_y = osd.bitmapsize(icon) 
                w = item_icon_size_x + 20
                h = (int)(item_icon_size_y - str_h) / 2
            
            if menu.selected == choice:
                osd.drawbox(x0 - PADDING + w,     y0 - PADDING + h,
                            x0 + str_w +PADDING, y0 + h + str_h + PADDING,
                            width=-1,
                            color=pref_item.selection.bgcolor)
                pref_item_use = pref_item.selection


            if icon != None: 
                osd.drawbitmap(util.resize(icon, item_icon_size_x, item_icon_size_y), x0, y0)


            self.DrawText(choice.name,
                          x0+w, y0+h, pref_item_use.color, 
                          pref_item_use.shadow_color, None, pref_item_use.font,
                          pref_item_use.size, pref_item_use.shadow_visible,
                          pref_item_use.shadow_pad_x, pref_item_use.shadow_pad_y)                
            

            y0 += 2*PADDING + max(str_h, item_icon_size_y)


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
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.selection.length, \
                            y0 + val.submenu.selection.size*1.5,
                            width=-1,
                            color=val.submenu.selection.bgcolor)
                
                self.DrawText(item.name, x0, y0, val.submenu.selection.color, 
                              val.submenu.selection.shadow_color, None, val.submenu.selection.font,
                              val.submenu.selection.size, val.submenu.selection.shadow_visible,
                              val.submenu.selection.shadow_pad_x, val.submenu.selection.shadow_pad_y)
                
            else:
                self.DrawText(item.name, x0, y0, val.submenu.color, 
                              val.submenu.shadow_color, None, val.submenu.font,
                              val.submenu.size, val.submenu.shadow_visible,
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
                osd.drawstring('Playing Music', val.title.x, val.title.y, val.title.color,
                               font=val.title.font,
                               ptsize=val.title.size)


            # Display the cover image file if it is present
            if info.image:
                osd.drawbox(465,190, 755, 480, width=1, color=0x000000)                            
                osd.drawbitmap(util.resize(info.image, 289, 289), 466, 191)

               

            file_name = info.filename.split('/')
            dir_name = ''
            for i in range(len(file_name)-1):
                dir_name += file_name[i] + '/'

            file_name = file_name[i+1]
            self.DrawText('Dir: '+dir_name, 5, 510, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
            self.DrawText('File: '+file_name, 5, 540, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
                
                

            self.DrawText('Title:', 30, 100, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.title, left, 100, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
 
            
            self.DrawText('Artist:', 30, 130, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.artist, left, 130, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)


            self.DrawText('Album:', 30, 160, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.album, left, 160, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
        

            self.DrawText('Year:', 30, 190, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.year, left, 190, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)


            self.DrawText('Track:', 30, 220, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.track, left, 220, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)

            self.DrawText('Time:', 30, 250, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)

                
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

        self.DrawText('%s:%02d/-%s:%02d (%0.1f%%) ' % (el_min, el_sec, rem_min, rem_sec, info.done), left, 250, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible,  val.shadow.x, val.shadow.y)


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

