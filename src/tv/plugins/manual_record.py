#!/usr/bin/env python
#-----------------------------------------------------------------------
# ManualRecord - 
#-----------------------------------------------------------------------
# $Id$
#
# Todo: 
# Notes: 
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/02/18 23:57:05  mikeruelle
# reflect dischi's changes
#
# Revision 1.1  2004/02/13 05:13:09  mikeruelle
# first shot, it works, but is slow to show.
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

from time import localtime, strftime, time, mktime, gmtime
import sys

import config
import plugin

import tv.record_client as record_client
import event as em

import tv.record_types
from tv.epg_types import TvProgram
import menu
from gui.GUIObject      import *
from gui.Border         import *
from gui.Label          import *
from gui.AlertBox       import *
from gui.OptionBox      import *
from gui.LetterBoxGroup import *
from gui.ConfirmBox     import ConfirmBox

# Use the alternate strptime module which seems to handle time zones
#
# XXX Remove when we are ready to require Python 2.3
if float(sys.version[0:3]) < 2.3:
    import tv.strptime as strptime
else:
    import _strptime as strptime

DEBUG = config.DEBUG
TRUE = 1
FALSE = 0

# maxinum number of days we can record
MAXDAYS = 7

# minimum amount of time it would take record_server.py to pick us up in seconds
# by default it is one minute plus a few seconds just in case
MINPICKUP = 70

class PluginInterface(plugin.Plugin):
    """
    """
    def __init__(self):
        """
        normal plugin init, but sets _type to 'mplayer_video'
        """
        plugin.Plugin.__init__(self)
        self._type = 'mainmenu_tv'
	self.parent = None

    def items(self, parent):
        self.parent = parent
        return [menu.MenuItem('Manual Record', action=self.show_manual_record)]

    def show_manual_record(self, menuw=None, arg=None):
        ManualRecord(parent=self.parent).show()

class ManualRecord(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    context   Context in which the object is instanciated
    """
    
    def __init__(self, parent=None, left=None, top=None, width=500, height=350):
        self.errormsg = ''
        PopupBox.__init__(self, text=_('Manual Record'), x=left, y=top, 
	                  width=width, height=height)

        self.v_spacing = 15
        self.h_margin = 20
        self.v_margin = 20

        self.internal_h_align = Align.LEFT

        if not self.left:     self.left   = self.osd.width/2 - self.width/2
        if not self.top:      self.top    = self.osd.height/2 - self.height/2

        # check the record server and see if up
        (self.server_available, msg) = record_client.connectionTest()
        if not self.server_available:
            errormsg = Label(_('Record server unavailable: %s') % msg,
                             self, Align.CENTER)
            return

        name = Label(_('Name:'), self, Align.LEFT)
        self.name_input = LetterBoxGroup(text='Test')
        self.name_input.h_align = Align.NONE
        self.add_child(self.name_input)

        chan = Label(_('Channel:'), self, Align.LEFT)

        self.chan_box = OptionBox('ANY')
        self.chan_box.h_align = Align.NONE
        i = 1
        chan_index = 0
        guide = tv.epg_xmltv.get_guide()
        for ch in guide.chan_list:
            i += 1
            self.chan_box.add_item(text=ch.displayname, value=ch.id)
        self.chan_box.toggle_selected_index(chan_index)
        self.chan_box.change_item(None)
        self.add_child(self.chan_box)

        # date 1
        toda1 = Label(_('Start Day:'), self, Align.LEFT)
	#month box
        self.todm_box1 = OptionBox('ANY')
        self.todm_box1.h_align = Align.NONE
	todm_index1 = 0
        mymonths = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
        for m in range(0, 12):
            self.todm_box1.add_item(text=mymonths[m], value=m+1)
        self.todm_box1.toggle_selected_index(todm_index1)
        self.todm_box1.change_item(None)
        self.add_child(self.todm_box1)
	#date box
        self.todd_box1 = OptionBox('ANY')
        self.todd_box1.h_align = Align.NONE
	todd_index1 = 0
        for m in range(1, 32):
            self.todd_box1.add_item(text=str(m), value=m)
        self.todd_box1.toggle_selected_index(todd_index1)
        self.todd_box1.change_item(None)
        self.add_child(self.todd_box1)

        # time 1
        tod1 = Label(_('Start Time:'), self, Align.LEFT)
        self.tod_box1 = OptionBox('ANY')
        self.tod_box1.h_align = Align.NONE

	tod_index1 = 0
        for h in range(0,24):
            for m in range(0,60,5):
                text = "%.2d:%.2d" % (h, m)
                self.tod_box1.add_item(text=text, value=text)
        self.tod_box1.toggle_selected_index(tod_index1)
        # This is a hack for setting the OptionBox's label to the current
        # value. It should be done by OptionBox when drawing, but it doesn't
        # work :(
        self.tod_box1.change_item(None)
        self.add_child(self.tod_box1)

        # date 2
        toda2 = Label(_('Stop Day:'), self, Align.LEFT)
	#month box
        self.todm_box2 = OptionBox('ANY')
        self.todm_box2.h_align = Align.NONE
	todm_index2 = 0
        for m in range(0, 12):
            self.todm_box2.add_item(text=mymonths[m], value=m+1)
        self.todm_box2.toggle_selected_index(todm_index2)
        self.todm_box2.change_item(None)
        self.add_child(self.todm_box2)
	#date box
        self.todd_box2 = OptionBox('ANY')
        self.todd_box2.h_align = Align.NONE
	todd_index2 = 0
        for m in range(1, 32):
            self.todd_box2.add_item(text=str(m), value=m)
        self.todd_box2.toggle_selected_index(todd_index2)
        self.todd_box2.change_item(None)
        self.add_child(self.todd_box2)


        # time 2
        tod2 = Label(_('End Time:'), self, Align.LEFT)
        self.tod_box2 = OptionBox('ANY')
        self.tod_box2.h_align = Align.NONE

        i = 0
	tod_index2 = 0
        for h in range(0,24):
            for m in range(0,60,10):
                text = "%.2d:%.2d" % (h, m)
                self.tod_box2.add_item(text=text, value=text)
        self.tod_box2.toggle_selected_index(tod_index2)
        # This is a hack for setting the OptionBox's label to the current
        # value. It should be done by OptionBox when drawing, but it doesn't
        # work :(
        self.tod_box2.change_item(None)
        self.add_child(self.tod_box2)

        self.save = Button(_('Save'))
        self.add_child(self.save)
        self.cancel = Button(_('CANCEL'))
        self.add_child(self.cancel)


    def eventhandler(self, event, menuw=None):
        #print 'SELECTED CHILD: %s' % self.get_selected_child()
        #this if here so we don't crash when no record_server
        if event == em.INPUT_EXIT:
            self.destroy()
            return
        elif self.get_selected_child() == self.name_input:
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

        elif self.get_selected_child() == self.chan_box:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.chan_box.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.chan_box.selected or self.chan_box.list.is_visible():
                    #if DEBUG: print '  Want to toggle_box'
                    self.chan_box.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.chan_box.toggle_selected()
                self.name_input.boxes[0].toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.chan_box.toggle_selected()
                self.todm_box1.toggle_selected()
                self.draw()
            elif event == em.INPUT_EXIT:
                self.destroy()
                return
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.todm_box1:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.todm_box1.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.todm_box1.selected or self.todm_box1.list.is_visible():
                    self.todm_box1.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.todm_box1.toggle_selected()
                self.chan_box.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.todm_box1.toggle_selected()
                self.todd_box1.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.todd_box1:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.todd_box1.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.todd_box1.selected or self.todd_box1.list.is_visible():
                    self.todd_box1.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.todd_box1.toggle_selected()
                self.todm_box1.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.todd_box1.toggle_selected()
                self.tod_box1.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.tod_box1:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.tod_box1.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.tod_box1.selected or self.tod_box1.list.is_visible():
                    self.tod_box1.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.tod_box1.toggle_selected()
                self.todd_box1.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.tod_box1.toggle_selected()
                self.todm_box2.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return
#
        elif self.get_selected_child() == self.todm_box2:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.todm_box2.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.todm_box2.selected or self.todm_box2.list.is_visible():
                    self.todm_box2.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.todm_box2.toggle_selected()
                self.tod_box1.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.todm_box2.toggle_selected()
                self.todd_box2.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.todd_box2:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.todd_box2.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.todd_box2.selected or self.todd_box2.list.is_visible():
                    self.todd_box2.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.todd_box2.toggle_selected()
                self.todm_box2.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.todd_box2.toggle_selected()
                self.tod_box2.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.tod_box2:
            if event in (em.INPUT_UP, em.INPUT_DOWN):
                self.tod_box2.change_item(event)
                self.draw()
            elif event == em.INPUT_ENTER:
                if self.tod_box2.selected or self.tod_box2.list.is_visible():
                    self.tod_box2.toggle_box()
                    self.draw()
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.tod_box2.toggle_selected()
                self.todd_box2.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.tod_box2.toggle_selected()
                self.save.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return

#
        elif self.get_selected_child() == self.save:
            if event == em.INPUT_ENTER:
                # schedule the recording here
                prog = self.make_prog()
                if prog:
                    self.schedule_recording(prog)
                else:
                    AlertBox(parent=self, text=_('Failed: %s') % self.errormsg).show()
                return
            elif event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.save.toggle_selected()
                self.tod_box2.toggle_selected()
                self.draw()
            elif event in (em.INPUT_RIGHT, em.MENU_PAGEDOWN):
                self.save.toggle_selected()
                self.cancel.toggle_selected()
                self.draw()
            self.osd.update(self.get_rect())
            return

        elif self.get_selected_child() == self.cancel:
            if event in (em.INPUT_LEFT, em.MENU_PAGEUP):
                self.save.toggle_selected()
                self.cancel.toggle_selected()
                self.draw()
            elif event == em.INPUT_ENTER:
                self.destroy()
                return
            self.osd.update(self.get_rect())
            return
        else:
            return self.parent.eventhandler(event)

    def make_prog(self):
        prog = None
        curtime_epoch = time()
        curtime = localtime(curtime_epoch)
        chan = self.chan_box.list.get_selected_item().value
        startmonth = self.todm_box1.list.get_selected_item().value
        startday = self.todd_box1.list.get_selected_item().value
        starthm = self.tod_box1.list.get_selected_item().value
        startyear = curtime[0] 
        stopmonth = self.todm_box2.list.get_selected_item().value
        stopday = self.todd_box2.list.get_selected_item().value
        stophm = self.tod_box2.list.get_selected_item().value
        stopyear = curtime[0] 
        currentmonth = curtime[1] 
        title = self.name_input.get_word()
        
        # handle the year wraparound
        if int(stopmonth) < currentmonth:
            stopyear = str(int(stopyear) + 1)
        if int(startmonth) < currentmonth:
            startyear = str(int(startyear) + 1)
        # create utc second start time
        starttime = mktime(strptime.strptime(str(startmonth)+" "+str(startday)+" "+str(startyear)+" "+str(starthm)+":00",'%m %d %Y %H:%M:%S'))
        # create utc stop time
        stoptime = mktime(strptime.strptime(str(stopmonth)+" "+str(stopday)+" "+str(stopyear)+" "+str(stophm)+":00",'%m %d %Y %H:%M:%S'))

        # so we don't record for more then maxdays (maxdays day * 24hr/day * 60 min/hr * 60 sec/min)
        if abs(stoptime - starttime) < (MAXDAYS * 86400): 
            if starttime < stoptime:
                if stoptime < curtime_epoch + MINPICKUP:
                    self.errormsg = "Sorry, the stop time does not give enough time for cron to pickup the change.  Please set it to record for a few minutes longer."
                else:
                    # assign attributes to object
                    prog = TvProgram()
                    prog.channel_id = chan
                    if title:
                        prog.title = title
                    else:
                        prog.title = "Manual Recorded"
                    prog.start = starttime
                    prog.stop = stoptime
            else:
                self.errormsg = "start time is not before stop time." 
        else:
            self.errormsg = "Program would record for more than " + str(MAXDAYS) + " day(s)!"
        return prog

    def schedule_recording(self,prog):
        (result, msg) = record_client.scheduleRecording(prog)
        if result:
            self.destroy()
            AlertBox(parent='osd', text=_('%s has been scheduled') % self.name_input.get_word()).show()
        else:
            AlertBox(parent=self, text=_('Failed: %s') % msg).show()
