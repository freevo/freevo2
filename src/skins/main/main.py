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
# Revision 1.26  2003/12/06 13:43:02  dischi
# more cleanup
#
# Revision 1.25  2003/12/05 18:07:55  dischi
# renaming of XML_xxx variables to Xxx
#
# Revision 1.24  2003/12/05 17:30:18  dischi
# some cleanup
#
# Revision 1.23  2003/12/04 21:49:18  dischi
# o remove BlankScreen and the Splashscreen
# o make it possible to register objects as areas
#
# Revision 1.22  2003/12/03 21:50:44  dischi
# rework of the loading/selecting
# o all objects that need a skin need to register what they areas they need
# o remove all 'player' and 'tv' stuff to make it more generic
# o renamed some skin function names
#
# Revision 1.21  2003/11/29 11:27:41  dischi
# move objectcache to util
#
# Revision 1.20  2003/11/28 20:08:58  dischi
# renamed some config variables
#
# Revision 1.19  2003/11/22 20:34:23  dischi
# use new vfs
#
# Revision 1.18  2003/11/22 12:02:11  dischi
# make the skin blankscreen a real plugin area
#
# Revision 1.17  2003/10/31 17:00:20  dischi
# splashscreen for bsd
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


import os, copy
import stat

import config
import util
import osd

from area import Skin_Area
from gui  import GUIObject

import xml_skin
import screen

# Create the OSD object
osd = osd.get_singleton()


###############################################################################
# Skin main functions
###############################################################################


class Skin:
    """
    main skin class
    """
    
    Rectange = xml_skin.Rectangle
    Image    = xml_skin.Image
    Area     = Skin_Area

    
    def __init__(self):
        """
        init the skin engine
        """
        global skin_engine
        skin_engine = self
        
        self.display_style = { 'menu' : config.SKIN_START_LAYOUT }
        self.force_redraw  = True
        self.last_draw     = None, None, None
        self.screen        = screen.get_singleton()
        self.xml_cache     = util.objectcache.ObjectCache(3, desc='xmlskin')
        self.areas         = {}

        # load default areas
        from listing_area   import Listing_Area
        from tvlisting_area import TVListing_Area
        from view_area      import View_Area
        from info_area      import Info_Area
        from default_areas  import Screen_Area, Title_Area, Subtitle_Area, Plugin_Area
        
        for a in ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info', 'plugin'):
            self.areas[a] = eval('%s_Area()' % a.capitalize())
        self.areas['tvlisting'] = TVListing_Area()

        # load the fxd file
        self.settings = xml_skin.XMLSkin()
        
        # try to find the skin xml file
        if not self.settings.load(config.SKIN_XML_FILE):
            print "skin not found, using fallback skin"
            self.settings.load('blue.fxd')
        
        for dir in config.cfgfilepath:
            local_skin = '%s/local_skin.fxd' % dir
            if os.path.isfile(local_skin):
                _debug_('Skin: Add local config %s to skin' % local_skin,2)
                self.settings.load(local_skin)
                break


    def register(self, type, areas):
        """
        register a new type objects to the skin
        """
        setattr(self, '%s_areas' % type, [])
        for a in areas:
            if isinstance(a, str):
                getattr(self, '%s_areas' % type).append(self.areas[a])
            else:
                getattr(self, '%s_areas' % type).append(a)


    def delete(self, type):
        """
        delete informations about a special skin type
        """
        exec('del self.%s_areas' % type)

        
    def load(self, dir, copy_content = 1):
        """
        return an object with new skin settings
        """
        if dir and vfs.isfile(vfs.join(dir, 'folder.fxd')):
            file = vfs.join(dir, 'folder.fxd')

        elif dir and vfs.isfile(dir):
            file = dir
        else:
            return None

        if copy_content:
            cname = '%s%s%s' % (str(self.settings), file, vfs.stat(file)[stat.ST_MTIME])
            settings = self.xml_cache[cname]
            if not settings:
                settings = copy.copy(self.settings)
                if not settings.load(file, copy_content, clear=True):
                    return None
                self.xml_cache[cname] = settings
        else:
            cname = '%s%s' % (file, vfs.stat(file)[stat.ST_MTIME])
            settings = self.xml_cache[cname]
            if not settings:
                settings = xml_skin.XMLSkin()
                if not settings.load(file, copy_content, clear=True):
                    return None
                self.xml_cache[cname] = settings

        return settings
    


    def get_skins(self):
        """
        return a list of all possible skins with name, image and filename
        """
        ret = []
        skin_files = util.match_files(os.path.join(config.SKIN_DIR, 'main'), ['fxd'])

        # image is not usable stand alone
        skin_files.remove(os.path.join(config.SKIN_DIR, 'main/image.fxd'))
        
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
    
        
    def toggle_display_style(self, menu):
        """
        Toggle display style
        """
        if isinstance(menu, str):
            if not self.display_style.has_key(menu):
                self.display_style[menu] = 0
            self.display_style[menu] = (self.display_style[menu] + 1) % \
                                       len(self.settings.sets[menu].style)
            return 1
            
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

        if self.display_style['menu'] >=  len(area.style):
            self.display_style['menu'] = 0
        self.display_style['menu'] = (self.display_style['menu'] + 1) % len(area.style)
        return 1


    def get_display_style(self, menu=None):
        """
        return current display style
        """
        if isinstance(menu, str):
            if not self.display_style.has_key(menu):
                self.display_style[menu] = 0
            return self.display_style[menu]
        
        if menu:            
            if menu.force_skin_layout != -1:
                return menu.force_skin_layout
        return self.display_style['menu']


    def __find_current_menu__(self, widget):
        if not widget:
            return None
        if not hasattr(widget, 'menustack'):
            return self.__find_current_menu__(widget.parent)
        return widget.menustack[-1]
        

    def get_popupbox_style(self, widget=None):
        """
        This function returns style information for drawing a popup box.

        return backround, spacing, color, font, button_default, button_selected
        background is ('image', Image) or ('rectangle', Rectangle)

        Image attributes: filename
        Rectangle attributes: color (of the border), size (of the border),
           bgcolor (fill color), radius (round box for the border). There are also
           x, y, width and height as attributes, but they may not be needed for the
           popup box

        button_default, button_selected are XML_item
        attributes: font, rectangle (Rectangle)

        All fonts are Font objects
        attributes: name, size, color, shadow
        shadow attributes: visible, color, x, y
        """

        menu = self.__find_current_menu__(widget)

        if menu and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = self.settings

        layout = settings.popup

        background = None

        for bg in layout.background:
            if isinstance(bg, xml_skin.Image):
                background = ( 'image', bg)
            elif isinstance(bg, xml_skin.Rectangle):
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

        

    def get_font(self, name):
        """
        Get the skin font object 'name'. Return the default object if
        a font with this name doesn't exists.
        """
        try:
            return self.settings.font[name]
        except:
            return self.settings.font['default']

        
    def items_per_page(self, (type, object)):
        """
        returns the number of items per menu page
        (cols, rows) for normal menu and
        rows         for the tv menu
        """
        if type == 'tv':
            info = self.areas['tvlisting']
            info = info.get_items_geometry(self.settings, object,
                                           self.get_display_style('tv'))
            return (info[4], info[-1])

        if object.skin_settings:
            settings = object.skin_settings
        else:
            settings = self.settings

        menu = None
        if type == 'menu':
            menu = object

        info = self.areas['listing']
        rows, cols = info.get_items_geometry(settings, object,
                                             self.get_display_style( menu ))[:2]
        return (cols, rows)



    def clear(self, osd_update=True):
        """
        clean the screen
        """
        _debug_('clear: %s' % osd_update, 2)
        self.force_redraw = True
        osd.clearscreen(osd.COL_BLACK)
        if osd_update:
            osd.update()


    def redraw(self):
        """
        redraw the current screen
        """
        _debug_('redraw', 2)
        if self.last_draw[0] and self.last_draw[1]:
            self.draw(self.last_draw[0], self.last_draw[1], self.last_draw[2])


    def prepare(self):
        """
        prepare the skin
        """
        self.settings.prepare()

        
    def draw(self, type, object, menu=None):
        """
        draw the object.
        object may be a menu widget, a table for the tv menu are an audio item for
        the audio player
        """
        if isinstance(object, GUIObject):
            # handling for gui objects: are they visible? what about children?
            if not object.visible:
                return

            draw_allowed = True
            for child in object.children:
                draw_allowed = draw_allowed and not child.visible

            if not draw_allowed:
                self.force_redraw = True
                return

        settings = self.settings
            
        if type == 'menu':
            menu = object.menustack[-1]
            if menu.skin_settings:
                settings = menu.skin_settings
            # XXX FIXME
            if len(object.menustack) == 1:
                menu.item_types = 'main'
            style = self.get_display_style(menu)

        else:
            try:
                if not object.visible:
                    return
            except AttributeError:
                pass
            style = self.get_display_style(type)


        if self.last_draw[0] != type:
            self.force_redraw = True
            self.all_areas    = getattr(self, '%s_areas' % type)
            
        self.last_draw = type, object, menu

        self.screen.clear()
        for a in self.all_areas:
            a.draw(settings, object, menu, style, type, self.force_redraw)
        self.screen.show(self.force_redraw)

        osd.update()
        self.force_redraw = False
