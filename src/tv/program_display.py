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
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    """
    
    def __init__(self, parent=None, prog=None, left=None, top=None, width=600,
                 height=520):

        self.left = left
        self.top = top
        self.prog = prog
        self.font = None

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

        start = Label('Start:\t%s on %s' % (time.strftime('%A %b %d %I:%M %p', 
                                        time.localtime(self.prog.start)),
                                        self.prog.channel_id), 
                                        self, Align.LEFT)

        stop = Label('Stop:\t%s' % time.strftime('%A %b %d %I:%M %p', 
                                     time.localtime(self.prog.stop)), 
                                     self, Align.LEFT)

        self.options = ListBox(width=(self.width-2*self.h_margin), 
                               height=200, show_v_scrollbar=0)
        self.options.items_height = 40
        self.options.add_item(text='Record this episode', value=1)
        self.options.add_item(text='Search for more of this program', value=2)
        self.options.add_item(text='Add "%s" to favorites' % prog.title, value=3)
        self.options.add_item(text='View favorites', value=4)
        self.options.add_item(text='View scheduled recordings', value=5)

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
                view_favorites.ViewFavorites(parent=self).show()
            elif self.options.get_selected_item().value == 5:
                view_recordings.ViewScheduledRecordings(parent=self).show()

        elif event == em.INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)

