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
# Skin_Screen   (this file)
# Skin_Title    (this file)
# Skin_View     (not implemented yet)
# Skin_Listing  (listing.py)
# Skin_Info     (not implemented yet)

from area import Skin_Area
from listing import Skin_Listing

class Skin_Screen(Skin_Area):
    def __init__(self, parent):
        Skin_Area.__init__(self, 'screen')

    def update_content_needed(self, settings, menuw):
        return FALSE

    def update_content(self, settings, menuw):
        pass


class Skin_Title(Skin_Area):
    def __init__(self, parent):
        Skin_Area.__init__(self, 'title')
        self.depends = ( parent.screen_area, )
        self.text = ''

        
    def update_content_needed(self, settings, menuw):
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

        self.write_text(text, settings.font[content.font], content, height=-1,
                        mode='hard')

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
        
    hold = 0

    def __init__(self):
        self.area_names = ( 'screen', 'title', 'listing')
        for a in self.area_names:
            setattr(self, '%s_area' % a, eval('Skin_%s%s(self)' % (a[0].upper(), a[1:])))


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
        

    # Called from the MenuWidget class to draw a menu page on the
    # screen
    def DrawMenu(self, menuw):
        if self.hold:
            print 'skin.drawmenu() hold!'
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
            
        for a in self.area_names:
            area = eval('self.%s_area' % a)
            area.draw(settings, menuw)

        osd.update()
        

    def DrawMP3(self, info):
        osd.update()

