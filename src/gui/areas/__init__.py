# -*- coding: iso-8859-1 -*-
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
# Revision 1.3  2004/07/24 12:21:30  dischi
# use new renderer and screen features
#
# Revision 1.2  2004/07/23 19:43:31  dischi
# move most of the settings code out of the skin engine
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
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


import os
import traceback

import config
import util

from area import Skin_Area

# Bad: import back in directory tree
from gui import fxdparser as fxdparser

class AreaHandler:
    """
    main skin class
    """
    
    Rectange = fxdparser.Rectangle
    Image    = fxdparser.Image
    Area     = Skin_Area

    def __init__(self, settings):
        """
        init the skin engine
        """
        self.settings      = settings
        self.display_style = { 'menu' : 0 }
        self.last_draw     = None, None, None
        self.screen        = None
        self.areas         = {}
        self.all_areas     = []
        
        # load default areas
        from listing_area   import Listing_Area
        from tvlisting_area import TVListing_Area
        from view_area      import View_Area
        from info_area      import Info_Area
        from default_areas  import Screen_Area, Title_Area, Subtitle_Area, Plugin_Area
        
        for a in ( 'screen', 'title', 'subtitle', 'view', 'listing', 'info', 'plugin'):
            self.areas[a] = eval('%s_Area()' % a.capitalize())
        self.areas['tvlisting'] = TVListing_Area()

        self.storage_file = os.path.join(config.FREEVO_CACHEDIR, 'skin-%s' % os.getuid())
        self.storage = util.read_pickle(self.storage_file)
        if self.storage and self.storage.has_key(config.SKIN_XML_FILE):
            self.display_style['menu'] = self.storage[config.SKIN_XML_FILE]
        else:
            self.display_style['menu'] = 0
        
        

    def set_screen(self, screen):
        """
        move the current drawing to a new screen object
        """
        for a in self.areas:
            self.areas[a].set_screen(screen)
        self.screen = screen


        
    def register(self, type, areas):
        """
        register a new type objects to the skin
        """
        setattr(self, '%s_areas' % type, [])
        for a in areas:
            if isinstance(a, str):
                getattr(self, '%s_areas' % type).append(self.areas[a])
            else:
                a.set_screen(self.screen)
                getattr(self, '%s_areas' % type).append(a)


    def delete(self, type):
        """
        delete informations about a special skin type
        """
        exec('del self.%s_areas' % type)
        self.last_draw = None, None, None


    def change_area(self, name, module, object):
        """
        replace an area with the code from module.object() from skins/plugins
        """
        exec('import skins.plugins.%s' % module)
        self.areas[name] = eval('skins.plugins.%s.%s()' % (module, object))

        
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

        if settings.special_menu.has_key(menu.item_types):
            area = settings.special_menu[menu.item_types]
        else:
            area = settings.default_menu['default']

        if self.display_style['menu'] >=  len(area.style):
            self.display_style['menu'] = 0
        self.display_style['menu'] = (self.display_style['menu'] + 1) % len(area.style)

        self.storage[config.SKIN_XML_FILE] = self.display_style['menu']
        util.save_pickle(self.storage, self.storage_file)
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
        self.screen.clear()
        for a in self.all_areas:
            a.clear()
        if osd_update:
            self.screen.show()


    def redraw(self):
        """
        redraw the current screen
        """
        _debug_('redraw', 2)
        if self.last_draw[0] and self.last_draw[1]:
            self.draw(self.last_draw[0], self.last_draw[1], self.last_draw[2])


    def draw(self, type, object, menu=None):
        """
        draw the object.
        object may be a menu widget, a table for the tv menu are an audio item for
        the audio player
        """
        if not self.screen:
            return
        
        # FIXME: 
        from gui import GUIObject
        if isinstance(object, GUIObject):
            # handling for gui objects: are they visible? what about children?
            if not object.visible:
                return

            draw_allowed = True
            for child in object.children:
                draw_allowed = draw_allowed and not child.visible

            if not draw_allowed:
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
            areas = getattr(self, '%s_areas' % type)
            for a in self.all_areas:
                if not a in areas:
                    print 'remove area %s' % a
                    a.clear()
            self.all_areas = areas
            

        self.last_draw = type, object, menu

        try:
            for a in self.all_areas:
                a.draw(settings, object, menu, style, type)
            self.screen.show()

        except UnicodeError, e:
            print '******************************************************************'
            print 'Unicode Error: %s' % e
            print 'Please report the following lines to the freevo mailing list'
            print 'or with the subject \'[Freevo-Bugreport\] Unicode\' to'
            print 'freevo@dischi-home.de.'
            print
            print traceback.print_exc()
            print
            print type, object
            if type == 'menu':
                for i in object.menustack[-1].choices:
                    print i
            print
            raise UnicodeError, e
