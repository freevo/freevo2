#if 0
# -----------------------------------------------------------------------
# skin_main1.py - Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:   This is the main1 skin
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.78  2003/02/15 20:47:50  dischi
# Use getFormatedImage from main1_image to speed up the display for
# image thumbnails
#
# Revision 1.77  2003/02/12 10:38:51  dischi
# Added a patch to make the current menu system work with the new
# main1_image.py to have an extended menu for images
#
# Revision 1.76  2003/02/11 06:53:00  krister
# Fixed small bugs.
#
# Revision 1.75  2003/02/08 23:31:33  gsbarbieri
# hanged the Image menu to ExtendedMenu.
#
# OBS:
#    main1_tv: modified to handle the <indicator/> as a dict
#    xml_skin: modified to handle <indicator/> as dict and the new tag, <img/>
#    main: modified to use the ExtendedMenu
#    mediamenu: DirItem.cmd() now return items, so we can use it without a menu
#
# Revision 1.74  2003/02/07 20:18:23  dischi
# break after a local_skin is found
#
# Revision 1.73  2003/02/07 19:27:29  dischi
# use config.cfgfilepath to find local_skin.xml
#
# Revision 1.72  2003/01/29 16:41:26  outlyer
# Removed a stray 'print sys.path' line.
#
# Revision 1.71  2002/12/21 17:26:52  dischi
# Added dfbmga support. This includes configure option, some special
# settings for mplayer and extra overscan variables
#
# Revision 1.70  2002/12/20 15:43:47  dischi
# The skin files are geometry independed now. They can be used for every
# resolution (e.g. 720x576 and 720x480)
#
# Revision 1.69  2002/12/02 22:09:41  dischi
# DrawStringFramed should now work for the title and the items
#
# Revision 1.68  2002/11/28 22:06:25  outlyer
# Reverting the switch to "DrawTextFramed" to "DrawText" since it was
# making a bunch of text disappear. DrawTextFramed is the better way to do it,
# but 50% of my menu items disappeared.
#
# Revision 1.67  2002/11/28 04:57:19  gsbarbieri
# Now do not draw the "selected box" under the icon in DrawMenu_Selection
#
# Revision 1.66  2002/11/28 03:45:42  gsbarbieri
# Changed DrawMenu_Selection to fix a bug and add icon support to items via xml image filed.
#
# Revision 1.4  2002/11/24 14:06:57  dischi
# code cleanup
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

# The gui class
import gui
    
# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# XML parser for skin informations
sys.path.append('skins/xml/type1')


import xml_skin

# Create the OSD object
osd = osd.get_singleton()

# Skin utility functions
from main1_utils import *

# TV guide support
import main1_tv

# Image browser support
import main1_image

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


PADDING=5   # Padding/spacing between items

###############################################################################

# Set up the mixer
mixer = mixer.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

###############################################################################
# Skin main functions
###############################################################################

XML_SKIN_DIRECTORY = 'skins/xml/type1'

class Skin:

    if DEBUG: print 'Skin: Loading XML file %s' % config.SKIN_XML_FILE
    
    settings = xml_skin.XMLSkin()

    # try to find the skin xml file
    
    if not settings.load(config.SKIN_XML_FILE):
        print "skin not found, using fallback skin"
        settings.load("%s/grey1.xml" % XML_SKIN_DIRECTORY)
        
    for dir in config.cfgfilepath:
        local_skin = '%s/local_skin.xml' % dir
        if os.path.isfile(local_skin):
            if DEBUG: print 'Skin: Add local config %s to skin' % local_skin
            settings.load(local_skin)
            break
        
    hold = 0


    def __init__(self):
        self.tv = main1_tv.Skin_TV()
        self.image = main1_image.Skin_Image()
        self.extended_menu = FALSE
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
        elif dir and os.path.isfile(dir):
            settings = copy.copy(self.settings)
            settings.load(dir, 1)
            return settings
        return None


    # Got DISPLAY event from menu
    def ToggleDisplayStyle(self, menu):
        if menu.item_types and menu.item_types in self.settings.e_menu and \
           hasattr(self, menu.item_types):
            self.extended_menu = not self.extended_menu
            return TRUE
        return FALSE

    def GetDisplayStyle(self):
        return self.extended_menu
    
    def ItemsPerMenuPage(self, menu):

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return (0,0)

        # hack for the main menu to fit all in one screen
        if not menu.packrows:
            return (5,1)
        
        if menu.item_types and menu.item_types in self.settings.e_menu and \
           hasattr(self, menu.item_types) and self.extended_menu:
        
            if menu.skin_settings:
                val = menu.skin_settings.e_menu[menu.item_types]
            else:
                val = self.settings.e_menu[menu.item_types]

            return (eval('self.%s.getRows(val)' % menu.item_types),
                    eval('self.%s.getCols(val)' % menu.item_types))

        # find the correct structures, I hope we don't need this
        # for the main menu ...
        if menu.skin_settings:
            val = menu.skin_settings.menu_default
        else:
            val = self.settings.menu_default

        used_height = 0
        n_items     = 0

        for item in menu.choices[menu.page_start : len(menu.choices)]:
            if item.type:
                if item.type == 'dir':
                    pref_item = val.items.dir
                elif item.type == 'list':
                    pref_item = val.items.pl
                else:
                    pref_item = val.items.default;
            else:
                pref_item = val.items.default;

            # Size of the non-selected item
            ns_str_w, ns_str_h = osd.stringsize('Ajg', font=pref_item.font,
                                                ptsize=pref_item.size)            
            # Size of the selected item
            s_str_w, s_str_h = osd.stringsize('Ajg', font=pref_item.font,
                                              ptsize=pref_item.selection.size)

            item_icon_size_x = item_icon_size_y = 0
            if item.icon != None:
                item_icon_size_x, item_icon_size_y = osd.bitmapsize(item.icon)
            
            # add the size used
            used_height += max(ns_str_h, s_str_h, item_icon_size_y) + PADDING + \
                           max(pref_item.shadow_pad_y, pref_item.selection.shadow_pad_y)
        
            if used_height < val.items.height:
                n_items+=1
            else:
                return (n_items, 1)

        return (n_items, 1)
        


    def SubMenuVisible(self, menu):
        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return TRUE

        # find the correct structures, I hope we don't need this
        # for the main menu ...
        if menu.skin_settings:
            return menu.skin_settings.menu_default.submenu.visible
        else:
            return self.settings.menu_default.submenu.visible


    def PopupBox(self, text=None, icon=None):
        """
        text  String to display

        Draw a popupbox with an optional icon and a text.
        
        Notes: Should maybe be named print_message or show_message.
               Maybe I should use one common box item.
        """

        val = self.settings.popup

        # XXX If someone has the time, please fix this. It's a bad mixture
        # XXX between hardcoded stuff (some values and the alpha mask) and
        # XXX the use of the gui toolkit

        x = val.message.x
        width = val.message.width
        
        # if we have an alpha mask, don't use the gui toolkit
        # just draw it
        if val.mask:
            osd.drawbitmap(val.mask, val.x, val.y)
            
        if icon:
            icon_width, icon_height = util.pngsize(icon)
            x += icon_width
            width -= icon_width

        need = osd.drawstringframed(text, x, val.message.y, width, val.message.height, \
                                    val.message.color, None, val.message.font, \
                                    val.message.size, val.message.align, 'center',
                                    mode='soft')
        (x0, y0, x1, y1) = need[1]

        if icon:
            x0 -= icon_width + 10
            if icon_height > (y1 - y0):
                missing = (icon_height - (y1 - y0)) / 2
                y1 += missing
                y0 -= missing
                
        if val.mask:
            if icon:
                osd.drawbitmap(icon, val.x+25, y0 + (y1-y0) / 2 - (icon_height/2))
                
        else:            
            drawroundbox(x0-val.spacing, y0-val.spacing, x1+val.spacing,
                             y1+val.spacing, color=val.bgcolor,
                             border_size=val.border_size, border_color=val.border_color,
                             radius=val.radius)

            if icon:
                osd.drawbitmap(icon, x0, y0 + (y1-y0) / 2 - (icon_height/2))

            osd.drawstringframed(text, x, val.message.y, width, val.message.height, \
                                 val.message.color, None, val.message.font, \
                                 val.message.size, val.message.align, 'center')

        osd.update()
        

    def DrawMenu_Cover(self, menuw, settings):
        image_x = 0
        val = settings
        menu = menuw.menustack[-1]

        i_val = None
        i_file = None
            

        # display the image and store the x0 position of the image
        for item in menuw.menu_items:
            image = item.image

            if image:
                type = item.type
                if hasattr(item, 'handle_type') and item.handle_type:
                    type = item.handle_type

                if type == 'image' and val.cover_image.visible:
                    image_x = val.cover_image.x-val.cover_image.spacing
                    if menu.selected == item:
                        (i_file, w, h) = self.image.getFormatedImage \
                                         (image, val.cover_image.width,
                                          val.cover_image.height)
                        i_val = copy.deepcopy(val.cover_image)
                        i_val.height = h
                        i_val.width  = w
                        
                        # check all round masks if they are around the image
                        # and shorten the width of those who are to fit
                        # the new size
                        if isinstance(i_val.mask, list):
                            for m in i_val.mask:
                                if m.x <= i_val.x and m.y <= i_val.y and \
                                   m.width >= i_val.width and \
                                   m.height >= i_val.height:
                                    m.height -= val.cover_image.height-h
                                    m.width -= val.cover_image.width-w
                                    


                elif type == 'video' and val.cover_movie.visible:
                    image_x = val.cover_movie.x-val.cover_movie.spacing
                    if menu.selected == item:
                        w, h = util.pngsize(image)

                        # this is no cover image, it's seems to be
                        # a screenshot of the movie, don't scale this
                        # to the cover sizes
                        if w > h:
                            scale = float(val.cover_movie.width) / w
                            i_file = util.resize(image, val.cover_movie.width,
                                                 h*scale)

                            i_val = copy.deepcopy(val.cover_movie)

                            # check all round masks if they are around the image
                            # and shorten the width of those who are to fit
                            # the new size
                            if isinstance(i_val.mask, list):
                                for m in i_val.mask:
                                    if m.x <= i_val.x and m.y <= i_val.y and \
                                       m.width >= i_val.width and \
                                       m.height >= i_val.height:
                                        m.height -= val.cover_movie.height-h*scale
                                
                            i_val.height = h*scale


                        # normal cover
                        else:
                            i_file = util.resize(image, val.cover_movie.width, \
                                                 val.cover_movie.height)
                            i_val = val.cover_movie

                elif type == 'audio' and val.cover_music.visible:
                    image_x = val.cover_music.x-val.cover_music.spacing
                    if menu.selected == item:
                        i_file = util.resize(image, val.cover_music.width, \
                                             val.cover_music.height)
                        i_val = val.cover_music


        return i_file, max(0, image_x-val.items.default.selection.spacing), i_val


    
    def DrawMenu_Selection(self, menuw, settings, x0, y0, width, height):
        val = settings
        menu = menuw.menustack[-1]

        if menu.packrows:
            spacing = 0                 # calculate this later
            icon_size = 28
        else:
            spacing = height / max(len(menuw.menu_items), 1)
            # The icons are 64x64 in 800x600 resolution, scale for other res.
            scale = osd.width / 800.0
            icon_size = int(round(64 * scale))


        for choice in menuw.menu_items:
            
            if menu.selected == choice:
                image = choice.image


            # Pick the settings for this kind of item
            valign = 0 # Vertical aligment to the icon
            if choice.type:
                if choice.type == 'dir':
                    item = val.items.dir
                elif choice.type == 'playlist':
                    item = val.items.pl
                else:
                    item = val.items.default
            else:
                item = val.items.default

            # And then pick the selected or non-selected settings for
            # that object
            if menu.selected == choice:
                obj = item.selection
            else:
                obj = item

            text = choice.name
            if choice.type == 'playlist':
                text = 'PL: %s' % text
            font_w, font_h = osd.stringsize(text, font=obj.font, ptsize=obj.size)

            if not spacing:
                spacing = font_h + PADDING        

            # Try and center the text to the middle of the icon
            if valign:
                top = y0 + (icon_size - font_h) / 2
            else:
                top = y0

            # icon or image?
            if choice.icon != None:
                icon = choice.icon
            else:
                icon = item.image
            icon_present = 0
            if icon != None and icon != '':
                icon_present = 1



            # Draw the selection bar for selected items
            if menu.selected == choice and obj.visible:
                drawroundbox(x0 - obj.spacing + icon_present * icon_size * 1.2,
                             top - 2, x0 + obj.spacing + width,
                             top + font_h + 2, color = obj.bgcolor,
                             radius=obj.radius)

            if not text:
                print "no text to display ... strange. Use default"
                text = "unknown"

            # Draw icon
            if icon_present==1:
                icon_x = x0
                icon_y = y0 - (icon_size - font_h) / 2
                osd.drawbitmap(util.resize(icon, icon_size, icon_size), icon_x,
                               icon_y)


            show_name = (None, None, None, None)
            if config.TV_SHOW_REGEXP_MATCH(text):
                show_name = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(text))
                if show_name[0] and show_name[0][-1] == '(':
                    show_name[0] = None

            # TV show, align the text with all files from the same show
            if show_name[0]:
                x = x0
                DrawText(show_name[0], obj, x=x, y=top)

                season_w = 0
                volume_w = 0
                
                for i in menuw.menu_items:
                    if config.TV_SHOW_REGEXP_MATCH(i.name):
                        s = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(i.name))
                        if s[0] == show_name[0]:
                            season_w = max(osd.stringsize(s[1], font=obj.font, \
                                                          ptsize=obj.size)[0], season_w)
                            volume_w = max(osd.stringsize(s[2], font=obj.font, \
                                                          ptsize=obj.size)[0], volume_w)

                x = x + \
                    osd.stringsize('%s  ' % show_name[0], font=obj.font, \
                                   ptsize=obj.size)[0] - season_w + \
                    osd.stringsize(show_name[1], font=obj.font, ptsize=obj.size)[0]
                DrawText('%sx%s' % (show_name[1], show_name[2]), obj, x=x, y=top)

                x = x + season_w + volume_w + \
                    osd.stringsize('x  ', font=obj.font, ptsize=obj.size)[0]
                DrawTextFramed('-  %s' % show_name[3], obj, x=x, y=top,
                               width=width-(x-x0), height=-1, mode='hard')
                

            # normal items
            else:
		DrawTextFramed(text, obj, x=x0+icon_present*icon_size*1.2, y=top,
                               width=width - icon_present*icon_size*1.2,
                               mode='hard', height=-1)


            y0 += spacing
        

    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        if self.hold:
            print 'skin.drawmenu() hold!'
            return
        
        osd.clearscreen(osd.COL_BLACK)

        menu = menuw.menustack[-1]

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        if menu.item_types and menu.item_types in self.settings.e_menu and \
           hasattr(self, menu.item_types) and menuw.menu_items and self.extended_menu:

            if menu.skin_settings:
                val = menu.skin_settings
            else:
                val = self.settings

            eval('self.%s(menuw, val)' % menu.item_types)
            osd.update()
            return

        # find the correct structures:
        if menu.skin_settings:
            val = menu.skin_settings
        else:
            val = self.settings

        # now find the correct menu:
        if len(menuw.menustack) == 1:
            val = val.menu_main
        else:
            val = val.menu_default


        image_object, image_x, image_val = self.DrawMenu_Cover(menuw, val)

        if image_val:
            InitScreen(val, (val.background.mask, image_val.mask), image_x)
        else:
            InitScreen(val, (val.background.mask, None), image_x)

        # Menu heading
        if val.title.visible:
            if val.title.text:
                menu.heading = val.title.text
            text = menu.heading
            width = osd.width
            if val.title.width:
                width = val.title.width

            DrawTextFramed(text, val.title, x=val.title.x-width/2, width=width, height=-1)

        if val.logo.image and val.logo.visible:
            if val.logo.width and val.logo.height:
                osd.drawbitmap(util.resize(val.logo.image, val.logo.width, val.logo.height),
                               val.logo.x, val.logo.y)
            else:
                osd.drawbitmap(val.logo.image, val.logo.x, val.logo.y)

        if image_object:
            osd.drawbitmap(image_object, image_val.x, image_val.y)

            if image_val and image_val.border_size > 0:
                osd.drawbox(image_val.x - image_val.border_size,
                            image_val.y - image_val.border_size,
                            image_val.x + image_val.width + image_val.border_size,
                            image_val.y + image_val.height + image_val.border_size,
                            width = image_val.border_size,
                            color = image_val.border_color)
            

        # Draw the menu choices for the main selection
        y0 = val.items.y

        selection_length = val.items.width

        # if there is an image and the selection will be cover the image
        # shorten the selection

        if image_x and val.items.x + val.items.width > image_x:
            selection_length = image_x - val.items.x

        self.DrawMenu_Selection(menuw, val, val.items.x, val.items.y, selection_length, \
                                val.items.height)


        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y

        s_w, s_h = osd.stringsize("Ajg", font=val.submenu.selection.font,
                                  ptsize=val.submenu.selection.size)
        w, h = osd.stringsize("Ajg", font=val.submenu.font, ptsize=val.submenu.size)

        h = max(h, s_h)
        
        for item in menuw.nav_items:
            if menu.selected == item:
                drawroundbox(x0, y0, x0 + val.submenu.selection.length, 
                                 y0 + h,
                                 color=val.submenu.selection.bgcolor,
                                 radius=val.submenu.selection.radius)
                
                DrawTextFramed(item.name, val.submenu.selection,
                               x0+val.submenu.selection.spacing, y0,
                               x0 + val.submenu.selection.length-\
                               2*val.submenu.selection.spacing, 
                               y0 + h)
                
            else:
                DrawTextFramed(item.name, val.submenu, x0+val.submenu.spacing, y0,
                               x0 + val.submenu.selection.length-2*val.submenu.spacing, 
                               y0 + h)
            x0 += 190

        osd.update()
        

    def DrawMP3(self, info):

        val = self.settings.mp3
        iv  = val.info
	
	right = iv.width
	# XXX In case it's not defined in the XML
	# XXX This is just for the interim
	if right == 0: right = 500

        str_w_title, str_h_title = osd.stringsize('Title: ',iv.font, iv.size)
        str_w_artist, str_h_artist = osd.stringsize('Artist: ',iv.font, iv.size)
        str_w_album, str_h_album = osd.stringsize('Album: ',iv.font, iv.size)
        str_w_year, str_h_year = osd.stringsize('Year: ',iv.font, iv.size)
        str_w_track, str_h_track = osd.stringsize('Track: ',iv.font, iv.size)
        str_w_length, str_h_length = osd.stringsize('Length: ',iv.font, iv.size)
        str_w_time, str_h_time = osd.stringsize('Time: ',iv.font, iv.size)
        left = max( str_w_title, str_w_artist, str_w_album, str_w_year, \
                    str_w_track, str_w_length, str_w_time )
        left += iv.x

        spacing = iv.height / 7

        if info.drawall:

            if info.image:
                InitScreen(val, (val.background.mask,val.cover.mask), info.image)
            else:
                InitScreen(val, (val.background.mask,), info.image)
            
            if val.title.visible:
                osd.drawstring('Playing Music', val.title.x, val.title.y,
                               val.title.color, font=val.title.font,
                               ptsize=val.title.size, align=val.title.align)

            if val.logo.image and val.logo.visible:
                osd.drawbitmap(val.logo.image, val.logo.x, val.logo.y)

            #Display the cover image file if it is present
            if info.image:
                c = val.cover
                osd.drawbox(c.x - c.border_size, c.y - c.border_size, \
                            c.x + c.border_size + c.width, c.y + c.border_size + c.height,\
                            width=c.border_size, color=c.border_color)
                osd.drawbitmap(util.resize(info.image, c.width, c.height), c.x, c.y)
               
            file_name = info.filename.split('/')
            dir_name = ''
            for i in range(len(file_name)-1):
                dir_name += file_name[i] + '/'

            file_name = file_name[i+1]
            py = val.progressbar.y

            top = iv.y
            DrawText('Title: ', iv, x=left, y=top, align='right')
            DrawTextFramed('%s ' % info.name, iv, x=left, y=top, width=right,
                           height=(str_h_title+5), mode='soft')
            if info.artist:
                top += spacing
                DrawText('Artist: ', iv, x=left, y=top, align='right')
                DrawTextFramed('%s ' % info.artist, iv, x=left, y=top,
                               width=right,height=(str_h_artist+5), mode='soft')

            if info.album:
                top += spacing
                DrawText('Album: ', iv, x=left, y=top, align='right')
                DrawTextFramed('%s ' % info.album, iv, x=left, y=top,
                               width=right,height=(str_h_album+5), mode='soft')

            if info.year:
                top += spacing
                DrawText('Year: ', iv, x=left, y=top, align='right')
                DrawText('%s ' % info.year, iv, x=left, y=top)

	    if info.trackof > 0:
	    	top += spacing
		DrawText('Track: ', iv, x=left, y=top, align='right')
		DrawText('%s/%s' % (info.track, info.trackof), iv, x=left, y=top)
            elif info.track:
                top += spacing
                DrawText('Track: ', iv, x=left, y=top, align='right')
                DrawText('%s ' % info.track, iv, x=left, y=top)

            if info.length > 0:
                top += spacing
                DrawText('Length: ', iv, x=left, y=top, align='right')
                DrawText('%d:%02d ' % (int(info.length / 60), int(info.length % 60)), \
                         iv, x=left, y=top)

            top += spacing
            DrawText('Time: ', iv, x=left, y=top, align='right')

            # remember the surface to redraw it
            self.time_y = top
            self.time_surface = osd.getsurface(left, top, 100, spacing)
            
                
        else:

            # redraw the surface on some positions
            osd.putsurface(self.time_surface, left, self.time_y)


        # XXX I changed this because round rounds up on 3.58 etc. instead
        # XXX of giving us the desired "round down modulo" effect.
        el_min  = int(info.elapsed)/60
        el_sec  = int(info.elapsed)%60
        rem_min = int(info.remain)/60
        rem_sec = int(info.remain)%60

        str = '%s:%02d ' % (el_min, el_sec)
        DrawText(str, iv, x=left, y=self.time_y)

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
            pixels = info.elapsed * val.progressbar.width / info.length

            # the progress indicator:
            osd.drawbox(val.progressbar.x +1,
                        val.progressbar.y +1,
                        val.progressbar.x + pixels,
                        val.progressbar.y + val.progressbar.height -1,
                        width = -1,
                        color = val.progressbar.color)
            
        osd.update()


    # TV Guide:

    def DrawTVGuide(self):
        if 'tv' in self.settings.e_menu:
            self.tv.DrawTVGuide(self.settings.e_menu['tv'])
        
    def DrawTVGuide_Clear(self):
        if 'tv' in self.settings.e_menu:
            self.tv.DrawTVGuide_Clear(self.settings.e_menu['tv'])

    def DrawTVGuide_getExpand(self):
        if 'tv' in self.settings.e_menu:
            return self.tv.DrawTVGuide_getExpand(self.settings.e_menu['tv'])

    def DrawTVGuide_setExpand(self, expand):
        if 'tv' in self.settings.e_menu:
            return self.tv.DrawTVGuide_setExpand(expand, self.settings.e_menu['tv'])

    def DrawTVGuide_View(self, to_view):
        if 'tv' in self.settings.e_menu:
            return self.tv.DrawTVGuide_View(to_view, self.settings.e_menu['tv'])

    def DrawTVGuide_Info(self, to_info):
        if 'tv' in self.settings.e_menu:
            return self.tv.DrawTVGuide_Info(to_info, self.settings.e_menu['tv'])
                         
    def DrawTVGuide_ItemsPerPage(self):
        if 'tv' in self.settings.e_menu:
            return self.tv.DrawTVGuide_ItemsPerPage(self.settings.e_menu['tv'])

    def DrawTVGuide_Listing(self, to_listing):
        if 'tv' in self.settings.e_menu:
            return self.tv.DrawTVGuide_Listing(to_listing, self.settings.e_menu['tv'])


    def format_track (self, array):
        """ Return a formatted string for use in music.py """
	# This is the default - track name only
	formatstr = '%(t)s'
       	# This will show the track number as well 
	#formatstr = '%(n)s - %(t)s'

	# Since we can't specify the length of the integer in the
	# format string (Python doesn't seem to recognize it) we
	# strip it out first, when we see the only thing that can be
	# a number.


        # Before we begin, make sure track is an integer
    
        if array.track:
            try:
    	        mytrack = ('%0.2d' % int(array.track))
            except:
    	        mytrack = None
        else:
           mytrack = None
    
        song_info = {  'a'  : array.artist,
       	               'l'  : array.album,
    	               'n'  : mytrack,
    	               't'  : array.title,
    	               'y'  : array.year }
   
        return formatstr % song_info
