# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# window.py - A window for popup boxes in freevo.
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a window used by the different kinds of popup boxes in
# Freevo. A window is always on top and gets the focus. The class only
# handles the basic window functions like show/destroy and drawing the
# background and border of the window. What the window should do needs to be
# defined in inherting classes like WaitBox in popups.py.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Version: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import copy

# freevo imports
import eventhandler

# gui imports
import displays
from theme_engine import get_theme
from widgets import Rectangle, Container


class Window(Container):
    """
    A window for Freevo popups. This class will only draw the background and
    border and has some basic functions to get skin informations and show
    hide methods. When a window is shown, it will get the focus to the
    eventhandler that needs to be defined by inherting classes.
    Not setting x, y, width and height will result in centering the window
    with a default size.
    """
    def __init__(self, pos=(None, None), size=(None, None)):
        Container.__init__(self)
        self.set_zindex(100)
        self.event_context = 'input'
        self.__display  = None

        # setting the size
        width  = size[0] or displays.get().width / 2
        height = size[1] or displays.get().height / 4
        self.set_size((width, height))

        # setting the position
        x, y = pos
        if x == None: x = displays.get().width/2 - width/2
        if y == None: y = displays.get().height/2 - height/2
        self.set_pos((x, y))

        # get theme values how the window should look like
        layout = get_theme().popup.content
        self.widget_normal   = layout.types['widget']
        self.widget_selected = layout.types['selected']
        self.button_normal   = layout.types['button']
        self.button_selected = layout.types['button selected']
        self.content_spacing = layout.spacing

        # get position where the content should be inside the window
        self.__c_x = int(eval(str(layout.x), { 'MAX': 0}))
        self.__c_y = int(eval(str(layout.y), { 'MAX': 0}))
        self.__c_w = -int(eval(str(layout.width), { 'MAX': 0}))
        self.__c_h = -int(eval(str(layout.height), { 'MAX': 0}))


    def __create_background(self, screen):
        """
        Draw the background and border of the window based on the theme
        settings.
        """
        objects = get_theme().popup.background
        for r in filter(lambda x: x.type == 'rectangle', objects):
            # calculate size of the rectangle
            width  = eval(str(r.width),  { 'MAX' : self.width })
            height = eval(str(r.height), { 'MAX' : self.height })
            if not width: width = self.width
            if not height: height = self.height
            if r.x + width > self.width: width = self.width - r.x
            if r.y + height > self.height: height = self.height - r.y

            # draw the rectangle and add it to the window, use zindex = -1
            # to make sure it is below the content
            r = Rectangle((r.x, r.y), (width, height), r.bgcolor, r.size,
                          r.color, r.radius)
            r.set_zindex(-1)
            self.add_child(r)


    def get_content_pos(self):
        """
        Return the position of the content inside the window
        """
        return self.__c_x, self.__c_y


    def get_content_size(self):
        """
        Return the size the content can have inside the window
        """
        w, h = self.get_size()
        return w - self.__c_w, h - self.__c_h
    
            
    def show(self):
        """
        Show the window on the screen
        """
        if self.__display:
            return
        eventhandler.add_window(self)
        self.__display = displays.get()
        self.__create_background(self.__display)
        self.__display.add_child(self)
        self.__display.update()


    def destroy(self):
        """
        Destroy (close) the window
        """
        eventhandler.remove_window(self)
        if not self.__display:
            return
        self.__display.remove_child(self)
        self.__display.update()
        self.__display = None


    def eventhandler(self):
        """
        Eventhandler for the window, this raw window has nothing to do
        """
        return False
