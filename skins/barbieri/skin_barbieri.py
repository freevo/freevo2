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


    def DrawText(self, text, x, y, color, shadow_color = 0x000000, bgcolor = None,
                 font = None, ptsize = None,
                 drop_shadow=None, shadow_mode=None, shadow_pad_x=2, shadow_pad_y=2):
        if drop_shadow:
            if shadow_mode == 'translucent':
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y, (160 << 24) | shadow_color, bgcolor, font, ptsize)
            elif shadow_mode == 'solid':
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y, shadow_color, bgcolor, font, ptsize)
            else: # solid
                osd.drawstring(text, x+shadow_pad_x, y+shadow_pad_y, shadow_color, bgcolor, font, ptsize)
                
        osd.drawstring(text, x, y, color, None, font, ptsize)


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

#        if len(menuw.menu_items) == 5:
#            icon_size = 64

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
	    if menu.selected == choice:
                image = choice.image

            if choice.eventhandler_args:
                if choice.eventhandler_args[0] == 'dir':
                    if menu.selected == choice:
                        osd.drawbox(x0 - 8 + w, y0 - 3 + h,
                                    x0 - 8 + val.item_dir.selection.length, y0 + val.item_dir.selection.size*1.5 + h, width=-1,
                                    color=((160 << 24) | val.item_dir.selection.bgcolor))
                        
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.item_dir.selection.color, 
                                      val.item_dir.selection.shadow_color, None, val.item_dir.selection.font,
                                      val.item_dir.selection.size, val.item_dir.selection.shadow_visible,
                                      val.item_dir.selection.shadow_mode,
                                      val.item_dir.selection.shadow_pad_x, val.item_dir.selection.shadow_pad_y)
                        
                    else:
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.item_dir.color, 
                                      val.item_dir.shadow_color, None, val.item_dir.font,
                                      val.item_dir.size, val.item_dir.shadow_visible,
                                      val.item_dir.shadow_mode,
                                      val.item_dir.shadow_pad_x, val.item_dir.shadow_pad_y)

                elif choice.eventhandler_args[0] == 'list':
                    if menu.selected == choice:
                        osd.drawbox(x0 - 8 + w, y0 - 3 + h,
                                    x0 - 8 + val.item_pl.selection.length, y0 + val.item_pl.selection.size*1.5 + h, width=-1,
                                    color=((160 << 24) | val.item_pl.selection.bgcolor))
                        
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.item_pl.selection.color, 
                                      val.item_pl.selection.shadow_color, None, val.item_pl.selection.font,
                                      val.item_pl.selection.size, val.item_pl.selection.shadow_visible,
                                      val.item_pl.selection.shadow_mode,
                                      val.item_pl.selection.shadow_pad_x, val.item_pl.selection.shadow_pad_y)
                        
                    else:
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.item_pl.color, 
                                      val.item_pl.shadow_color, None, val.item_pl.font,
                                      val.item_pl.size, val.item_pl.shadow_visible,
                                      val.item_pl.shadow_mode,
                                      val.item_pl.shadow_pad_x, val.item_pl.shadow_pad_y)

                elif choice.eventhandler_args[0] == 'main':
                    if menu.selected == choice:
                        osd.drawbox(x0 - 8 + w, y0 - 3 + h,
                                    x0 - 8 + val.item_main.selection.length, y0 + val.item_main.selection.size*1.5 + h, width=-1,
                                    color=((160 << 24) | val.item_main.selection.bgcolor))
                        
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.item_main.selection.color, 
                                      val.item_main.selection.shadow_color, None, val.item_main.selection.font,
                                      val.item_main.selection.size, val.item_main.selection.shadow_visible,
                                      val.item_main.selection.shadow_mode,
                                      val.item_main.selection.shadow_pad_x, val.item_main.selection.shadow_pad_y)
                        
                    else:
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.item_main.color, 
                                      val.item_main.shadow_color, None, val.item_main.font,
                                      val.item_main.size, val.item_main.shadow_visible,
                                      val.item_main.shadow_mode,
                                      val.item_main.shadow_pad_x, val.item_main.shadow_pad_y)

                else:
                    if menu.selected == choice:
                        osd.drawbox(x0 - 8 + w, y0 - 3 + h,
                                    x0 - 8 + val.items.selection.length, y0 + val.items.selection.size*1.5 + h, width=-1,
                                    color=((160 << 24) | val.items.selection.bgcolor))
                        
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.items.selection.color, 
                                      val.items.selection.shadow_color, None, val.items.selection.font,
                                      val.items.selection.size, val.items.selection.shadow_visible,
                                      val.items.selection.shadow_mode,
                                      val.items.selection.shadow_pad_x, val.items.selection.shadow_pad_y)
                    else:
                        self.DrawText(choice.name, (x0+w+10), y0+h, val.items.color, 
                                      val.items.shadow_color, None, val.items.font,
                                      val.items.size, val.items.shadow_visible,
                                      val.items.shadow_mode,
                                      val.items.shadow_pad_x, val.items.shadow_pad_y)
            else:
                if menu.selected == choice:
                    osd.drawbox(x0 - 8 + w, y0 - 3 + h,
                                x0 - 8 + val.items.selection.length, y0 + val.items.selection.size*1.5 + h, width=-1,
                                color=((160 << 24) | val.items.selection.bgcolor))
                    
                    self.DrawText(choice.name, (x0+w+10), y0+h, val.items.selection.color, 
                                  val.items.selection.shadow_color, None, val.items.selection.font,
                                  val.items.selection.size, val.items.selection.shadow_visible,
                                  val.items.selection.shadow_mode,
                                  val.items.selection.shadow_pad_x, val.items.selection.shadow_pad_y)

                else:
                    self.DrawText(choice.name, (x0+w+10), y0+h, val.items.color, 
                                  val.items.shadow_color, None, val.items.font,
                                  val.items.size, val.items.shadow_visible,
                                  val.items.shadow_mode,
                                  val.items.shadow_pad_x, val.items.shadow_pad_y)

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
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.selection.length, \
                            y0 + val.submenu.selection.size*1.5,
                            width=-1,
                            color=((160 << 24) | val.submenu.selection.bgcolor))
                
                self.DrawText(item.name, x0, y0, val.submenu.selection.color, 
                              val.submenu.selection.shadow_color, None, val.submenu.selection.font,
                              val.submenu.selection.size, val.submenu.selection.shadow_visible,
                              val.submenu.selection.shadow_mode,
                              val.submenu.selection.shadow_pad_x, val.submenu.selection.shadow_pad_y)
                
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
            self.DrawText('Dir: '+dir_name, 5, 510, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
            self.DrawText('File: '+file_name, 5, 540, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
                
                

            self.DrawText('Title:', 30, 100, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.title, left, 100, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
 
            
            self.DrawText('Artist:', 30, 130, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.artist, left, 130, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)


            self.DrawText('Album:', 30, 160, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.album, left, 160, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
        

            self.DrawText('Year:', 30, 190, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.year, left, 190, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)


            self.DrawText('Track:', 30, 220, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)
            self.DrawText('%s ' % info.track, left, 220, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)

            self.DrawText('Time:', 30, 250, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)

                
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

        self.DrawText('%s:%02d/-%s:%02d (%0.1f%%) ' % (el_min, el_sec, rem_min, rem_sec, info.done), left, 250, val.font.color, val.shadow.color, None, val.font.font, val.font.size, val.shadow.visible, val.shadow.mode, val.shadow.x, val.shadow.y)


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
    
