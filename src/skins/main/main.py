#if 0
# -----------------------------------------------------------------------
# skin_main1.py - Freevo default skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/08/05 18:59:22  dischi
# Directory cleanup, part 1:
# move skins/main1/* to src/skins/main
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

import sys, os, copy

# Various utilities
import util

# The OSD class, used to communicate with the OSD daemon
import osd

import stat
import objectcache

# XML parser for skin informations
sys.path.append('skins/main1')

import xml_skin

# Create the OSD object
osd = osd.get_singleton()

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


from area import Skin_Area, Screen

from listing_area import Listing_Area
from tvlisting_area import TVListing_Area
from view_area import View_Area
from info_area import Info_Area

import plugin


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
        check if the content needs an update. This function does the same as
        update_content, so it's faster to return always 1
        """
        return 1

    def update_content(self):
        """
        update the content
        """
        menu      = self.menu
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=TRUE)

        text = ''
        try:
            if content.type == 'menu':
                text = menu.heading
            elif len(menu.choices) == 0:
                text = ''
            elif content.type == 'short item':
                if menu.selected.image and menu.selected.type == 'video' and \
                   hasattr(menu.selected, 'tv_show') and menu.selected.tv_show:
                    sn = menu.selected.show_name
                    text = sn[1] + "x" + sn[2] + " - " + sn[3] 
                else:
                    text = menu.selected.name
            else:
                text = menu.selected.name
        except AttributeError:
            try:
                if menu.type == 'tv':
                    if content.type == 'item' or content.type == 'short item':
                        text = menu.table[1].title
                    else:
                        text = 'TV GUIDE'
            except:
                pass
            
        self.text = text
        self.write_text(text, content.font, content, height=-1, mode='hard')


class Subtitle_Area(Title_Area):
    """
    in this area the subtitle of the menu is drawn
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'subtitle', screen)
        self.text = ''


class Plugin_Area(Skin_Area):
    """
    in this area all plugins can draw
    """
    def __init__(self, parent, screen):
        Skin_Area.__init__(self, 'plugin', screen)
        self.plugins = None
        self.x = config.OVERSCAN_X
        self.y = config.OVERSCAN_Y
        self.width   = osd.width  - 2 * config.OVERSCAN_X
        self.height  = osd.height - 2 * config.OVERSCAN_Y
        
    def get_font(self, name):
        try:
            return self.xml_settings.font[name]
        except:
            return self.xml_settings.font['default']
    
    def update_content_needed(self):
        """
        this area needs never a content update
        """
        return TRUE

    def update_content(self):
        """
        there is no content in this area
        """
        if self.plugins == None:
            self.plugins = plugin.get('daemon_draw')

        if self.widget_type == 'player':
            object = self.infoitem
        else:
            object = self.menuw
            
        for p in self.plugins:
            p.draw((self.widget_type, object), self)



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
        self.last_draw = None, None
        self.screen = Screen()
        self.xml_cache = objectcache.ObjectCache(3, desc='xmlskin')

        self.normal_areas = []
        self.tv_areas = []

        for a in ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info', 'plugin'):
            o = eval('%s%s_Area(self, self.screen)' % (a[0].upper(), a[1:]))
            self.normal_areas.append(o)
            if a == 'listing':
                self.listing_area = o
                o = TVListing_Area(self, self.screen)
                self.tvlisting = o
            self.tv_areas.append(o)
        
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
        if dir and os.path.isfile(os.path.join(dir, 'folder.fxd')):
            file = os.path.join(dir, 'folder.fxd')

        elif dir and os.path.isfile(dir):
            file = dir
        else:
            return None

        if copy_content:
            cname = '%s%s%s' % (str(self.settings), file, os.stat(file)[stat.ST_MTIME])
            settings = self.xml_cache[cname]
            if not settings:
                settings = copy.copy(self.settings)
                if not settings.load(file, copy_content, clear=TRUE):
                    return None
                self.xml_cache[cname] = settings
        else:
            cname = '%s%s' % (file, os.stat(file)[stat.ST_MTIME])
            settings = self.xml_cache[cname]
            if not settings:
                settings = xml_skin.XMLSkin()
                if not settings.load(file, copy_content, clear=TRUE):
                    return None
                self.xml_cache[cname] = settings

        return settings
    


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
            elif os.path.isfile('%s.jpg' % os.path.splitext(skin)[0]):
                image = '%s.jpg' % os.path.splitext(skin)[0]
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
        if menu:            
            if menu.force_skin_layout != -1:
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

        menu = None
        if type == 'menu':
            menu = object

        rows, cols = self.listing_area.get_items_geometry(settings, object,
                                                          self.GetDisplayStyle( menu ))[:2]
        return (cols, rows)



    def clear(self):
        """
        clean the screen
        """
        self.force_redraw = TRUE
        osd.clearscreen(osd.COL_BLACK)
        osd.update()


    def redraw(self):
        """
        redraw the current screen
        """
        if self.last_draw[0] and self.last_draw[1]:
            self.draw(self.last_draw)

            
    def draw(self, (type, object)):
        """
        draw the object.
        object may be a menu widget, a table for the tv menu are an audio item for
        the audio player
        """

        if not self.settings.prepared:
            self.settings.prepare()
            
        menu = None
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
            if not object.visible:
                return
            all_areas = self.tv_areas
            style = 0
        elif type == 'player':
            all_areas = self.normal_areas
            style = 0
        else:
            all_areas = self.normal_areas
            style = self.GetDisplayStyle(menu)

        if self.last_draw[0] != type:
            self.force_redraw = TRUE
        self.last_draw = type, object

        self.screen.clear()

        for a in all_areas:
            a.draw(settings, object, style, type, self.force_redraw)
            
        self.screen.show(self.force_redraw)

        osd.update()
        self.force_redraw = FALSE
