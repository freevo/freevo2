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
# Revision 1.2  2002/10/08 15:25:29  outlyer
# Moved the logo to the upper left corner; looks cleaner and doesn't
# interfere with the menus
#
# Revision 1.1  2002/10/07 04:39:44  outlyer
# Continuing to fix the stupid mistake I made.
#
# Revision 1.1  2002/10/07 04:33:55  outlyer
# Crap. I think I just overwrote the default skin because I forgot to rename my skin to
# skin_aubin1. I'll revert in a second. Argh.
#
# Revision 1.36  2002/10/07 04:16:35  outlyer
# The rough draft of the skin I showed some screenshots of. It uses the images
# I just added to create some nice alpha masking. You'll also need a bunch of
# things which I can't commit if you want to get the exact look:
# 1. Arial_Bold.ttf - get it from a Windows box, or if you have the Truetype font
# package from Microsoft
# 2. the MythTV background - get it from them; they won't let us use it.
#
# There will also be a seperate XML file which I'll commit in a minute.
#
# Revision 1.35  2002/10/06 14:35:19  dischi
# log message cleanup and removed a debug message
#
# Revision 1.34  2002/10/05 18:16:37  dischi
# Don't copy settings, we want to override it
#
# Revision 1.33  2002/10/05 18:10:56  dischi
# Added support for a local_skin.xml file. See Docs/documentation.html
# section 4.1 for details. An example is also included.
#
# Revision 1.32  2002/10/05 17:25:45  dischi
# Added ability to display shadows for title as well (deactivated in the
# xml file)
#
# Revision 1.31  2002/09/27 08:43:38  dischi
# removed 2 debugs again, this makes no sense.
#
# Revision 1.30  2002/09/27 08:39:10  dischi
# More debug for error location
#
# Revision 1.29  2002/09/26 09:20:58  dischi
# Fixed (?) bug when using freevo_runtime. Krister, can you take a look
# at that?
#
# Revision 1.28  2002/09/25 18:53:43  dischi
# Added border around the cover image (set by the xml file border_size
# and border_color)
#
# Revision 1.27  2002/09/24 02:17:00  gsbarbieri
# In DrawMP3 changed the layout, now the labels ('Title: ', 'Author: ', ...) are right aligned.
#
# Revision 1.26  2002/09/23 19:01:06  dischi
# o Added alignment from the xml file for fonts
# o Added PopupBox from gui classes (looks better)
# o cleanup: improved DrawText(...) and now the code looks much
#   better, also alignment works for all texts
#
# Revision 1.25  2002/09/23 18:16:48  dischi
# removed shadow mode
#
# Revision 1.24  2002/09/22 09:54:31  dischi
# XML cleanup. Please take a look at the new skin files to see the new
# structure. The 640x480 skin is also workin now, only one small bug
# in the submenu (seems there is something hardcoded).
#
# Revision 1.23  2002/09/21 10:08:53  dischi
# Added the function PopupBox. This function is identical with
# osd.popup_box, but drawing a popup box should be part of the skin.
#
# Revision 1.22  2002/09/20 19:18:59  dischi
# o added ItemsPerMenuPage and adapted some stuff that it works
# o integrated the tv show alignment from dischi1 (testfiles needed to show
#   that feature)
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
import osd,pygame


# XXX Krister, please change this to 1 and start freevo with and
# without the runtime. Very strange.

SHOW_FREEVO_RUNTIME_BUG=0

if not SHOW_FREEVO_RUNTIME_BUG:
    sys.path.append(os.path.abspath('./gui'))
    from Color import Color
    from PopupBox import PopupBox
    from Label import Label
    
else:
    import gui

    
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

    if DEBUG: print 'Skin: Loading XML file %s' % config.SKIN_XML_FILE
    
    settings = xml_skin.XMLSkin()
    settings.load(config.SKIN_XML_FILE)

    if os.path.isfile("local_skin.xml"):
        if DEBUG: print 'Skin: Add local config to skin'
        settings.load("local_skin.xml")

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
        
        # get the settings
        if menu.skin_settings:
            val = menu.skin_settings.menu
        else:
            val = self.settings.menu

        used_height = 0
        n_items     = 0

        for item in menu.choices[menu.page_start : len(menu.choices)]:
            if item.type:
                if item.type == 'dir':
                    pref_item = val.items.dir
                elif item.type == 'list':
                    pref_item = val.items.pl
                elif item.type == 'main':
                    pref_item = val.item_main
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
        text  STring to display

        Draw a popupbox with an optional icon and a text.
        
        Notes: Should maybe be named print_message or show_message.
               Maybe I should use one common box item.
        """
        left   = (osd.width/2)-180
        top    = (osd.height/2)-30
        width  = 360
        height = 60
        icn    = icon
        bd_w   = 2

        if not SHOW_FREEVO_RUNTIME_BUG:
            bg_c   = Color(osd.default_bg_color)
            fg_c   = Color(osd.default_fg_color)

            bg_c.set_alpha(192)

            pb = PopupBox(left, top, width, height, icon=icn, bg_color=bg_c,
                          fg_color=fg_c, border='flat', bd_width=bd_w)
            pb.set_text(text)
            pb.set_h_align(Label.CENTER)

        else:
            bg_c   = gui.Color(osd.default_bg_color)
            fg_c   = gui.Color(osd.default_fg_color)

            bg_c.set_alpha(192)

            pb = gui.PopupBox(left, top, width, height, icon=icn, bg_color=bg_c,
                              fg_color=fg_c, border='flat', bd_width=bd_w)

            pb.set_text(text)
            pb.set_h_align(gui.Label.CENTER)

        pb.set_font('skins/fonts/bluehigh.ttf', 24)
        pb.show()
        
        osd.update()
        

    # Draws a text based on the settings in the XML file
    def DrawText(self, text, settings, x=-1, y=-1):
        if x == -1:
            x = settings.x
        if y == -1:
            y = settings.y
            
        if settings.shadow_visible:
            osd.drawstring(text, x+settings.shadow_pad_x, y+settings.shadow_pad_y,
                           settings.shadow_color, None, settings.font,
                           settings.size, settings.align)
        osd.drawstring(text, x, y, settings.color, None, settings.font,
                       settings.size, settings.align)


    def DrawMenu_Cover(self, menuw, settings):
        image_x = 0
        val = settings
        menu = menuw.menustack[-1]
        
        # display the image and store the x0 position of the image
        for item in menuw.menu_items:
            image = item.image
            i_val = None
            
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
                            i_val = val.cover_image
                            
                elif type == 'movie' and val.cover_movie.visible:
                    image_x = val.cover_movie.x
                    if menu.selected == item:
                        osd.drawbitmap(util.resize(image, val.cover_movie.width, \
                                                   val.cover_movie.height),\
                                       val.cover_movie.x, val.cover_movie.y)
			osd.drawbitmap('skins/images/moviebox.png',-1,-1)
                        i_val = val.cover_movie

                elif type == 'music' and val.cover_music.visible:
                    image_x = val.cover_music.x
                    if menu.selected == item:
                        osd.drawbitmap(util.resize(image, val.cover_music.width, \
                                                   val.cover_music.height),\
                                       val.cover_music.x, val.cover_music.y)
                        i_val = val.cover_music

                if i_val and i_val.border_size > 0:
                    osd.drawbox(i_val.x - i_val.border_size,
                                i_val.y - i_val.border_size,
                                i_val.x + i_val.width + i_val.border_size,
                                i_val.y + i_val.height + i_val.border_size,
                                width = i_val.border_size,
                                color = i_val.border_color)
            
        return image_x


    
    def DrawMenu_Selection(self, menuw, settings, x0, y0, width, height):
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

                # XXX BAD HACK (tm)
                # overwrite settings for main
                elif choice.type == 'main':
                    item = val.item_main
                    valign = 1
                    x0 = val.item_main.x
                    width = val.item_main.width
                    
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
                osd.drawbox(x0 - 8, top - 2, x0 - 8 + width, top + font_h + 2,
                            width = -1, color = ((160 << 24) | obj.bgcolor))

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
                self.DrawText(show_name[0], obj, x=x, y=top)

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
                self.DrawText('%sx%s' % (show_name[1], show_name[2]), obj, x=x, y=top)

                x = x + season_w + volume_w + \
                    osd.stringsize('x  ', font=obj.font, ptsize=obj.size)[0]
                self.DrawText('-  %s' % show_name[3], obj, x=x, y=top)
                

            # normal items
            else:
                self.DrawText(text, obj, x=x0, y=top)

            # draw icon
            if choice.icon != None:
                icon_x = item.x - icon_size - 15
                osd.drawbitmap(util.resize(choice.icon, icon_size, icon_size), icon_x, y0)

            y0 += spacing
        

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

            self.DrawText(menu.heading, val.title)
            
	osd.drawbitmap('skins/images/logo.png',10,10)
        # Draw the menu choices for the main selection
        y0 = val.items.y

        image_x = self.DrawMenu_Cover(menuw, val)

        selection_length = val.items.width

        # if there is an image and the selection will be cover the image
        # shorten the selection

        if image_x and val.items.x - 8 + val.items.width > image_x - 30:
            selection_length = image_x - 30 - val.items.x + 8

        self.DrawMenu_Selection(menuw, val, val.items.x, val.items.y, selection_length, \
                                val.items.height)


        # Draw the menu choices for the meta selection
        x0 = val.submenu.x
        y0 = val.submenu.y
        
        for item in menuw.nav_items:
            if menu.selected == item:
                osd.drawbox(x0 - 4, y0 - 3, x0 + val.submenu.selection.length, 
                            y0 + val.submenu.selection.size*1.5,
                            width=-1,
                            color=((160 << 24) | val.submenu.selection.bgcolor))
                
                self.DrawText(item.name, val.submenu.selection, x=x0, y=y0)
                
            else:
                self.DrawText(item.name, val.submenu, x=x0, y=y0)
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
            osd.drawstring(menu.heading, val.title.x, val.title.y,
                           val.title.color, font=val.title.font,
                           ptsize=val.title.size, align=val.title.align)

        # Sub menus
        icon_size = 25

        x0 = val.items.x
        y0 = val.items.y
        height = val.items.height

        fontsize = val.items.default.size


	osd.drawbitmap('skins/images/tvmask.png',-1,-1)

        if menu.packrows:
            w, h = osd.stringsize('Ajg', font=val.items.default.font,
                                  ptsize=fontsize)
            spacing = h + PADDING
        else:
            spacing = height / max(len(menuw.menu_items),1)

        # image to display
        image = None
        
        
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
            w, h = osd.stringsize(row[0], font=val.items.default.font,
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
            osd.drawstring(rows[row][0], x0, y0, val.items.default.color,
                           font=val.items.default.font,
                           ptsize=fontsize)
            
            if menu.selected == choice:
                osd.drawbox(x0 - 3, y0 - 3,
                            x0 + maxwidth + 3,
                            y0 + fontsize*1.5 + 1, width=-1,
                            color=((160 << 24) | val.items.default.selection.bgcolor))

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
                
                w, h = osd.stringsize(row[col], font=val.items.default.font,
                                      ptsize=fontsize)
                maxwidth = max(maxwidth, w)

            # Draw the column strings for all rows
            for row in rows:
                if col < len(row): 
                    osd.drawstring(row[col], x0, y0, val.items.default.color,
                                   font=val.items.default.font,
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
                
                self.DrawText(item.name, val.submenu.selection, x=x0, y=y0)
            else:
                self.DrawText(item.name, val.submenu, x=x0, y=y0)
            x0 += 190

        osd.update()


    def DrawMP3(self, info):

        val = self.settings.mp3
        val2 = copy.copy(val)
        val2.align = 'right'

        str_w_title, str_h_title = osd.stringsize('Title: ',val2.font, val2.size)
        str_w_artist, str_h_artist = osd.stringsize('Artist: ',val2.font, val2.size)
        str_w_album, str_h_album = osd.stringsize('Album: ',val2.font, val2.size)
        str_w_year, str_h_year = osd.stringsize('Year: ',val2.font, val2.size)
        str_w_track, str_h_track = osd.stringsize('Track: ',val2.font, val2.size)
        str_w_time, str_h_time = osd.stringsize('Time: ',val2.font, val2.size)
        left = max( str_w_title, str_w_artist, str_w_album, str_w_year, str_w_track, str_w_time )
        left += 30

        if info.drawall:
            osd.clearscreen()

            if val.bgbitmap[0]:
                apply(osd.drawbitmap, (val.bgbitmap, -1, -1))
        
	    osd.drawbitmap('skins/images/highlight.png',-1,-1)

            #Display the cover image file if it is present
            if info.image:
                osd.drawbox(465,190, 755, 480, width=1, color=0x000000)   
                osd.drawbitmap(util.resize(info.image, 289, 289), 466, 191)
               
            file_name = info.filename.split('/')
            dir_name = ''
            for i in range(len(file_name)-1):
                dir_name += file_name[i] + '/'

            file_name = file_name[i+1]
            py = val.progressbar.y
                
            self.DrawText('Title: ', val2, x=left, y=100)

            self.DrawText('%s ' % info.title, val, x=left, y=100)
 
            self.DrawText('Artist: ', val2, x=left, y=130)
            self.DrawText('%s ' % info.artist, val, x=left, y=130)

            self.DrawText('Album: ', val2, x=left, y=160)
            self.DrawText('%s ' % info.album, val, x=left, y=160)
        
            self.DrawText('Year: ', val2, x=left, y=190)
            self.DrawText('%s ' % info.year, val, x=left, y=190)

            self.DrawText('Track: ', val2, x=left, y=220)
            self.DrawText('%s ' % info.track, val, x=left, y=220)

            self.DrawText('Time: ', val2, x=left, y=250)

                
        else:
            # Erase the portion that will be redrawn
            if val.bgbitmap[0]:
                osd.drawbitmap( val.bgbitmap, left, 250, None, left,
                                250, 100, 30 )
	        #osd.drawbitmap('skins/images/highlight.png', left, 250, None, left,
		#		250, 100, 30)
		box = pygame.Surface((100,30),0,32)
		box.fill ((0,0,0))
		box.set_alpha(128)
		osd.screen.blit(box,(left,250))

        # XXX I changed this because round rounds up on 3.58 etc. instead
        # XXX of giving us the desired "round down modulo" effect.
        el_min  = int(info.elapsed)/60
        el_sec  = int(info.elapsed)%60
        rem_min = int(info.remain)/60
        rem_sec = int(info.remain)%60

        str = '%s:%02d ' % (el_min, el_sec)
        self.DrawText(str, val, x=left, y=250)

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
    
