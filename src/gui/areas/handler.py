# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# handler.py - Handling the different used areas
# -----------------------------------------------------------------------------
# $Id$
#
# The Handler can be used to draw application on the screen. It uses
# different areas also defined in this directory for the real drawing.
#
# The handler itself checks the theme and calls the draw function of the areas
#
# TODO: o more documentation how to use the Handler
#       o remove Container definition in this file
#       o do not add various stuff to the item object, use a specific dict
#         for that
#       o cleanup and internal documentation
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------------

__all__ = [ 'Handler' ]

# python imports
import os
import traceback
import time

import logging
log = logging.getLogger('gui')

# freevo imports
import config
import util.cache
from kaa.weakref import weakref

# gui imports
import gui
import gui.animation as animation 
from gui.widgets import Container
import gui.theme
import gui.imagelib as imagelib

# areas
from default_areas  import *
for f in os.listdir(os.path.dirname(__file__)):
    if f.endswith('_area.py'):
        exec('from %s import *' % f[:-3])


class Handler(object):
    """
    Handler for the areas used to draw an application on the screen.
    """
    def __init__(self, type, areas):
        """
        Init the handler by laoding all areas
        """
        self.type          = type
        self.display_style = { 'menu' : 0 }
        self.areas         = []
        self.visible       = False

        self.canvas = gui.display
        
        self.layer = (Container('Handler: Background'),
                      Container('Handler: Content'))
        self.layer[0].set_zindex(-10)

        for c in self.layer:
            c.sticky = True
            c.hide()
            self.canvas.add_child(c)

        self.imagelib  = imagelib
        self.width     = self.canvas.width
        self.height    = self.canvas.height

        for a in areas:
            if isinstance(a, str):
                self.areas.append(eval('%sArea()' % a.capitalize()))
            else:
                self.areas.append(a)

        for a in self.areas:
            # Set the screen of the areas to this area handler.
            # Use a weakref to avoid memory problems.
            a.set_screen(weakref(self))
            
        self.storage_file = os.path.join(config.FREEVO_CACHEDIR,
                                         'skin-%s' % os.getuid())
        self.display_style['menu'] = 0
        if os.path.isfile(self.storage_file):
            self.storage = util.cache.load(self.storage_file)
            if self.storage and self.storage.has_key(config.GUI_XML_FILE):
                self.display_style['menu'] = self.storage[config.GUI_XML_FILE]
	else:
	    self.storage = None


    def __del__(self):
        """
        Delete an area handler
        """
        log.info('Delete AreaHandler %s' % self.type)
        while self.areas:
            self.areas[0].clear_all()
            del self.areas[0]
        for l in self.layer:
            l.unparent()
        self.layer = []
        self.container = None

        
    def toggle_display_style(self, menu):
        """
        Toggle display style
        """
        theme = gui.theme.get()

        if isinstance(menu, str):
            if not self.display_style.has_key(menu):
                self.display_style[menu] = 0
            self.display_style[menu] = (self.display_style[menu] + 1) % \
                                       len(theme.sets[menu].style)
            return
            
        if menu.force_skin_layout != -1:
            return
        
        if theme.special_menu.has_key(menu.item_types):
            area = theme.special_menu[menu.item_types]
        else:
            area = theme.default_menu['default']

        if self.display_style['menu'] >=  len(area.style):
            self.display_style['menu'] = 0
        self.display_style['menu'] = (self.display_style['menu'] + 1) % \
                                     len(area.style)

        if self.storage and self.storage.has_key(config.GUI_XML_FILE):
            self.storage[config.GUI_XML_FILE] = self.display_style['menu']
            util.cache.save(self.storage_file, self.storage)



    def __scan_for_text_view(self, menu):
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

        if menu.submenu:
            menu.skin_default_has_images = True
            
        for i in menu.choices:
            if i.image:
                menu.skin_default_has_images = True
            if i['description'] or i.type:
                # have have a description if description is an attribute
                # or when the item has a type (special skin handling here)
                menu.skin_default_has_description = True
            if menu.skin_default_has_images and \
                   menu.skin_default_has_description:
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
                if config.GUI_FORCE_TEXTVIEW_STYLE == 1 and \
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
                if config.GUI_FORCE_TEXTVIEW_STYLE == 1 and folder > 3 \
                       and not i.media:
                    self.use_text_view = False
                    return
                    
            if image and i.image != image:
                menu.skin_force_text_view = False
                self.use_text_view        = False
                return
            image = i.image
            
        menu.skin_force_text_view = True
        self.use_text_view        = True

    
    def __get_display_style(self, menu=None):
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



    def hide(self, fade=0):
        """
        hide the screen
        """
        if self.visible:
            if fade:
                a = animation.FadeAnimation(self.layer, fade, 255, 0)
                a.application = True
                a.start()
            else:
                for l in self.layer:
                    l.hide()
        self.visible = False
        

    def show(self, fade=0):
        """
        hide the screen
        """
        if not self.visible:
            if fade:
                a = animation.FadeAnimation(self.layer, fade, 0, 255)
                a.application = True
                a.start()
            else:
                for l in self.layer:
                    l.set_alpha(255)
                    l.show()
                self.canvas.update()
        self.visible = True


    def draw(self, object):
        """
        draw the object.
        object may be a menu, a table for the tv menu are an audio item for
        the audio player
        """
        theme = gui.theme.get()
        
        if self.type == 'menu':
            style = self.__get_display_style(object)

            if object.force_skin_layout != -1:
                style = object.force_skin_layout

            # get the correct <menu>
            if object.item_types and \
                   theme.special_menu.has_key(object.item_types):
                area_definitions = theme.special_menu[object.item_types]
            else:
                self.__scan_for_text_view(object)

                name = 'default'
                if self.use_description:
                    name += ' description'
                if not self.use_images:
                    name += ' no image'
                area_definitions = theme.default_menu[name]

            # get the correct style based on style
            if len(area_definitions.style) > style:
                area_definitions = area_definitions.style[style]
            else:
                area_definitions = area_definitions.style[0]

            if area_definitions[0] and area_definitions[1]:
                self.__scan_for_text_view(object)
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
            style = self.__get_display_style(self.type)
            area_definitions  = theme.sets[self.type]
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

        t1 = time.time()
        try:
            for a in self.areas:
                a.draw(theme, object, viewitem, infoitem, area_definitions)
            t2 = time.time()
            if self.visible:
                self.canvas.update()
            t3 = time.time()
            log.debug('time debug: %s %s' % (t2-t1, t3-t2))

        except UnicodeError, e:
            print '***********************************************************'
            print 'Unicode Error: %s' % e
            print 'Please report the following lines to the freevo mailing'
            print 'list or with the subject \'[Freevo-Bugreport\] Unicode\' to'
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
