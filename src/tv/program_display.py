#!/usr/bin/env python
#-----------------------------------------------------------------------
# ProgramDisplay - Information and actions for TvPrograms.
#-----------------------------------------------------------------------
# $Id$
#
# Todo: 
# Notes: 
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/06/03 01:41:38  rshortt
# More progress, still ots to do.
#
# Revision 1.1  2003/06/01 19:05:15  rshortt
# Better to commit these before I mess something up.  Still event code to fix I think, among other things.
#
#
#
#-----------------------------------------------------------------------
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

import time

import config, record_client, edit_favorite
import view_favorites, program_search
import event as em

from gui.GUIObject import *
from gui.Border    import *
from gui.Label     import *
from gui.ListBox   import *
from gui.AlertBox  import *

DEBUG = 1


class ProgramDisplay(PopupBox):
    """
    prog      the program to record
    context   guide or recording
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    """
    
    def __init__(self, parent=None, prog=None, context=None, left=None, 
                 top=None, width=600, height=440):

        self.left = left
        self.top = top
        self.prog = prog
        self.font = None

        if context:
            self.context = context
        else:
            self.context = 'guide'

        PopupBox.__init__(self, left=left, top=top, width=width, 
                          height=height)

        self.v_spacing = 15
        self.h_margin = 20
        self.v_margin = 20

        self.internal_h_align = Align.LEFT

        if self.prog.sub_title:
            title_txt = 'Title:\t%s - %s' % (self.prog.title, self.prog.sub_title)
        else:
            title_txt = 'Title:\t%s' % self.prog.title

        title = Label(title_txt, self, Align.LEFT)

        desc = Label('Description:\t%s' % self.prog.desc, self, Align.LEFT)

        chan = Label('Channel:\t%s' % self.prog.channel_id, self, Align.LEFT)

        start = Label('Start:\t%s' % time.strftime('%A %b %d %I:%M %p', 
                                      time.localtime(self.prog.start)),
                                      self, Align.LEFT)

        stop = Label('Stop:\t%s' % time.strftime('%A %b %d %I:%M %p', 
                                     time.localtime(self.prog.stop)), 
                                     self, Align.LEFT)
        items_height = 40

        if self.context == 'guide':
            num_items = 3
        else:
            num_items = 1

        self.options = ListBox(width=(self.width-2*self.h_margin), 
                               height=items_height*num_items, 
                               show_v_scrollbar=0)
        self.options.items_height = items_height

        if self.context == 'guide':
            self.options.add_item(text='Record this episode', value=1)
            self.options.add_item(text='Search for more of this program', value=2)
            self.options.add_item(text='Add "%s" to favorites' % prog.title, value=3)
        else:
            self.options.add_item(text='Remove from scheduled recordings', value=4)

        self.options.set_h_align(Align.CENTER)
        self.options.toggle_selected_index(0)
        self.add_child(self.options)


    def eventhandler(self, event):
        if DEBUG: print 'ProgramDisplay: event = %s' % event

        trapped = em.MENU_EVENTS.values()

        #if event in trapped:
        #    return
        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT):
            if DEBUG: print 'ProgramDisplay: should scroll'
            return self.options.eventhandler(event)

        elif event == em.INPUT_ENTER:
            if self.options.get_selected_item().value == 1:
                (result, msg) = record_client.scheduleRecording(self.prog)
                if result:
                    AlertBox(parent=self, 
                             text='%s has been scheduled for recording' % \
                              self.prog.title, handler=self.destroy).show()
                else:
                    AlertBox(parent=self, 
                             text='Scheduling Failed: %s' % msg).show()
            elif self.options.get_selected_item().value == 2:
                program_search.ProgramSearch(parent=self, 
                                             search=self.prog.title).show()
            elif self.options.get_selected_item().value == 3:
                edit_favorite.EditFavorite(parent=self, 
                                           subject=self.prog).show()
            elif self.options.get_selected_item().value == 4:
                (result, msg) = record_client.removeScheduledRecording(self.prog)
                if result:
                    AlertBox(parent=self, 
                             text='%s has been removed' % \
                              self.prog.title, handler=self.destroy).show()
                else:
                    AlertBox(parent=self, 
                             text='Remove Failed: %s' % msg).show()

        elif event == em.INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)



class ScheduledRecordings(PopupBox):
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

        
    def __init__(self, parent='osd', text=None, handler=None, 
                 left=None, top=None, width=600, height=520, bg_color=None, 
                 fg_color=None, icon=None, border=None, bd_color=None, 
                 bd_width=None):

        if not text:
            text = 'Scheduled Recordings'
        
        PopupBox.__init__(self, parent, text, handler, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width)


        (self.result, recordings) = record_client.getScheduledRecordings()
        if self.result:
            progs = recordings.getProgramList()
        else:
            errormsg = Label('Get recordings failed: %s' % recordings, 
                             self, Align.CENTER)
            return 

        self.internal_h_align = Align.CENTER

        items_height = 40
        self.num_shown_items = 7
        self.results = ListBox(width=(self.width-2*self.h_margin),
                               height=self.num_shown_items*items_height,
                               show_v_scrollbar=0)
        self.results.y_scroll_interval = self.results.items_height = items_height
        max_results = 10

        self.results.set_h_align(Align.CENTER)
        self.add_child(self.results)


        if self.result:
            i = 0
            self.results.items = []

            if len(progs) > self.num_shown_items:
                self.results.show_v_scrollbar = 1
            else:
                self.results.show_v_scrollbar = 0

            f = lambda a, b: cmp(a.start, b.start)
            progs = progs.values()
            progs.sort(f)
            for prog in progs:
                i += 1
                self.results.add_item(text='%s %s: %s' % \
                                        (time.strftime('%b %d %I:%M %p',
                                           time.localtime(prog.start)),
                                         prog.channel_id,
                                         prog.title),
                                      value=prog)

            space_left = self.num_shown_items - i
            if space_left > 0:
                for i in range(space_left):
                    self.results.add_item(text=' ', value=0)

            self.results.toggle_selected_index(0)


    def eventhandler(self, event):
        if not self.result:
            self.destroy()
            return

        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT):
            return self.results.eventhandler(event)
        elif event == em.INPUT_ENTER:
            ProgramDisplay(prog=self.results.get_selected_item().value,
                           context='recording', height=360).show()
            return
        elif event == em.INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)


