# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# tvguide.py - This is the Freevo TV Guide module. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.38  2004/07/22 21:21:49  dischi
# small fixes to fit the new gui code
#
# Revision 1.37  2004/07/11 13:53:52  dischi
# do not change menu start/stop times for CHAN_NO_DATA
#
# Revision 1.36  2004/07/11 11:46:03  dischi
# decrease record server calling
#
# Revision 1.35  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.34  2004/06/28 15:56:42  dischi
# fix off by one error on scrolling down
#
# Revision 1.33  2004/06/20 14:07:58  dischi
# remove upsoon on changes
#
# Revision 1.32  2004/06/20 12:40:07  dischi
# better handling of very long programs
#
# Revision 1.31  2004/06/13 00:28:19  outlyer
# Fix a crash.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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


import os
import time

import config
import rc
import util

from gui import PopupBox
from gui import AlertBox

import skin
from event import *

# The Electronic Program Guide
import epg_xmltv, epg_types

from item import Item
from program_display import ProgramItem
import record_client as ri

skin = skin.get_singleton()
skin.register('tv', ('screen', 'title', 'subtitle', 'view', 'tvlisting', 'info', 'plugin'))

CHAN_NO_DATA = _('This channel has no data loaded')

class TVGuide(Item):
    def __init__(self, start_time, player, menuw):
        Item.__init__(self)

        self.n_items, hours_per_page = skin.items_per_page(('tv', self))
        stop_time = start_time + hours_per_page * 60 * 60

        guide = epg_xmltv.get_guide(PopupBox(text=_('Preparing the program guide')))
        channels = guide.GetPrograms(start=start_time+1, stop=stop_time-1)
        if not channels:
            AlertBox(text=_('TV Guide is corrupt!')).show()
            return

        selected = None
        for chan in channels:
            if chan.programs:
                selected = chan.programs[0]
                break

        self.col_time = 30 # each col represents 30 minutes 
        self.n_cols  = (stop_time - start_time) / 60 / self.col_time
        self.player = player

        self.type = 'tv'
        self.menuw = menuw
        self.visible = True
        self.select_time = start_time
        self.last_update = 0
        
        self.update_schedules(force=True)

        self.rebuild(start_time, stop_time, guide.chan_list[0].id, selected)
        self.event_context = 'tvmenu'
        menuw.pushmenu(self)


    def update_schedules(self, force=False):
        if not force and self.last_update + 60 > time.time():
            return

        # less than one second? Do not belive the force update
        if self.last_update + 1 > time.time():
            return

        upsoon = '%s/upsoon' % (config.FREEVO_CACHEDIR)
        if os.path.isfile(upsoon):
            os.unlink(upsoon)
            
        _debug_('update schedule')
        self.last_update = time.time()
        self.scheduled_programs = []
        (got_schedule, schedule) = ri.getScheduledRecordings()

        util.misc.comingup(None, (got_schedule, schedule))

        if got_schedule:
            l = schedule.getProgramList()
            for k in l:
                self.scheduled_programs.append(l[k].encode())

        
    def eventhandler(self, event):
        _debug_('TVGUIDE EVENT is %s' % event, 2)

        if event == MENU_CHANGE_STYLE:
            if skin.toggle_display_style('tv'):
                start_time    = self.start_time
                stop_time     = self.stop_time
                start_channel = self.start_channel
                selected      = self.selected

                self.n_items, hours_per_page = skin.items_per_page(('tv', self))

                before = -1
                after  = -1
                for c in self.guide.chan_list:
                    if before >= 0 and after == -1:
                        before += 1
                    if after >= 0:
                        after += 1
                    if c.id == start_channel:
                        before = 0
                    if c.id == selected.channel_id:
                        after = 0
                    
                if self.n_items <= before:
                    start_channel = selected.channel_id

                if after < self.n_items:
                    up = min(self.n_items -after, len(self.guide.chan_list)) - 1
                    for i in range(len(self.guide.chan_list) - up):
                        if self.guide.chan_list[i+up].id == start_channel:
                            start_channel = self.guide.chan_list[i].id
                            break
                    
                stop_time = start_time + hours_per_page * 60 * 60

                self.n_cols  = (stop_time - start_time) / 60 / self.col_time
                self.rebuild(start_time, stop_time, start_channel, selected)
                self.menuw.refresh()
            
        if event == MENU_UP:
            self.event_change_channel(-1)
            self.menuw.refresh()

        elif event == MENU_DOWN:
            self.event_change_channel(1)
            self.menuw.refresh()

        elif event == MENU_LEFT:
            self.event_change_program(-1)
            self.menuw.refresh()

        elif event == MENU_RIGHT:
            self.event_change_program(1)
            self.menuw.refresh()

        elif event == MENU_PAGEUP:
            self.event_change_channel(-self.n_items)
            self.menuw.refresh()

        elif event == MENU_PAGEDOWN:
            self.event_change_channel(self.n_items)
            self.menuw.refresh()

        elif event == MENU_SUBMENU:
            
            pass

        elif event == TV_START_RECORDING:
            self.event_RECORD()
            self.menuw.refresh()
 
        elif event == MENU_SELECT or event == PLAY:
            tvlockfile = config.FREEVO_CACHEDIR + '/record'

            # jlaska -- START
            # Check if the selected program is >7 min in the future
            # if so, bring up the record dialog
            now = time.time() + (7*60)
            if self.selected.start > now:
                self.event_RECORD()
            # jlaska -- END
            elif os.path.exists(tvlockfile):
                # XXX: In the future add the options to watch what we are
                #      recording or cencel it and watch TV.
                AlertBox(text=_('Sorry, you cannot watch TV while recording. ')+ \
                              _('If this is not true then remove ') + \
                              tvlockfile + '.', height=200).show()
                return TRUE
            else:
                self.hide()
                self.player('tv', self.selected.channel_id)
        
        elif event == PLAY_END:
            self.show()

        else:
            return FALSE

        return TRUE


    def show(self):
        if not self.visible:
            self.visible = 1
            self.refresh()

            
    def hide(self):
        if self.visible:
            self.visible = 0
            skin.clear()
        

    def refresh(self):
        self.update_schedules(force=True)
        if not self.menuw.children:
            rc.set_context(self.event_context)
            self.menuw.refresh()


    def rebuild(self, start_time, stop_time, start_channel, selected):

        self.guide = epg_xmltv.get_guide()
        channels = self.guide.GetPrograms(start=start_time+1, stop=stop_time-1)

        table = [ ]
        self.update_schedules()

        self.start_time    = start_time
        self.stop_time     = stop_time
        self.start_channel = start_channel
        self.selected      = selected

        self.display_up_arrow   = FALSE
        self.display_down_arrow = FALSE

        # table header
        table += [ ['Chan'] ]
        for i in range(int(self.n_cols)):
            table[0] += [ start_time + self.col_time * i* 60 ]

        table += [ self.selected ] # the selected program

        found_1stchannel = 0
        if stop_time == None:
            found_1stchannel = 1
            
        flag_selected = 0

        n = 0
        for chan in channels:
            if n >= self.n_items:
                self.display_down_arrow = TRUE
                break
            
            if start_channel != None and chan.id == start_channel:
                found_1stchannel = 1            

            if not found_1stchannel:
                self.display_up_arrow = TRUE
                
            if found_1stchannel:
                if not chan.programs:
                    prg = epg_types.TvProgram()
                    prg.channel_id = chan.id
                    prg.start = 0
                    prg.stop = 2147483647   # Year 2038
                    prg.title = CHAN_NO_DATA
                    prg.desc = ''
                    chan.programs = [ prg ]

                    
                for i in range(len(chan.programs)):
                    if selected:
                        if chan.programs[i] == selected:
                            flag_selected = 1
                                
                table += [  chan  ]
                n += 1

        if flag_selected == 0:
            for i in range(2, len(table)):
                if flag_selected == 1:
                    break
                else:
                    if table[i].programs:
                        for j in range(len(table[i].programs)):
                            if table[i].programs[j].stop > start_time:
                                self.selected = table[i].programs[j]
                                table[1] = table[i].programs[j]
                                flag_selected = 1
                                break

        self.table = table
        for t in table:
            try:
                for p in t.programs:
                    if p in self.scheduled_programs:
                        p.scheduled = TRUE # DO NOT change this to 'True' Twisted
                                           # does not support boolean objects and 
                                           # it will break under Python 2.3
                    else:
                        p.scheduled = FALSE # Same as above; leave as 'FALSE' until
                                            # Twisted includes Boolean
            except:
                pass


    def event_RECORD(self):
        if self.selected.scheduled:
            pi = ProgramItem(self, prog=self.selected, context='schedule')
        else:
            pi = ProgramItem(self, prog=self.selected, context='guide')
        pi.display_program(menuw=self.menuw)


    def event_change_program(self, value, full_scan=False):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        channel = self.guide.chan_dict[last_prg.channel_id]
        if full_scan:
            all_programs = self.guide.GetPrograms(start_time-24*60*60, stop_time+24*60*60,
                                                  [ channel.id ])
        else:
            all_programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])

        # Current channel programs
        programs = all_programs[0].programs
        if programs:
            for i in range(len(programs)):
                if programs[i].title == last_prg.title and \
                   programs[i].start == last_prg.start and \
                   programs[i].stop == last_prg.stop and \
                   programs[i].channel_id == last_prg.channel_id:
                    break

            prg = None

            if value > 0:
                if i + value < len(programs):
                    prg = programs[i+value]
                elif full_scan:
                    prg = programs[-1]
                else:
                    return self.event_change_program(value, True)
            else:
                if i+value >= 0:
                    prg = programs[i+value]
                elif full_scan:
                    prg = programs[0]
                else:
                    return self.event_change_program(value, True)

            if prg.sub_title:
                procdesc = '"' + prg.sub_title + '"\n' + prg.desc
            else:
                procdesc = prg.desc
            to_info = (prg.title, procdesc)
            self.select_time = prg.start

            # set new (better) start / stop times
            extra_space = 0
            if prg.stop - prg.start > self.col_time * 60:
                extra_space = self.col_time * 60

            while prg.start + extra_space >= stop_time:
                start_time += (self.col_time * 60)
                stop_time += (self.col_time * 60)

            while prg.start + extra_space <= start_time:
                start_time -= (self.col_time * 60)
                stop_time -= (self.col_time * 60)


        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA

        self.rebuild(start_time, stop_time, start_channel, prg)

        
    def event_change_channel(self, value):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == start_channel:
                start_pos = i                                        
                end_pos   = i + self.n_items
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break

        channel_pos = min(len(self.guide.chan_list)-1, max(0, i+value))

        # calc real changed value
        value = channel_pos - i
        
        if value < 0 and channel_pos and channel_pos <= start_pos:
            # move start channel up
            start_channel = self.guide.chan_list[start_pos + value].id

        if value > 0 and channel_pos < len(self.guide.chan_list)-1 and \
               channel_pos + 1 >= end_pos:
            # move start channel down
            start_channel = self.guide.chan_list[start_pos + value].id
            
        channel = self.guide.chan_list[channel_pos]

        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs


        prg = None
        if programs and len(programs) > 0:
            for i in range(len(programs)):
                if programs[i].stop > self.select_time and programs[i].stop > start_time:
                    break

                
            prg = programs[i]
            if prg.sub_title:
                procdesc = '"' + prg.sub_title + '"\n' + prg.desc
            else:
                procdesc = prg.desc
            
            to_info = (prg.title, procdesc)
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA

        self.rebuild(start_time, stop_time, start_channel, prg)
