#if 0
# -----------------------------------------------------------------------
# skin_dischi1.py - Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.46  2003/03/30 18:05:25  dischi
# give correct skin information to the gui object
#
# Revision 1.45  2003/03/30 17:42:03  dischi
# image.fxd is no real skin
#
# Revision 1.44  2003/03/30 14:13:23  dischi
# (listing.py from prev. checkin has the wrong log message)
# o tvlisting now has left/right items and the label width is taken from the
#   skin xml file. The channel logos are scaled to fit that space
# o add image load function to area
# o add some few lines here and there to make it possible to force the
#   skin to a specific layout
# o initial display style is set to config.SKIN_START_LAYOUT
#
# Revision 1.43  2003/03/27 20:11:00  dischi
# Fix endless loop on empty directories (and added a messages)
#
# Revision 1.42  2003/03/23 21:40:31  dischi
# small bugfixes for loading a new skin
#
# Revision 1.41  2003/03/23 19:57:11  dischi
# Moved skin xml files to skins/xml/type1 and all stuff for blue_round2 to
# skins/xml/blue_round2
#
# Revision 1.40  2003/03/22 22:21:41  dischi
# DISPLAY can now toggle between more than two styles. The video menu
# has a 3rd style, all infos. Press DISPLAY two times on a video item
# (should be a fxd file to see everything)
#
# Revision 1.39  2003/03/22 20:08:30  dischi
# Lots of changes:
# o blue2_big and blue2_small are gone, it's only blue2 now
# o Support for up/down arrows in the listing area
# o a sutitle area for additional title information (see video menu in
#   blue2 for an example)
# o some layout changes in blue2 (experimenting with the skin)
# o the skin searches for images in current dir, skins/images and icon dir
# o bugfixes
#
# Revision 1.38  2003/03/16 19:36:06  dischi
# Adjustments to the new xml_parser, added listing type 'image+text' to
# the listing area and blue2, added grey skin. It only looks like grey1
# in the menu. The skin inherits from blue1 and only redefines the colors
# and the fonts. blue2 now has an image view for the image menu.
#
# Revision 1.37  2003/03/15 17:20:07  dischi
# renamed skin.xml to folder.fxd
#
# Revision 1.36  2003/03/13 21:02:05  dischi
# misc cleanups
#
# Revision 1.35  2003/03/13 19:57:08  dischi
# add font height information to font
#
# Revision 1.34  2003/03/08 17:36:47  dischi
# integration of the tv guide
#
# Revision 1.33  2003/03/07 17:27:48  dischi
# added support for extended menus
#
# Revision 1.32  2003/03/05 21:57:11  dischi
# Added audio player. The info area is empty right now, but this skin
# can player audio files
#
# Revision 1.31  2003/03/05 20:08:18  dischi
# More speed enhancements. It's now faster than the keyboard control :-)
#
# Revision 1.30  2003/03/05 19:20:47  dischi
# cleanip
#
# Revision 1.29  2003/03/04 22:46:33  dischi
# VERY fast now (IMHO as fast as we can get it). There are some cleanups
# necessary, but it's working. area.py only blits the parts of the screen
# that changed, Aubins idle bar won't blink at all anymore (except you change
# the background below it)
#
# Revision 1.28  2003/03/02 21:48:34  dischi
# Support for skin changing in the main menu
#
# Revision 1.27  2003/03/02 19:31:35  dischi
# split the draw function in two parts
#
# Revision 1.26  2003/03/02 15:18:48  dischi
# Don't redraw if a child is visble
#
# Revision 1.25  2003/03/02 15:04:08  dischi
# Added forced_redraw after Clear()
#
# Revision 1.24  2003/03/02 14:35:11  dischi
# Added clear function
#
# Revision 1.23  2003/03/02 11:46:32  dischi
# Added GetPopupBoxStyle to return popup box styles to the gui
#
# Revision 1.22  2003/02/27 22:39:50  dischi
# The view area is working, still no extended menu/info area. The
# blue_round1 skin looks like with the old skin, blue_round2 is the
# beginning of recreating aubin_round1. tv and music player aren't
# implemented yet.
#
# Revision 1.21  2003/02/26 21:21:11  dischi
# blue_round1.xml working
#
# Revision 1.20  2003/02/26 19:59:26  dischi
# title area in area visible=(yes|no) is working
#
# Revision 1.19  2003/02/25 22:56:00  dischi
# New version of the new skin. It still looks the same (except that icons
# are working now), but the internal structure has changed. Now it will
# be easier to do the next steps.
#
# Revision 1.18  2003/02/23 18:42:20  dischi
# Current status of my skin redesign. Currently only the background and
# the listing area is working, the listing without icons. Let me know what
# you thing before I spend more time with it
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
import pygame

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
sys.path.append('skins/dischi1')

import xml_skin

# Create the OSD object
osd = osd.get_singleton()

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


# Set up the mixer
mixer = mixer.get_singleton()

# Create the remote control object
rc = rc.get_singleton()




from area import Skin_Area
from area import Screen

from listing_area import Listing_Area
from tvlisting_area import TVListing_Area
from view_area import View_Area
from info_area import Info_Area



class Screen_Area(Skin_Area):
    """
    this area is the screen or background of the skin
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'screen', screen)

    def update_content_needed(self):
        """
        this area needs never a content update
        """
        return FALSE

    def update_content(self):
        """
        there is no content in this area
        """
        pass



class Title_Area(Skin_Area):
    """
    in this area the title of the menu is drawn
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'title', screen)
        self.text = ''

        
    def update_content_needed(self):
        """
        check if the content needs an update
        """
        menu      = self.menu
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        if content.type == 'menu':
            text = menu.heading
        elif len(menu.choices) == 0:
            text = ''
        elif content.type == 'short item':
            if menu.selected.type == 'video' and menu.selected.tv_show:
                sn = menu.selected.show_name
                text = sn[1] + "x" + sn[2] + " - " + sn[3] 
            else:
                text = menu.selected.name
        else:
            text = menu.selected.name

        return self.text != text


    def update_content(self):
        """
        update the content
        """
        menu      = self.menu
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        if content.type == 'menu':
            text = menu.heading
        elif len(menu.choices) == 0:
            text = ''
        elif content.type == 'short item':
            if menu.selected.type == 'video' and menu.selected.tv_show:
                sn = menu.selected.show_name
                text = sn[1] + "x" + sn[2] + " - " + sn[3] 
            else:
                text = menu.selected.name
        else:
            text = menu.selected.name

        self.text = text
        self.write_text(text, content.font, content, mode='hard')


class Subtitle_Area(Title_Area):
    """
    in this area the subtitle of the menu is drawn
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'subtitle', screen)
        self.text = ''


###############################################################################


###############################################################################
# Skin main functions
###############################################################################

class Skin:
    """
    main skin class
    """
    
    def __init__(self):
        self.display_style = config.SKIN_START_LAYOUT
        self.force_redraw = TRUE
        self.last_draw = None
        self.screen = Screen()
        self.area_names = ( 'screen', 'title', 'subtitle', 'listing', 'view', 'info')
        for a in self.area_names:
            setattr(self, '%s_area' % a, eval('%s%s_Area(self, self.screen)' % \
                                              (a[0].upper(), a[1:])))

        self.tvlisting = TVListing_Area(self, self.screen)
        
        if DEBUG: print 'Skin: Loading XML file %s' % config.SKIN_XML_FILE
    
        self.settings = xml_skin.XMLSkin()
        
        # try to find the skin xml file
        if not self.settings.load(config.SKIN_XML_FILE):
            print "skin not found, using fallback skin"
            self.settings.load("skins/xml/type1/blue1_big.fxd")
        
        for dir in config.cfgfilepath:
            local_skin = '%s/local_skin.fxd' % dir
            if os.path.isfile(local_skin):
                if DEBUG: print 'Skin: Add local config %s to skin' % local_skin
                self.settings.load(local_skin)
                break
        

    
    def LoadSettings(self, dir, copy_content = 1):
        """
        return an object with new skin settings
        """
        if copy_content:
            settings = copy.copy(self.settings)
        else:
            settings = xml_skin.XMLSkin()
            
        if dir and os.path.isfile(os.path.join(dir, 'folder.fxd')):
            settings.load(os.path.join(dir, 'folder.fxd'), copy_content, clear=TRUE)
            return settings

        elif dir and os.path.isfile(dir):
            settings.load(dir, copy_content, clear=TRUE)
            return settings
        return None



    def GetSkins(self):
        """
        return a list of all possible skins with name, image and filename
        """
        ret = []
        skin_files = util.match_files('skins/xml/type1', ['fxd'])
        for d in util.getdirnames('skins/xml'):
            skin = os.path.join(d, os.path.basename(d)+'.fxd')
            if os.path.isfile(skin):
                skin_files += [ skin ]

        # image is not usable stand alone
        skin_files.remove('skins/xml/type1/image.fxd')
        
        for skin in skin_files:
            name  = os.path.splitext(os.path.basename(skin))[0]
            if os.path.isfile('%s.png' % os.path.splitext(skin)[0]):
                image = '%s.png' % os.path.splitext(skin)[0]
            else:
                image = None
            ret += [ ( name, image, skin ) ]
        return ret
    
        
    def ToggleDisplayStyle(self, menu):
        """
        Toggle display style
        """
        if menu.force_skin_layout != -1:
            return 0
        
        if menu and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        # get the correct <menu>
        if settings.menu.has_key(menu.item_types):
            area = settings.menu[menu.item_types]
        else:
            area = settings.menu['default']

        if self.display_style >=  len(area.style):
            self.display_style = 0
        self.display_style = (self.display_style + 1) % len(area.style)
        return 1


    def GetDisplayStyle(self, menu=None):
        """
        return current display style
        """
        if menu and menu.force_skin_layout != -1:
            return menu.force_skin_layout
        return self.display_style


    def FindCurrentMenu(self, widget):
        if not widget:
            return None
        if not hasattr(widget, 'menustack'):
            return self.FindCurrentMenu(widget.parent)
        return widget.menustack[-1]
        
    def GetPopupBoxStyle(self, widget=None):
        """
        This function returns style information for drawing a popup box.

        return backround, spacing, color, font, button_default, button_selected
        background is ('image', XML_image) or ('rectangle', XML_rectangle)

        XML_image attributes: filename
        XML_rectangle attributes: color (of the border), size (of the border),
           bgcolor (fill color), radius (round box for the border). There are also
           x, y, width and height as attributes, but they may not be needed for the
           popup box

        button_default, button_selected are XML_item
        attributes: font, rectangle (XML_rectangle)

        All fonts are XML_font objects
        attributes: name, size, color, shadow
        shadow attributes: visible, color, x, y
        """

        menu = self.FindCurrentMenu(widget)

        if menu and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        layout = settings.popup

        background = None

        for bg in layout.background:
            if isinstance(bg, xml_skin.XML_image):
                background = ( 'image', bg)
            elif isinstance(bg, xml_skin.XML_rectangle):
                background = ( 'rectangle', bg)

        button_default  = None
        button_selected = None

        spacing = layout.content.spacing
        color   = layout.content.color

        if layout.content.types.has_key('default'):
            button_default = layout.content.types['default']

        if layout.content.types.has_key('selected'):
            button_selected = layout.content.types['selected']

        return (background, spacing, color, layout.content.font,
                button_default, button_selected)

        
    def SubMenuVisible(self, menu):
        """
        deprecated
        """
        return 0


    def PopupBox(self, text=None, icon=None):
        """
        deprecated
        """
        pass
        

    def DrawMenu(self, menuw):
        """
        deprecated, dummy for now
        """
        self.draw(('menu', menuw))

    def DrawMP3(self, info):
        """
        deprecated, dummy for now
        """
        self.draw(('player', info))

    def DrawTVGuide(self, menuw):
        """
        deprecated, dummy for now
        """
        self.draw(('tv', menuw))
    
    def DrawTVGuide_ItemsPerPage(self, tv):
        """
        deprecated, dummy for now
        """
        return self.items_per_page(('tv', tv))


    def ItemsPerMenuPage(self, menu):
        """
        deprecated, dummy for now
        """
        return self.items_per_page(('menu', menu))


    def items_per_page(self, (type, object)):
        """
        returns the number of items per menu page
        (cols, rows) for normal menu and
        rows         for the tv menu
        """
        if not object:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return
        
        if type == 'tv':
            return self.tvlisting.get_items_geometry(self.settings, object)[4]

        if object.skin_settings:
            settings = object.skin_settings
        else:
            settings = self.settings

        # hack for the main menu to fit all in one screen
        if not object.packrows:
            object.item_types = 'main'

        rows, cols = self.listing_area.get_items_geometry(settings, object,
                                                          self.display_style)[:2]
        return (cols, rows)



    def Clear(self):
        """
        clean the screen
        """
        self.force_redraw = TRUE
        osd.clearscreen(osd.COL_BLACK)
        osd.update()


    def draw(self, (type, object)):
        """
        draw the object.
        object may be a menu widget, a table for the tv menu are an audio item for
        the audio player
        """

        if type == 'menu':
            menuw = object
            
            if not menuw.visible:
                return

            draw_allowed = TRUE
            for child in menuw.children:
                draw_allowed = draw_allowed and not child.visible

            if not draw_allowed:
                self.force_redraw = TRUE
                return

            menu = menuw.menustack[-1]

            if not menu:
                osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
                return

            if menu.skin_settings:
                settings = menu.skin_settings
            else:
                settings = self.settings

            # FIXME
            if len(menuw.menustack) == 1:
                menu.item_types = 'main'


        else:
            settings = self.settings

        if type == 'tv':
            l = self.listing_area
            self.listing_area = self.tvlisting

        if self.last_draw != type:
            self.force_redraw = TRUE
            self.last_draw = type

        self.screen.clear()

        for a in self.area_names:
            area = eval('self.%s_area' % a)
            area.draw(settings, object, self.display_style, self.last_draw,
                      self.force_redraw)

        self.screen.show(self.force_redraw)

        if type == 'tv':
            self.listing_area = l

        osd.update()
        self.force_redraw = FALSE


            
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
            except ValueError:
    	        mytrack = None
        else:
           mytrack = None
    
        song_info = {  'a'  : array.artist,
       	               'l'  : array.album,
    	               'n'  : mytrack,
    	               't'  : array.title,
    	               'y'  : array.year }
   
        return formatstr % song_info
