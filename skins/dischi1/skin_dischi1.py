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




#
# We have five areas, all inherit from Skin_Area (file area.py)
#
# Screen_Area   (this file)
# Title_Area    (this file)
# View_Area     (view_area.py)
# Listing_Area  (listing_area.py)
# Info_Area     (not implemented yet)

from area import Skin_Area
from area import Screen

from listing_area import Listing_Area
from view_area import View_Area


class Screen_Area(Skin_Area):
    """
    this area is the screen or background of the skin
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'screen', screen)

    def update_content_needed(self, settings, menuw):
        """
        this area needs never a content update
        """
        return FALSE

    def update_content(self, settings, menuw):
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

        
    def update_content_needed(self, settings, menuw):
        """
        check if the content needs an update
        """
        menu = menuw.menustack[-1]

        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        if content.type == 'menu':
            text = menu.heading
        else:
            text = menu.selected.name

        return self.text != text


    def update_content(self, settings, menuw):
        """
        update the content
        """
        menu = menuw.menustack[-1]

        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        if content.type == 'menu':
            text = menu.heading
        else:
            text = menu.selected.name

        self.text = text

        if not settings.font.has_key(content.font):
            print '*** font <%s> not found' % content.font
            return

        self.write_text(text, settings.font[content.font], content, mode='hard')



###############################################################################


###############################################################################
# Skin main functions
###############################################################################

XML_SKIN_DIRECTORY = 'skins/dischi1'

class Skin:

    if DEBUG: print 'Skin: Loading XML file %s' % config.SKIN_XML_FILE
    
    settings = xml_skin.XMLSkin()

    # try to find the skin xml file
    
    if not settings.load(config.SKIN_XML_FILE):
        print "skin not found, using fallback skin"
        settings.load("%s/blue1_big.xml" % XML_SKIN_DIRECTORY)
        
    for dir in config.cfgfilepath:
        local_skin = '%s/local_skin.xml' % dir
        if os.path.isfile(local_skin):
            if DEBUG: print 'Skin: Add local config %s to skin' % local_skin
            settings.load(local_skin)
            break
        
    def __init__(self):
        self.force_redraw = TRUE
        self.screen = Screen()
        self.area_names = ( 'screen', 'title', 'listing', 'view')
        for a in self.area_names:
            setattr(self, '%s_area' % a, eval('%s%s_Area(self, self.screen)' % \
                                              (a[0].upper(), a[1:])))


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
        return FALSE

    def GetDisplayStyle(self):
        return 0

    def GetPopupBoxStyle(self, menu=None):
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

        if menu and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        if not settings.layout.has_key(settings.popup):
            print '*** layout <%s> not found' % settings.popup
            return None

        layout = settings.layout[settings.popup]

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

        if not settings.font.has_key(layout.content.font):
            print '*** font <%s> not found' % layout.content.font
            font = None
        else:
            font = settings.font[layout.content.font]
                
        if layout.content.types.has_key('default'):
            button_default = copy.copy(layout.content.types['default'])

            if not settings.font.has_key(button_default.font):
                print '*** font <%s> not found' % button_default.font
                button_default.font = None
            else:
                button_default.font = settings.font[button_default.font]

            
        if layout.content.types.has_key('selected'):
            button_selected = copy.copy(layout.content.types['selected'])

            if not settings.font.has_key(button_selected.font):
                print '*** font <%s> not found' % button_selected.font
                button_selected.font = None
            else:
                button_selected.font = settings.font[button_selected.font]

        return (background, spacing, color, font, button_default, button_selected)

        
    def ItemsPerMenuPage(self, menu):

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return (0,0)

        if menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        # hack for the main menu to fit all in one screen
        if not menu.packrows:
            menu.item_types = 'main'

        rows, cols = self.listing_area.get_items_geometry(settings, menu)[:2]
        return (cols, rows)
        


    def SubMenuVisible(self, menu):
        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return TRUE

        return 0


    def PopupBox(self, text=None, icon=None):
        """
        text  String to display

        Draw a popupbox with an optional icon and a text.
        
        Notes: Should maybe be named print_message or show_message.
               Maybe I should use one common box item.
        """
        pass
        

    def Clear(self):
        self.force_redraw = TRUE
        osd.clearscreen(osd.COL_BLACK)
        osd.update()

    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        if not menuw.visible:
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
            
        self.screen.clear()
        for a in self.area_names:
            area = eval('self.%s_area' % a)
            area.draw(settings, menuw, self.force_redraw)

        osd.update()
        self.force_redraw = FALSE
        

    def DrawMP3(self, info):
        osd.update()

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
