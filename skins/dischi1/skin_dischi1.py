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


PADDING=5   # Padding/spacing between items

###############################################################################

# Set up the mixer
mixer = mixer.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

###############################################################################



# Draws a text inside a frame based on the settings in the XML file
def write_text(text, font, area, x=-1, y=-1, width=None, height=None,
               mode='hard', ellipses='...'):
    
    if x == -1: x = area.x
    if y == -1: y = area.y

    if width == None:
        width  = area.width
    if height == None:
        height = area.height

    if font.shadow.visible:
        osd.drawstringframed(text, x+font.shadow.x, y+font.shadow.y,
                             width, height, font.shadow.color, None,
                             font=font.name, ptsize=font.size,
                             mode=mode, ellipses=ellipses)
    osd.drawstringframed(text, x, y, width, height, font.color, None,
                         font=font.name, ptsize=font.size,
                         mode=mode, ellipses=ellipses)




###############################################################################

class Skin_Area:
    def __init__(self, name):
        self.area_name = name
        self.alpha     = None           # alpha layer for rectangles
        self.screen    = None           # backup of the final screen
        self.area_val  = None
        self.redraw    = TRUE

    def calc_geometry(self, object, copy_object=0, fit_area=1):
        if copy_object:
            object = copy.deepcopy(object)
            
        try:
            if object.width[:3] == 'max':
                object.width = self.area_val.width + int(object.width[3:])
        except TypeError:
            pass
        
        try:
            if object.height[:3] == 'max':
                object.height = self.area_val.height + int(object.height[3:])
        except TypeError:
            pass

        if fit_area:
            object.x += self.area_val.x
            object.y += self.area_val.y

        if not object.width:
            object.width = self.area_val.width

        if not object.height:
            object.height = self.area_val.height

        return object

        
    def init_vars(self, settings, display_type):
        dep_redraw = self.redraw
        
        if settings.menu.has_key(display_type):
            area_val = settings.menu[display_type][0]
        else:
            area_val = settings.menu['default'][0]

        area_val = eval('area_val.%s' % self.area_name)
        
        if (not self.area_val) or area_val != self.area_val:
            self.area_val = area_val
            self.redraw = TRUE
            
        if not settings.layout.has_key(area_val.layout):
            print '*** layout <%s> not found' % area_val.layout
            return 0

        if not self.redraw:
            return
        
        self.layout = settings.layout[area_val.layout]

        # we need to redraw the area we want to draw in
        if not dep_redraw and self.redraw and hasattr(self, 'bg'):
            osd.screen.blit(self.bg[0][0], self.bg[0][1:])


    def draw_background(self):
        if not self.redraw:
            return

        area = self.area_val

        if hasattr(self, 'bg') and hasattr(self, 'depends'):
            self.bg = [ [ None, area.x, area.y ], None ]
            self.bg[0][0] = osd.createlayer(area.width, area.height)
            self.bg[0][0].blit(osd.screen, (0,0), (area.x, area.y,
                                                   area.x + area.width,
                                                   area.y + area.height))
                
        self.alpha = None
        for bg in copy.deepcopy(self.layout.background):
            if isinstance(bg, xml_skin.XML_image):
                self.calc_geometry(bg)
                image = osd.loadbitmap(bg.filename)
                osd.screen.blit(image, (bg.x, bg.y))
            elif isinstance(bg, xml_skin.XML_rectangle):
                self.calc_geometry(bg, fit_area=FALSE)
                if not self.alpha:
                    self.alpha = osd.createlayer(area.width, area.height)
                    # clear surface
                    self.alpha.fill((0,0,0,0))
                osd.drawroundbox(bg.x, bg.y, bg.x+bg.width, bg.y+bg.height, bg.bgcolor,
                                 bg.size, bg.color, bg.radius, layer=self.alpha)

        if self.alpha:
            osd.screen.blit(self.alpha, (area.x, area.y))

        if hasattr(self, 'bg'):
            self.bg[1] = osd.createlayer(area.width, area.height)
            self.bg[1].blit(osd.screen, (0,0), (area.x, area.y,
                                                area.x + area.width,
                                                area.y + area.height))



    def drawroundbox(self, x, y, width, height, rect):
        area = self.area_val
        if self.alpha:
            osd.screen.blit(self.bg[0][0], (x, y), (x-area.x, y-area.y, width, height))
            a = osd.createlayer(width, height)
            a.blit(self.alpha, (0,0), (x - area.x, y - area.y, width, height))

            osd.drawroundbox(0, 0, width, height,
                             color = rect.bgcolor, border_size=rect.size,
                             border_color=rect.color, radius=rect.radius, layer=a)
            osd.screen.blit(a, (x, y))
        else:
            osd.drawroundbox(x, y, x+width, y+height,
                             color = rect.bgcolor, border_size=rect.size,
                             border_color=rect.color, radius=rect.radius)

        
    
###############################################################################
        
class Skin_Screen(Skin_Area):
    def __init__(self, parent):
        Skin_Area.__init__(self, 'screen')

    def __call__(self, settings, menuw):
        menu = menuw.menustack[-1]

        self.redraw = FALSE
        self.init_vars(settings, menu.item_types)
        self.draw_background()

###############################################################################


class Skin_Listing(Skin_Area):
    def __init__(self, parent):
        Skin_Area.__init__(self, 'listing')
        self.bg = [ None, None ]
        self.last_choices = ( None, None )
        self.depends = ( parent.screen_area, )
        
    def __call__(self, settings, menuw):
        menu = menuw.menustack[-1]

        self.redraw = FALSE
        for d in self.depends:
            self.redraw = d.redraw or self.redraw

        self.init_vars(settings, menu.item_types)

        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)
        selection = content.selection

        self.draw_background()
        menu_redraw = self.redraw
        
        if not settings.font.has_key(content.font):
            print '*** font <%s> not found' % content.font
            return 0

        font1 = settings.font[content.font]

        if not settings.font.has_key(selection.font):
            print '*** font <%s> not found' % selection.font
            font2 = font1
        else:
            font2 = settings.font[selection.font]

        if not self.redraw:
            self.redraw = self.last_choices[0] != menu.selected
            
        if not self.redraw:
            i = 0
            for choice in menuw.menu_items:
                if self.last_choices[1][i] != choice:
                    self.redraw = TRUE
                    break
                i += 1
                
        if not self.redraw:
            return

        if not menu_redraw:
            osd.screen.blit(self.bg[1], (area.x, area.y))

        x0 = content.x + selection.spacing
        y0 = content.y + selection.spacing

        width  = content.width - 2* selection.spacing

        for choice in menuw.menu_items:
            font = font1
            if choice == menu.selected:
                font = font2


            text = choice.name
            if not text:
                print "no text to display ... strange. Use default"
                text = "unknown"

            if choice.type == 'playlist':
                text = 'PL: %s' % text

            font_w, font_h = osd.stringsize(text, font=font.name, ptsize=font.size)
            spacing = font_h + content.spacing     
        
            if choice == menu.selected and selection.visible:
                self.drawroundbox(x0 - selection.spacing,
                                  y0 - selection.spacing,
                                  2*selection.spacing + width,
                                  2*selection.spacing + font_h,
                                  selection)
                                  
                    
            write_text(text, font, area, x=x0, y=y0, width=width,
                       height=-1, mode='hard')

            y0 += spacing

        self.last_choices = (menu.selected, copy.copy(menuw.menu_items))


        
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
        self.area_names = ( 'screen', 'listing')
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

        # hack for the main menu to fit all in one screen
        if not menu.packrows:
            return (5,1)
        
        return (5, 1)
        


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
            area(settings, menuw)

        osd.update()
        

    def DrawMP3(self, info):
        osd.update()

