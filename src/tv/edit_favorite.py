#!/usr/bin/env python
#-----------------------------------------------------------------------
# EditFavorite - 
#-----------------------------------------------------------------------
# $Id$
#
# Todo: 
# Notes: 
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/11/16 17:38:48  dischi
# i18n patch from David Sagnol
#
# Revision 1.4  2003/09/05 02:48:12  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.3  2003/09/01 19:46:02  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.2  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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

import config, tv.epg_xmltv, tv.view_favorites
import tv.record_client as record_client
import event as em

from tv.record_types import Favorite
import tv.record_types
from tv.epg_types import TvProgram

from gui.GUIObject      import *
from gui.Border         import *
from gui.Label          import *
from gui.AlertBox       import *
from gui.OptionBox      import *
from gui.LetterBoxGroup import *

DEBUG = 1
TRUE = 1
FALSE = 0


class EditFavorite(PopupBox):
    """
    prog      the program to record
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    """
    
    def __init__(self, parent=None, subject=None, left=None, top=None, width=500,
                 height=350):

        self.oldname = None

        print 'DEBUG::subject: %s' % dir(subject)
        print 'DEBUG::subject::__module__ %s' % subject.__module__
        #if isinstance(subject, tv.record_types.Favorite):
        #    print 'DEBUG::subject: FUCK'
        #    self.fav = subject
        #    self.oldname = self.fav.name
        #elif isinstance(subject, TvProgram):
        if isinstance(subject, TvProgram):
            (result, favs) = record_client.getFavorites()
            if result:
                num_favorites = len(favs)
                self.priority = num_favorites + 1
            else:
                self.priority = 1

            self.fav = Favorite(subject.title, subject, TRUE, TRUE, TRUE, self.priority)
        else:
            self.fav = subject
            self.oldname = self.fav.name
            


        PopupBox.__init__(self, text=_('Edit Favorite'), left=left, top=top, width=width, 
                          height=height)

        self.v_spacing = 15
        self.h_margin = 20
        self.v_margin = 20

        self.internal_h_align = Align.LEFT

        if not self.left:     self.left   = self.osd.width/2 - self.width/2
        if not self.top:      self.top    = self.osd.height/2 - self.height/2

        guide = tv.epg_xmltv.get_guide()

        name = Label(_('Name:\t'), self, Align.LEFT)
        self.name_input = LetterBoxGroup(text=self.fav.name)
        self.name_input.h_align = Align.NONE
        self.add_child(self.name_input)


        title = Label(_('Title:\t%s') % self.fav.title, self, Align.LEFT)

        chan = Label(_('Channel:\t'), self, Align.LEFT)

        self.chan_box = OptionBox('ANY')
        self.chan_box.h_align = Align.NONE
        self.chan_box.add_item(text='ANY', value='ANY')
      
        i = 0
        chan_index = 0
        for ch in guide.chan_list:
            if ch.id == self.fav.channel_id:
                chan_index = i
            i += 1
            self.chan_box.add_item(text=ch.id, value=ch.id)


        self.chan_box.toggle_selected_index(chan_index)
        self.add_child(self.chan_box)

        dow = Label(_('Day of Week:\t'), self, Align.LEFT)
        self.dow_box = OptionBox('ANY DAY')
        self.dow_box.h_align = Align.NONE

        self.dow_box.add_item(text=_('ANY DAY'), value='ANY')
        self.dow_box.add_item(text=_('Mon'), value=0)
        self.dow_box.add_item(text=_('Tues'), value=1)
        self.dow_box.add_item(text=_('Wed'), value=2)
        self.dow_box.add_item(text=_('Thurs'), value=3)
        self.dow_box.add_item(text=_('Fri'), value=4)
        self.dow_box.add_item(text=_('Sat'), value=5)
        self.dow_box.add_item(text=_('Sun'), value=6)

        self.dow_box.toggle_selected_index(0)
        self.add_child(self.dow_box)

        tod = Label(_('Time of Day:\t'), self, Align.LEFT)
        self.tod_box = OptionBox('ANY')
        self.tod_box.h_align = Align.NONE
        self.tod_box.add_item(text=_('ANY TIME'), value='ANY')
        self.tod_box.add_item(text='12:00 AM', value=0)
        self.tod_box.add_item(text='11:30 AM', value=30)
        self.tod_box.add_item(text='1:00 AM', value=60)
        self.tod_box.add_item(text='1:30 AM', value=90)
        self.tod_box.add_item(text='2:00 AM', value=120)
        self.tod_box.add_item(text='2:30 AM', value=150)
        self.tod_box.add_item(text='3:00 AM', value=180)
        self.tod_box.add_item(text='3:30 AM', value=210)
        self.tod_box.add_item(text='4:00 AM', value=240)
        self.tod_box.add_item(text='4:30 AM', value=270)
        self.tod_box.add_item(text='5:00 AM', value=300)
        self.tod_box.add_item(text='5:30 AM', value=330)
        self.tod_box.add_item(text='6:00 AM', value=360)
        self.tod_box.add_item(text='6:30 AM', value=390)
        self.tod_box.add_item(text='7:00 AM', value=420)
        self.tod_box.add_item(text='7:30 AM', value=450)
        self.tod_box.add_item(text='8:00 AM', value=480)
        self.tod_box.add_item(text='8:30 AM', value=510)
        self.tod_box.add_item(text='9:00 AM', value=540)
        self.tod_box.add_item(text='9:30 AM', value=570)
        self.tod_box.add_item(text='10:00 AM', value=600)
        self.tod_box.add_item(text='10:30 AM', value=630)
        self.tod_box.add_item(text='11:00 AM', value=660)
        self.tod_box.add_item(text='11:30 AM', value=690)
        self.tod_box.add_item(text='12:00 PM', value=720)
        self.tod_box.add_item(text='12:30 PM', value=750)
        self.tod_box.add_item(text='1:00 PM', value=780)
        self.tod_box.add_item(text='1:30 PM', value=810)
        self.tod_box.add_item(text='2:00 PM', value=840)
        self.tod_box.add_item(text='2:30 PM', value=870)
        self.tod_box.add_item(text='3:00 PM', value=900)
        self.tod_box.add_item(text='3:30 PM', value=930)
        self.tod_box.add_item(text='4:00 PM', value=960)
        self.tod_box.add_item(text='4:30 PM', value=990)
        self.tod_box.add_item(text='5:00 PM', value=1020)
        self.tod_box.add_item(text='5:30 PM', value=1050)
        self.tod_box.add_item(text='6:00 PM', value=1080)
        self.tod_box.add_item(text='6:30 PM', value=1110)
        self.tod_box.add_item(text='7:00 PM', value=1140)
        self.tod_box.add_item(text='7:30 PM', value=1170)
        self.tod_box.add_item(text='8:00 PM', value=1200)
        self.tod_box.add_item(text='8:30 PM', value=1230)
        self.tod_box.add_item(text='9:00 PM', value=1260)
        self.tod_box.add_item(text='9:30 PM', value=1290)
        self.tod_box.add_item(text='10:00 PM', value=1320)
        self.tod_box.add_item(text='10:30 PM', value=1350)
        self.tod_box.add_item(text='11:00 PM', value=1380)
        self.tod_box.add_item(text='11:30 PM', value=1410)
      
        self.tod_box.toggle_selected_index(0)
        self.add_child(self.tod_box)

        self.save = Button(_('Save'))
        self.add_child(self.save)


    def eventhandler(self, event, menuw=None):
        print 'SELECTED CHILD: %s' % self.get_selected_child()
        if self.get_selected_child() == self.name_input:
            if event == em.INPUT_LEFT:
                self.name_input.change_selected_box('left')
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_RIGHT:
                self.name_input.change_selected_box('right')
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_ENTER:
                self.name_input.get_selected_box().toggle_selected()
                self.chan_box.toggle_selected()
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_UP:
                self.name_input.get_selected_box().charUp()
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_DOWN:
                self.name_input.get_selected_box().charDown()
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event in em.INPUT_ALL_NUMBERS: 
                self.name_input.get_selected_box().cycle_phone_char(event)
                self.draw()
                self.osd.update(self.get_rect())
                return
            elif event == em.INPUT_EXIT:
                self.destroy()
                return

        elif self.get_selected_child() == self.chan_box:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.chan_box.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.chan_box.selected or self.chan_box.list.is_visible():
                    if DEBUG: print '  Want to toggle_box'
                    self.chan_box.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.chan_box.toggle_selected()
                self.name_input.boxes[0].toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.chan_box.toggle_selected()
                self.dow_box.toggle_selected()
                self.draw()
            elif event == em.INPUT_EXIT:
                self.destroy()
                return
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.dow_box:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.dow_box.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.dow_box.selected or self.dow_box.list.is_visible():
                    self.dow_box.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.dow_box.toggle_selected()
                self.chan_box.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.dow_box.toggle_selected()
                self.tod_box.toggle_selected()
                self.draw()
            elif event == em.INPUT_EXIT:
                self.destroy()
                return
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.tod_box:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.tod_box.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.tod_box.selected or self.tod_box.list.is_visible():
                    self.tod_box.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.tod_box.toggle_selected()
                self.dow_box.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.tod_box.toggle_selected()
                self.save.toggle_selected()
                self.draw()
            elif event == em.INPUT_EXIT:
                self.destroy()
                return
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.save:
            if event == em.INPUT_ENTER:
                if self.oldname:
                    record_client.removeFavorite(self.oldname)
                (result, msg) = record_client.addEditedFavorite(
                             self.name_input.get_word(), 
                             self.fav.title, 
                             self.fav.channel_id, 
                             self.dow_box.list.get_selected_item().value, 
                             self.tod_box.list.get_selected_item().value, 
                             self.fav.priority)
                if result:
                    tv.view_favorites.ViewFavorites(parent=self.parent, text='Favorites').show()
                    self.destroy()
                else:
                    AlertBox(parent=self, text=_('Failed: %s') % msg)
                return
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.save.toggle_selected()
                self.tod_box.toggle_selected()
                self.draw()
            elif event == em.INPUT_EXIT:
                self.destroy()
                return

        if event == em.INPUT_EXIT:
            self.destroy()
            return
        else:
            return self.parent.eventhandler(event)

