# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Window - A window for freevo.
# -----------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.9  2004/08/05 17:29:14  dischi
# improved screen and eventhandler
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

from mevas.container import CanvasContainer

import eventhandler
import gui

class Window(CanvasContainer):
    """
    """
    def __init__(self, x=None, y=None, width=None, height=None):
        CanvasContainer.__init__(self)
        self.set_zindex(100)
        
        self._display_width  = gui.get_display().width
        self._display_height = gui.get_display().height
        self.evt_context   = 'input'

        self.center_on_screen = False

        if width == None:
            width  = self._display_width / 2

        if height == None:
            height = self._display_height / 4

        if x == None:
            x = self._display_width/2 - width/2

        if y == None:
            y  = self._display_height/2 - height/2
            self.center_on_screen = True

        self.__set_popupbox_style__()

        self.set_size((width, height))
        self.set_pos((x, y))
        
        self.widget_normal   = self.content_layout.types['widget']
        self.widget_selected = self.content_layout.types['selected']
        self.button_normal   = self.content_layout.types['button']
        self.button_selected = self.content_layout.types['button selected']

        self._display  = None


    def _create_background(self, screen):
        """
        The draw function.
        """
        _debug_('Window::_create_background %s' % self, 1)
        
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

            r = gui.Rectangle((r.x, r.y), (r.width, r.height),
                              r.bgcolor, r.size, r.color, r.radius)
            r.set_zindex(-1)
            self.add_child(r)

            
    def show(self):
        if self._display:
            return
        self.parent_handler = eventhandler.get().eventhandler
        eventhandler.append(self)

        self._display = gui.get_display()
        self._create_background(self._display)
        self._display.add_child(self)
        self._display.update()


    def destroy(self):
        eventhandler.remove(self)
        if not self._display:
            return
        self._display.remove_child(self)
        self._display.update()
        self._display = None
        

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
