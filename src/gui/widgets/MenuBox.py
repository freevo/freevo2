# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# MenuBox - A dialog box for freevo showing a menu
# -----------------------------------------------------------------------
# $Id$
#
# Note: this is a very bad ugly hack!
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/08/01 10:37:08  dischi
# smaller changes to stuff I need
#
# Revision 1.2  2004/07/25 18:14:05  dischi
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
from event import *

from Window import Window
from label  import Label

import menu
import gui
import gui.areas.listing_area

class ListingArea(gui.areas.listing_area.Listing_Area):
    def __init__(self, x1, y1, x2, y2):
        gui.areas.listing_area.Listing_Area.__init__(self)
        self.real_x1 = x1
        self.real_y1 = y1
        self.real_x2 = x2
        self.real_y2 = y2

        
    def init_vars(self, settings, display_type, widget_type = 'menu'):
        """
        check which layout is used and set variables for the object
        """
        redraw = False
        self.settings = settings

        # get the correct <menu>
        area = settings.default_menu['default'].style[0][1]
        area = getattr(area, self.area_name)

        if (not self.area_val) or area != self.area_val:
            self.area_val = copy.copy(area)
            self.area_val.x = self.real_x1
            self.area_val.y = self.real_y1
            self.area_val.width = self.real_x2 - self.real_x1
            self.area_val.height = self.real_y2 - self.real_y1
            redraw = True
            
        if not area.layout:
            return redraw

        old_layout  = self.layout
        self.layout = area.layout

        if old_layout and old_layout != self.layout:
            redraw = True

        area.r = (area.x, area.y, area.width, area.height)
        return redraw


    def update_content(self):
        """
        update the listing area
        """
        r = gui.areas.listing_area.Listing_Area.update_content(self)
        for b in self.tmp_objects.bgimages:
            if not b.screen:
                b.layer += 200
        for b in self.tmp_objects.rectangles:
            if not b.screen:
                b.layer += 200
        for b in self.tmp_objects.images:
            if not b.screen:
                b.layer += 200
        for b in self.tmp_objects.text:
            if not b.screen:
                b.layer += 200
        return r
    
        
class MenuwWidget(menu.MenuWidget):
    def __init__(self, parent, x1, y1, x2, y2):
        self.menustack = [ menu.Menu('', []) ]
        self.rows      = 0
        self.cols      = 0
        self.eventhandler_plugins = []
        self.area = ListingArea(x1, y1, x2, y2)
        self.area.set_screen(gui.get_screen())
        self.settings = gui.get_settings()
        self.parent = parent
        

    def show(self):
        pass
    

    def hide(self):
        self.area.clear()
    

    def destroy(self):
        self.area.clear()
    

    def delete_menu(self, arg=None, menuw=None, allow_reload=True):
        menu.MenuWidget.delete_menu(self, arg, menuw, allow_reload)
        if len(self.menustack) == 1:
            self.parent.destroy()
            

    def delete_submenu(self, refresh=True, reload=False, osd_message=''):
        menu.MenuWidget.delete_submenu(self, refresh, reload, osd_message)
        if len(self.menustack) == 1:
            self.parent.destroy()
            

    def back_one_menu(self, arg=None, menuw=None):
        menu.MenuWidget.back_one_menu(self, arg, menuw)
        if len(self.menustack) == 1:
            self.parent.destroy()

        
    def refresh(self, reload=0):
        menu = self.menustack[-1]

        if self.menustack[-1].umount_all == 1:
            util.umount_all()
                    
        if reload:
            if menu.reload_func:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload
            self.init_page()

        self.area.draw(self.settings, self, self.menustack[-1])


class MenuBox(Window):
    """
    """
    def __init__(self, x=None, y=None, width=None, height=None,
                 vertical_expansion=1):

        Window.__init__(self, x, y, width, height)
        self.evt_context = 'menu'
        self.menuw    = MenuwWidget(self, self.x1 + 10, self.y1 + 10,
                                    self.x2 - 10, self.y2 - 10)
        self.pushmenu = self.menuw.pushmenu


    def eventhandler(self, event):
        if not self.menuw.eventhandler(event):
            return self.parent_handler(event)
        if self.screen:
            self.screen.update()
        return True


    def show(self):
        self.menuw.refresh()
        Window.show(self)
        

    def destroy(self):
        try:
            self.menuw.destroy()
            Window.destroy(self)
        except:
            pass
        
    def hide(self):
        self.menuw.destroy()
        self.menuw = None
        Window.hide(self)
        
