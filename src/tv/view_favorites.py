#if 0 /*
# -----------------------------------------------------------------------
# ViewFavorites.py -
#                    
#               
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/11/16 17:38:48  dischi
# i18n patch from David Sagnol
#
# Revision 1.4  2003/09/01 19:46:03  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.3  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------- */
#endif

import time

import config, record_client, edit_favorite
import event as em

from gui.GUIObject      import *
from gui.PopupBox       import *
from gui.Border         import *
from gui.Label          import *
from gui.ListBox        import *

DEBUG = 0


class ViewFavorites(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    handler   Function to call after pressing ENTER.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

        
    def __init__(self, parent='osd', text=None, search=None, handler=None, 
                 left=None, top=None, width=600, height=520, bg_color=None, 
                 fg_color=None, icon=None, border=None, bd_color=None, 
                 bd_width=None):

        if not text:
            text = _('View Favorites')
        
        PopupBox.__init__(self, parent, text, handler, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width)

        (self.server_available, msg) = record_client.connectionTest()
        if not self.server_available:
            errormsg = Label(_('Record server unavailable: %s') % msg, 
                             self, Align.CENTER)
            return 

        self.internal_h_align = Align.CENTER

        legend = Label(_('Name\tTitle\tChannel\tDOW\tTOD'), self, Align.CENTER)

        items_height = 40
        self.num_shown_items = 7
        self.results = ListBox(width=(self.width-2*self.h_margin),
                               height=self.num_shown_items*items_height,
                               show_v_scrollbar=0)
        self.results.y_scroll_interval = self.results.items_height = items_height
        max_results = 10

        self.results.set_h_align(Align.CENTER)
        self.add_child(self.results)

        (result, favorites) = record_client.getFavorites()

        if result:
            i = 0

            if len(favorites) > self.num_shown_items:
                self.results.show_v_scrollbar = 1
            else:
                self.results.show_v_scrollbar = 0

            f = lambda a, b: cmp(a.priority, b.priority)
            favorites = favorites.values()
            favorites.sort(f)
            for fav in favorites:
                i += 1
                self.results.add_item(text='%s : %s : %s : %s : %s' % \
                                        (fav.name, 
                                         fav.title,
                                         fav.channel_id,
                                         fav.dow,
                                         fav.mod),
                                      value=fav)

            space_left = self.num_shown_items - i
            if space_left > 0:
                for i in range(space_left):
                    self.results.add_item(text=' ', value=0)

            self.results.toggle_selected_index(0)


    def eventhandler(self, event, menuw=None):
        if not self.server_available:
            self.destroy()
            return

        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT):
            return self.results.eventhandler(event)
        elif event == em.INPUT_ENTER:
            edit_favorite.EditFavorite(parent=self.parent,
                           subject=self.results.get_selected_item().value).show()
            # self.destroy()
            return
        elif event == em.INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)

