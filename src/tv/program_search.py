#if 0 /*
# -----------------------------------------------------------------------
# ProgramSearch - a popup that allows the user to search the EPG
#                 using a remote.
#               
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/09/07 11:18:27  dischi
# many optical improvements
#
# Revision 1.8  2003/09/05 02:48:12  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.7  2003/09/01 19:46:03  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.6  2003/08/23 12:51:43  dischi
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

import config, tv.program_display, tv.tv_util
import tv.record_client as record_client
import event as em

from gui.GUIObject      import *
from gui.PopupBox       import *
from gui.Border         import *
from gui.Label          import *
from gui.LetterBoxGroup import *
from gui.ListBox        import *
from gui.Button         import *

DEBUG = 0


class ProgramSearch(PopupBox):
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
                 left=None, top=None, width=600, height=200, bg_color=None, 
                 fg_color=None, icon=None, border=None, bd_color=None, 
                 bd_width=None, vertical_expansion=1):

        if not text:
            text = 'Program Search'
        
        PopupBox.__init__(self, parent, text, handler, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width,
                          vertical_expansion)

        (self.server_available, msg) = record_client.connectionTest()
        if not self.server_available:
            errormsg = Label('Record server unavailable: %s\n\nFeel free to impliment this function inside the main guide.' % msg, 
                             self, Align.CENTER)
            return 


        self.internal_h_align = Align.CENTER

        self.lbg = LetterBoxGroup(text=search)
        self.add_child(self.lbg)

        items_height = Button('foo').height
        self.num_shown_items = 8
        self.results = ListBox(width=(self.width-2*self.h_margin),
                               height=self.num_shown_items*items_height,
                               show_v_scrollbar=0)
        self.results.y_scroll_interval = self.results.items_height = items_height
        max_results = 10

        self.results.set_h_align(Align.CENTER)
        self.add_child(self.results)

        if search:
            self.searchProg(search)
        self.center_on_screen = TRUE
        

    def searchProg(self, find):
        if DEBUG: print 'SEARCHING FOR: %s' % find
        pop = PopupBox(parent=self, text='Searching, please wait...')
        pop.show()

        (result, matches) = record_client.findMatches(find)

        if result:
            if DEBUG: print 'FOUND: %s' % len(matches)
            i = 0
            self.results.items = []

            if len(matches) > self.num_shown_items:
                self.results.show_v_scrollbar = 1
            else:
                self.results.show_v_scrollbar = 0

            f = lambda a, b: cmp(a.start, b.start)
            matches.sort(f)
            for prog in matches:
                i += 1
                self.results.add_item(text='%s %s: %s' % \
                                        (time.strftime('%b %d %I:%M %p', 
                                           time.localtime(prog.start)), 
                                         tv.tv_util.get_chan_displayname(prog.channel_id),
                                         prog.title),
                                      value=prog)

            space_left = self.num_shown_items - i
            if space_left > 0:
                for i in range(space_left):
                    self.results.add_item(text=' ', value=0)

        pop.destroy()


    def eventhandler(self, event, menuw=None):
        if not self.server_available:
            self.destroy()
            return

        if self.get_selected_child() == self.lbg:
            if event == em.INPUT_LEFT:
                self.lbg.change_selected_box('left')
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_RIGHT:
                self.lbg.change_selected_box('right')
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_ENTER:
                self.searchProg(self.lbg.get_word())
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_UP:
                self.lbg.get_selected_box().charUp()
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_DOWN:
                self.lbg.get_selected_box().charDown()
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.MENU_PAGEDOWN:
                self.lbg.get_selected_box().toggle_selected()
                self.results.toggle_selected_index(0)
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event in em.INPUT_ALL_NUMBERS:
                self.lbg.get_selected_box().cycle_phone_char(event)
                self.draw()
                self.osd.update(self.get_rect())
                return

        elif self.get_selected_child() == self.results:
            if event == em.INPUT_UP or event == em.INPUT_DOWN:
                return self.results.eventhandler(event)
            elif event in (em.INPUT_LEFT, em.INPUT_RIGHT, em.MENU_PAGEUP):
                self.results.get_selected_child().toggle_selected()
                self.lbg.boxes[0].toggle_selected()
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_ENTER:
                prog = self.results.get_selected_child().value
                if prog:
                    tv.program_display.ProgramDisplay(parent=self, prog=prog).show()
                return

        if event == em.INPUT_EXIT:
            self.destroy()
            return
        else:
            return self.parent.eventhandler(event)

