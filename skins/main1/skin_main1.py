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
# Revision 1.44  2002/10/20 09:19:12  dischi
# bugfix
#
# Revision 1.43  2002/10/19 17:10:51  dischi
# some small bugfixes
#
# Revision 1.42  2002/10/19 15:09:55  dischi
# added alpha mask support
#
# Revision 1.41  2002/10/16 19:40:34  dischi
# some cleanups
#
# Revision 1.40  2002/10/16 04:58:16  krister
# Changed the main1 skin to use Gustavos new extended menu for TV guide, and Dischis new XML code. grey1 is now the default skin, I've tested all resolutions. I have not touched the blue skins yet, only copied from skin_dischi1 to skins/xml/type1.
#
# Revision 1.16  2002/10/15 19:57:56  dischi
# Added extended menu support
#
# Revision 1.15  2002/10/14 18:47:00  dischi
# o added scale support, you can define a scale value for the import
#   grey640x480 and grey768x576 are very simple now
# o renamed the xml files
#
# Revision 1.14  2002/10/13 14:16:55  dischi
# Popup box and mp3 player are now working, too. This skin can look
# like main1 and aubin1. I droped the support for the gui classes
# because there are not powerfull enough
#
# Revision 1.13  2002/10/12 19:00:55  dischi
# deactivated the movie box since we don't have informations for this
# right now.
#
# Revision 1.12  2002/10/12 18:45:25  dischi
# New skin, Work in progress
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
        if not settings.load("%s%s.xml" % (config.SKIN_XML_FILE, config.CONF.geometry)):
            if not settings.load("%s/%s_%s.xml" % (XML_SKIN_DIRECTORY, config.SKIN_XML_FILE, \
                                                   config.CONF.geometry)):
                print "skin not found, using fallback skin"
                settings.load("%s/grey1_%s.xml" % (XML_SKIN_DIRECTORY, config.CONF.geometry))
        
    if os.path.isfile("local_skin.xml"):
        if DEBUG: print 'Skin: Add local config to skin'
        settings.load("local_skin.xml")

    hold = 0


    def __init__(self):
        self.tv = main1_tv.Skin_TV()
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


    def ItemsPerMenuPage(self, menu):
        
        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        # hack for the main menu to fit all in one screen
        if not menu.packrows:
            return 5
        
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
                return n_items

        return n_items
        


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
            osd.drawroundbox(x0-val.spacing, y0-val.spacing, x1+val.spacing,
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
                (type, image) = image
            if image:
                if type == 'photo' and val.cover_image.visible:
                    image_x = val.cover_image.x-val.cover_image.spacing
                    if menu.selected == item:
                        thumb = util.getExifThumbnail(image, val.cover_image.width, \
                                                      val.cover_image.height)
                        if thumb:
                            i_file = thumb
                            i_val = val.cover_image
                            
                elif type == 'movie' and val.cover_movie.visible:
                    image_x = val.cover_movie.x-val.cover_movie.spacing
                    if menu.selected == item:
                        i_file = util.resize(image, val.cover_movie.width, \
                                             val.cover_movie.height)
                        i_val = val.cover_movie

                elif type == 'music' and val.cover_music.visible:
                    image_x = val.cover_music.x-val.cover_music.spacing
                    if menu.selected == item:
                        i_file = util.resize(image, val.cover_music.width, \
                                             val.cover_music.height)
                        i_val = val.cover_music


        return max(0, image_x-val.items.default.selection.spacing), i_val, i_file


    
    def DrawMenu_Selection(self, menuw, settings, x0, y0, width, height, layer=None):
        val = settings
        menu = menuw.menustack[-1]

        if menu.packrows:
            spacing = 0                 # calculate this later
            icon_size = 28
        else:
            spacing = height / max(len(menuw.menu_items),1)
            icon_size = 64


        for choice in menuw.menu_items:

            if menu.selected == choice:
                image = choice.image

            # Pick the settings for this kind of item
            valign = 0 # Vertical aligment to the icon
            if choice.type:

                if choice.type == 'dir':
                    item = val.items.dir
                elif choice.type == 'list':
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
            font_w, font_h = osd.stringsize(text, font=obj.font, ptsize=obj.size)

            if not spacing:
                spacing = font_h + PADDING
            
            # Draw the menu item text, shorten the text before to fit
            # the selection length

            if font_w + 26 > width:
                text = text + "..."
                    
            while font_w + 26 > width:
                text = text[0:-4] + "..."
                font_w, font_h = osd.stringsize(text, font=obj.font, ptsize=obj.size)


            # Try and center the text to the middle of the icon
            if valign:
                top = y0 + (icon_size - font_h) / 2
            else:
                top = y0

            # Draw the selection bar for selected items
            if menu.selected == choice and obj.visible:
                osd.drawroundbox(x0 - obj.spacing, top - 2, x0 + obj.spacing + width,
                                 top + font_h + 2, color = obj.bgcolor,
                                 radius=obj.radius, layer=layer)

            if not text:
                print "no text to display ... strange. Use default"
                text = "unknown"

            show_name = (None, None, None, None)
            if config.TV_SHOW_REGEXP_MATCH(text):
                show_name = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(text))
                if show_name[0][-1] == '(':
                    show_name[0] = None

            # TV show, align the text with all files from the same show
            if show_name[0]:
                x = x0
                DrawText(show_name[0], obj, x=x, y=top, layer=layer)

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
                DrawText('%sx%s' % (show_name[1], show_name[2]), obj, x=x, y=top,
                         layer=layer)

                x = x + season_w + volume_w + \
                    osd.stringsize('x  ', font=obj.font, ptsize=obj.size)[0]
                DrawText('-  %s' % show_name[3], obj, x=x, y=top, layer=layer)
                

            # normal items
            else:
                DrawText(text, obj, x=x0, y=top, layer=layer)

            # draw icon
            if choice.icon != None:
                icon_x = x0 - icon_size - 15
                icon_y = y0 - (icon_size - font_h) / 2
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size), icon_x,
                               icon_y, layer=layer)

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
            
        image_x, image_val, image_file = self.DrawMenu_Cover(menuw, val)

        if image_val:
            layer = InitScreen(val, (val.background.mask, image_val.mask), image_x)
        else:
            layer = InitScreen(val, (val.background.mask, None), image_x)

        # Menu heading
        if val.title.visible:
            if val.title.text:
                menu.heading = val.title.text

            DrawText(menu.heading, val.title, layer=layer)

        if val.logo.image and val.logo.visible:
            if val.logo.width and val.logo.height:
                osd.drawbitmap(util.resize(val.logo.image, val.logo.width, val.logo.height),
                               val.logo.x, val.logo.y)
            else:
                osd.drawbitmap(val.logo.image, val.logo.x, val.logo.y, layer=layer)

        if image_file:
            osd.drawbitmap(image_file, image_val.x, image_val.y, layer=layer)

            if image_val and image_val.border_size > 0:
                osd.drawbox(image_val.x - image_val.border_size,
                            image_val.y - image_val.border_size,
                            image_val.x + image_val.width + image_val.border_size,
                            image_val.y + image_val.height + image_val.border_size,
                            width = image_val.border_size,
                            color = image_val.border_color,
                            layer=layer)
            

        # Draw the menu choices for the main selection
        y0 = val.items.y

        selection_length = val.items.width

        # if there is an image and the selection will be cover the image
        # shorten the selection

        if image_x and val.items.x + val.items.width > image_x:
            selection_length = image_x - val.items.x

        self.DrawMenu_Selection(menuw, val, val.items.x, val.items.y, selection_length, \
                                val.items.height, layer=layer)


        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y

        s_w, s_h = osd.stringsize("Ajg", font=val.submenu.selection.font,
                                  ptsize=val.submenu.selection.size)
        w, h = osd.stringsize("Ajg", font=val.submenu.font, ptsize=val.submenu.size)

        h = max(h, s_h)
        
        for item in menuw.nav_items:
            if menu.selected == item:
                osd.drawroundbox(x0, y0, x0 + val.submenu.selection.length, 
                                 y0 + h,
                                 color=val.submenu.selection.bgcolor,
                                 radius=val.submenu.selection.radius, layer=layer)
                
                DrawTextFramed(item.name, val.submenu.selection,
                               x0+val.submenu.selection.spacing, y0,
                               x0 + val.submenu.selection.length-\
                               2*val.submenu.selection.spacing, 
                               y0 + h, layer=layer)
                
            else:
                DrawTextFramed(item.name, val.submenu, x0+val.submenu.spacing, y0,
                               x0 + val.submenu.selection.length-2*val.submenu.spacing, 
                               y0 + h, layer=layer)
            x0 += 190

        ShowScreen(layer)
        

    def DrawMP3(self, info):

        val = self.settings.mp3
        iv  = val.info

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
                PutLayer(InitScreen(val, (val.background.mask,val.cover.mask), info.image))
            else:
                PutLayer(InitScreen(val, (val.background.mask,), info.image))
            
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
            DrawText('%s ' % info.title, iv, x=left, y=top)

            if info.artist:
                top += spacing
                DrawText('Artist: ', iv, x=left, y=top, align='right')
                DrawText('%s ' % info.artist, iv, x=left, y=top)

            if info.album:
                top += spacing
                DrawText('Album: ', iv, x=left, y=top, align='right')
                DrawText('%s ' % info.album, iv, x=left, y=top)

            if info.year:
                top += spacing
                DrawText('Year: ', iv, x=left, y=top, align='right')
                DrawText('%s ' % info.year, iv, x=left, y=top)

            if info.track:
                top += spacing
                DrawText('Track: ', iv, x=left, y=top, align='right')
                DrawText('%s ' % info.track, iv, x=left, y=top)

            top += spacing
            DrawText('Length: ', iv, x=left, y=top, align='right')
            DrawText('%s:%s ' % (info.length / 60, info.length % 60), \
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
            pixels = int(round((info.done)/100 * val.progressbar.width))

            # the progress indicator:
            osd.drawbox(val.progressbar.x +1,
                        val.progressbar.y +1,
                        val.progressbar.x + pixels,
                        val.progressbar.y + val.progressbar.height -1,
                        width = -1,
                        color = val.progressbar.color)
            
        osd.update()



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
