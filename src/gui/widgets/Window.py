# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Window - A window for freevo.
# -----------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2004/08/05 17:29:14  dischi
# improved screen and eventhandler
#
# Revision 1.8  2004/08/01 10:37:08  dischi
# smaller changes to stuff I need
#
# Revision 1.7  2004/07/27 18:52:31  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.6  2004/07/26 18:10:17  dischi
# move global event handling to eventhandler.py
#
# Revision 1.5  2004/07/25 19:47:38  dischi
# use application and not rc.app
#
# Revision 1.4  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------

import copy

import gui
import eventhandler

from base import GUIObject

class Window(GUIObject):
    """
    """
    def __init__(self, x1=None, y1=None, width=None, height=None):
        self.screen_width  = gui.get_screen().width
        self.screen_height = gui.get_screen().height
        self.evt_context   = 'input'

        self.center_on_screen = False

        if width == None:
            width  = self.screen_width / 2

        if height == None:
            height = self.screen_height / 4

        if x1 == None:
            x1 = self.screen_width/2 - width/2

        if y1 == None:
            y1  = self.screen_height/2 - height/2
            self.center_on_screen = True

        GUIObject.__init__(self, x1, y1, x1 + width, y1 + height)

        self.width  = width
        self.height = height

        self.__set_popupbox_style__()

        self.widget_normal   = self.content_layout.types['widget']
        self.widget_selected = self.content_layout.types['selected']
        self.button_normal   = self.content_layout.types['button']
        self.button_selected = self.content_layout.types['button selected']

        self.objects = []
        self.screen  = None
        self.add(self)

        
    def add(self, object):
        object.layer = 100
        self.objects.append(object)
        if self.screen:
            self.screen.add(object)
            

    def remove(self, object):
        self.objects.remove(object)
        if self.screen:
            self.screen.remove(object)


    def draw(self, rect=None):
        """
        The draw function.
        """
        _debug_('Window::_draw %s' % self, 2)
        
        for o in self.background_layout:
            if o[0] == 'rectangle':
                r = copy.deepcopy(o[1])
                r.width  = eval(str(r.width),  { 'MAX' : self.width })
                r.height = eval(str(r.height), { 'MAX' : self.height })

                if not r.width:
                    r.width  = self.width
                if not r.height:
                    r.height = self.height
                if r.x + r.width > self.width:
                    r.width = self.width - r.x
                if r.y + r.height > self.height:
                    r.height = self.height - r.y

            self.screen.drawbox(r.x + self.x1, r.y + self.y1,
                                r.x + r.width + self.x1,
                                r.y + r.height + self.y1,
                                r.bgcolor, r.size, r.color, r.radius)

    def show(self):
        if self.screen:
            return
        self.parent = eventhandler.get()
        self.parent_handler = self.parent.eventhandler
        eventhandler.append(self)

        self.screen = gui.get_screen()

        for o in self.objects:
            self.screen.add(o)
        self.screen.update()
        

    def destroy(self):
        eventhandler.remove(self)
        if not self.screen:
            return
        for o in self.objects:
            o.screen.remove(o)
        gui.get_screen().update()
        self.screen = None
        

    def __find_current_menu__(self, widget):
        if not widget:
            return None
        if not hasattr(widget, 'menustack'):
            return self.__find_current_menu__(widget.parent)
        return widget.menustack[-1]
        

    def __set_popupbox_style__(self, widget=None):
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
        import gui
        from gui import fxdparser
        menu = self.__find_current_menu__(widget)

        if menu and hasattr(menu, 'skin_settings') and menu.skin_settings:
            settings = menu.skin_settings
        else:
            settings = gui.settings.settings

        layout = settings.popup

        background = []
        for bg in layout.background:
            if isinstance(bg, fxdparser.Image):
                background.append(( 'image', bg))
            elif isinstance(bg, fxdparser.Rectangle):
                background.append(( 'rectangle', bg))

        self.content_layout   = layout.content
        self.background_layout = background
