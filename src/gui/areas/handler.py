# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# handler.py - area handler
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/08/14 15:07:34  dischi
# New area handling to prepare the code for mevas
# o each area deletes it's content and only updates what's needed
# o work around for info and tvlisting still working like before
# o AreaHandler is no singleton anymore, each type (menu, tv, player)
#   has it's own instance
# o clean up old, not needed functions/attributes
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


import os
import traceback

import config
import util


class AreaHandler:
    """
    main skin class
    """
    
    def __init__(self, type, areas, settings, screen):
        """
        init the skin engine
        """
        self.type          = type
        self.settings      = settings
        self.display_style = { 'menu' : 0 }
        self.screen        = screen
        self.areas         = []
        
        # load default areas
        from listing_area   import Listing_Area
        from tvlisting_area import TVListing_Area as Tvlisting_Area
        from view_area      import View_Area
        from info_area      import Info_Area
        from default_areas  import Screen_Area, Title_Area, Subtitle_Area

        for a in areas:
            if isinstance(a, str):
                self.areas.append(eval('%s_Area()' % a.capitalize()))
            else:
                self.areas.append(a)

        for a in self.areas:
            a.set_screen(screen)

        self.storage_file = os.path.join(config.FREEVO_CACHEDIR, 'skin-%s' % os.getuid())
        self.storage = util.read_pickle(self.storage_file)
        if self.storage and self.storage.has_key(config.SKIN_XML_FILE):
            self.display_style['menu'] = self.storage[config.SKIN_XML_FILE]
        else:
            self.display_style['menu'] = 0


    def __del__(self):
        """
        delete an area handler
        """
        _debug_('delete AreaHandler for %s' % self.type)
        while self.areas:
            self.areas[0].clear_all()
            del self.areas[0]


    def toggle_display_style(self, menu):
        """
        Toggle display style
        """
        if isinstance(menu, str):
            if not self.display_style.has_key(menu):
                self.display_style[menu] = 0
            self.display_style[menu] = (self.display_style[menu] + 1) % \
                                       len(self.settings.sets[menu].style)
            return
            
        if menu.force_skin_layout != -1:
            return
        
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



    def __scan_for_text_view__(self, menu):
        """
        scan if we have to fall back to text view. This will be done if some
        items have images and all images are the same. And the number of items
        must be greater 5. With that the skin will fall back to text view for
        e.g. mp3s inside a folder with cover file
        """
        try:
            self.use_text_view = menu.skin_force_text_view
            try:
                self.use_images      = menu.skin_default_has_images
                self.use_description = menu.skin_default_has_description
            except:
                self.use_images      = False
                self.use_description = False
            return
        except:
            pass

        image  = None
        folder = 0

        menu.skin_default_has_images      = False
        menu.skin_default_has_description = False

        if hasattr(menu, 'is_submenu'):
            menu.skin_default_has_images = True
            
        for i in menu.choices:
            if i.image:
                menu.skin_default_has_images = True
            if i['description'] or i.type:
                # have have a description if description is an attribute
                # or when the item has a type (special skin handling here)
                menu.skin_default_has_description = True
            if menu.skin_default_has_images and menu.skin_default_has_description:
                break
            
        self.use_images      = menu.skin_default_has_images
        self.use_description = menu.skin_default_has_description

        if len(menu.choices) < 6:
            try:
                if menu.choices[0].info_type == 'track':
                    menu.skin_force_text_view = True
                    self.use_text_view = True
                    return
            except:
                pass

            for i in menu.choices:
                if config.SKIN_FORCE_TEXTVIEW_STYLE == 1 and \
                       i.type == 'dir' and not i.media:
                    # directory with few items and folder:
                    self.use_text_view = False
                    return
                    
                if image and i.image != image:
                    menu.skin_force_text_view = False
                    self.use_text_view        = False
                    return
                image = i.image

            menu.skin_force_text_view = True
            self.use_text_view        = True
            return

        for i in menu.choices:
            if i.type == 'dir':
                folder += 1
                # directory with mostly folder:
                if config.SKIN_FORCE_TEXTVIEW_STYLE == 1 and folder > 3 and not i.media:
                    self.use_text_view = False
                    return
                    
            if image and i.image != image:
                menu.skin_force_text_view = False
                self.use_text_view        = False
                return
            image = i.image
            
        menu.skin_force_text_view = True
        self.use_text_view        = True

    
    def __get_display_style__(self, menu=None):
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



    def clear(self):
        """
        clean the screen
        """
        _debug_('clear skin (%s)' % self.type)
        for a in self.areas:
            a.clear_all()



    def draw(self, object):
        """
        draw the object.
        object may be a menu, a table for the tv menu are an audio item for
        the audio player
        """
        if not self.screen:
            return
        
        settings = self.settings
            
        if self.type == 'menu':
            if object.skin_settings:
                settings = object.skin_settings
            style = self.__get_display_style__(object)

            if object.force_skin_layout != -1:
                style = object.force_skin_layout

            # get the correct <menu>
            if object.item_types and settings.special_menu.has_key(object.item_types):
                area_definitions = settings.special_menu[object.item_types]
            else:
                self.__scan_for_text_view__(object)

                name = 'default'
                if self.use_description:
                    name += ' description'
                if not self.use_images:
                    name += ' no image'
                area_definitions = settings.default_menu[name]

            # get the correct style based on style
            if len(area_definitions.style) > style:
                area_definitions = area_definitions.style[style]
            else:
                try:
                    area_definitions = area_definitions.style[0]
                except IndexError:
                    print 'index error for %s %s' % (style, 'menu')
                    raise

            if area_definitions[0] and area_definitions[1]:
                self.__scan_for_text_view__(object)
                if not self.use_text_view:
                    area_definitions = area_definitions[0]
                else:
                    area_definitions = area_definitions[1]
            elif area_definitions[1]: 
                area_definitions = area_definitions[1]
            else:
                area_definitions = area_definitions[0]

            viewitem = object.viewitem or object.selected
            infoitem = object.infoitem or object.selected
                
        else:
            style = self.__get_display_style__(self.type)
            area_definitions  = settings.sets[self.type]
            if hasattr(area_definitions, 'style'):
                try:
                    area_definitions = area_definitions.style[style][1]
                except:
                    area_definitions = area_definitions.style[0][1]
            try:
                viewitem = object.selected
                infoitem = object.selected
            except:
                viewitem = object
                infoitem = object

        try:
            for a in self.areas:
                a.draw(settings, object, viewitem, infoitem, area_definitions)
            self.screen.update()

        except UnicodeError, e:
            print '******************************************************************'
            print 'Unicode Error: %s' % e
            print 'Please report the following lines to the freevo mailing list'
            print 'or with the subject \'[Freevo-Bugreport\] Unicode\' to'
            print 'freevo@dischi-home.de.'
            print
            print traceback.print_exc()
            print
            print self.type, object
            if hasattr(object, 'choices'):
                for i in object.choices:
                    print i
            print
            raise UnicodeError, e