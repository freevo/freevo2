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
# Revision 1.63  2002/11/23 19:50:29  dischi
# cleanup
#
# Revision 1.62  2002/11/21 05:23:44  krister
# Made the main menu fonts and icons larger. Made the icon sizes scale with the resolution.
#
# Revision 1.61  2002/11/20 22:07:32  dischi
# small fix for my code cleanup
#
# Revision 1.60  2002/11/20 03:44:57  krister
# Dirty fix in the skin to display the new icons better, the icons should be resized instead.
#
# Revision 1.59  2002/11/19 22:04:15  dischi
# Some changes I had to made to integrate a first version of my code
# cleanup. This shouldn't break anything and it should work as before.
#
# Revision 1.58  2002/11/01 20:05:11  dischi
# Make it possible to set deactivate the submenu. Just put
# <submenu visible="no"> in the xml file. If there are no "normal" menu
# items the submenu item BACK will be displayed to have at least one
# item to select.
#
# Revision 1.57  2002/10/30 16:34:25  outlyer
# Don't crash if show_name[0][-1] is undefined.
#
# (I had files named: 1x14 - something.avi, and it matched the TV SHOW regexp
# but it crashed since show_name[0] was undefined, so FIRST check if show_name[0]
# is undefined before doing something with the show_name[0])
#
# Revision 1.56  2002/10/28 21:32:42  dischi
# Oops
#
# Revision 1.55  2002/10/26 12:27:45  dischi
# Keep the aspect ratio for image thumbnails, also show thumbnails for
# images smaller 1100x800. Maybe these values are too high, for larger
# images it takes too much time to generate thumbnails on-the-fly.
#
# Revision 1.54  2002/10/25 20:11:14  dischi
# Added support for screenshots instead of cover for the movie browser.
# For covers is width < height, for screenshots not and to scale them
# looks odd. So if width > height, it's a screenshot. Keep the ratio
# and scale it to the width from the xml file. Than check for round
# boxes alpha masks in this section and when they are around the cover
# shorten the height of the boxes, too.
#
# Revision 1.53  2002/10/24 22:16:50  outlyer
# We're now using the width field in the fileinfo tag of the XML to decide
# how wide to write the MP3 data on the screen. This removes the hardcoded
# '500's from the skin
#
# Revision 1.52  2002/10/24 22:03:50  outlyer
# Changed the DrawTextFramed line to use a hard line height based on the
# actual height of the displayed string. This way, it's font, skin and
# screen size independent.
#
# Revision 1.51  2002/10/24 21:34:12  outlyer
# Changed to use two digits if track is specified. I still can't get Python
# to accept string = '%0.2(n)s' % int(a) without crashing.
#
# Revision 1.50  2002/10/24 21:19:58  outlyer
# No visible change, but now, we have a function called:
# skin.format_trackr() which takes in the array of id3 tag data and generates
# the track names for the mp3 browser. By default, it just shows the track
# name as it did before, but by editing the formatstr (currently IN the
# function) you can set it to show any combination of artist, album, year,
# track number, and title.
#
# Revision 1.49  2002/10/24 20:20:50  dischi
# Set height to -1 (font height) to avoid non showing because of the
# fixed height. If no one is working on the width=500 thing I will fix
# that this weekend.
#
# Revision 1.48  2002/10/24 06:11:45  krister
# Changed debug levels for less output. Don't display length in DrawMP3 if not valid.
#
# Revision 1.47  2002/10/24 05:28:40  outlyer
# Modified to match the new stuff included in the audioinfo library. We can
# now show the track number for an id3v2.x track, and we truncate the title,
# album and artist if they fall outside of the mask.
#
# Revision 1.46  2002/10/21 20:30:50  dischi
# The new alpha layer support slows the system down. For that, the skin
# now saves the last background/alpha layer combination and can reuse it.
# It's quite a hack, the main skin needs to call drawroundbox in main1_utils
# to make the changes to the alpha layer. Look in the code, it's hard to
# explain, but IMHO it's faster now.
#
# Revision 1.45  2002/10/20 16:03:20  outlyer
# Force seconds in mp3 player to be displayed as two digits. (Previously, if
# a track was 2 min, 03 sec, it would show as 2:3, now it's 2:03)
#
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

                # fix for the new code, I renamed some stuff
                if type == 'video':
                    type = 'movie'
                    
                if type == 'photo' and val.cover_image.visible:
                    image_x = val.cover_image.x-val.cover_image.spacing
                    if menu.selected == item:
                        thumb = util.getExifThumbnail(image)
                        if not thumb:
                            thumb = image

                        w, h = util.pngsize(thumb)

                        # don't make thumbnails for very large images when
                        # they don't have a thumbnail in the exif header, it
                        # takes too much time
                        if w<1100 and h<800:
                            scale = min(float(val.cover_image.width) / w,
                                        float(val.cover_image.height) / h)
                            
                            i_file = util.resize(thumb, int(w*scale), int(h*scale))
                            i_val = copy.deepcopy(val.cover_image)
                        
                            # check all round masks if they are around the image
                            # and shorten the width of those who are to fit
                            # the new size
                            if isinstance(i_val.mask, list):
                                for m in i_val.mask:
                                    if m.x <= i_val.x and m.y <= i_val.y and \
                                       m.width >= i_val.width and \
                                       m.height >= i_val.height:
                                        m.height -= val.cover_image.height-h*scale
                                        m.width -= val.cover_image.width-w*scale
                                    
                            i_val.height = h*scale
                            i_val.width  = w*scale


                elif type == 'movie' and val.cover_movie.visible:
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

                elif type == 'music' and val.cover_music.visible:
                    image_x = val.cover_music.x-val.cover_music.spacing
                    if menu.selected == item:
                        i_file = util.resize(image, val.cover_music.width, \
                                             val.cover_music.height)
                        i_val = val.cover_music


        return max(0, image_x-val.items.default.selection.spacing), i_val, i_file


    
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
                drawroundbox(x0 - obj.spacing, top - 2, x0 + obj.spacing + width,
                                 top + font_h + 2, color = obj.bgcolor,
                                 radius=obj.radius)

            if not text:
                print "no text to display ... strange. Use default"
                text = "unknown"

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
                DrawText('-  %s' % show_name[3], obj, x=x, y=top)
                

            # normal items
            else:
                DrawText(text, obj, x=x0, y=top)

            # draw icon
            if choice.icon != None:
                icon_x = x0 - icon_size - 15
                icon_y = y0 - (icon_size - font_h) / 2
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size), icon_x,
                               icon_y)

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
            InitScreen(val, (val.background.mask, image_val.mask), image_x)
        else:
            InitScreen(val, (val.background.mask, None), image_x)

        # Menu heading
        if val.title.visible:
            if val.title.text:
                menu.heading = val.title.text

            DrawText(menu.heading, val.title)

        if val.logo.image and val.logo.visible:
            if val.logo.width and val.logo.height:
                osd.drawbitmap(util.resize(val.logo.image, val.logo.width, val.logo.height),
                               val.logo.x, val.logo.y)
            else:
                osd.drawbitmap(val.logo.image, val.logo.x, val.logo.y)

        if image_file:
            osd.drawbitmap(image_file, image_val.x, image_val.y)

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
            if hasattr(info, 'title'):
                DrawTextFramed('%s ' % info.title, iv, x=left, y=top, width=right,
                               height=(str_h_title+5), mode='soft')
            else:
                DrawTextFramed('%s ' % info.name, iv, x=left, y=top, width=right,
                               height=(str_h_title+5), mode='soft')
            if info.artist:
                top += spacing
                DrawText('Artist: ', iv, x=left, y=top, align='right')
                DrawTextFramed('%s ' % info.artist, iv, x=left, y=top, width=right,height=(str_h_artist+5), mode='soft')

            if info.album:
                top += spacing
                DrawText('Album: ', iv, x=left, y=top, align='right')
                DrawTextFramed('%s ' % info.album, iv, x=left, y=top, width=right,height=(str_h_album+5), mode='soft')

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
