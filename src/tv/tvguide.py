#if 0 /*
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
# Revision 1.12  2003/08/25 18:44:32  dischi
# Moved HOURS_PER_PAGE into the skin fxd file, default=2
#
# Revision 1.11  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.10  2003/08/22 05:59:35  gsbarbieri
# Fixed some mistakes.
# Now it's possible to have more than one line for program/label, just make
# the height fit the number of wanted lines.
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
#endif


import gui.GUIObject
import skin
import event as em
import config


# The Electronic Program Guide
import epg_xmltv as epg, epg_types

import record_video

from gui.PopupBox import PopupBox
from gui.AlertBox import AlertBox

skin = skin.get_singleton() # Create the Skin object


TRUE = 1
FALSE = 0


CHAN_NO_DATA = 'This channel has no data loaded'


class TVGuide(gui.GUIObject):
    def __init__(self, start_time, player, menuw):
        gui.GUIObject.__init__(self)

        self.n_items, hours_per_page = skin.items_per_page(('tv', self))
        stop_time = start_time + hours_per_page * 60 * 60

        guide = epg.get_guide(PopupBox(text='Preparing the program guide'))
        channels = guide.GetPrograms(start=start_time+1, stop=stop_time-1)

        if not channels:
            AlertBox(text='TV Guide is corrupt!').show()
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

        self.rebuild(start_time, stop_time, guide.chan_list[0].id, selected)
        menuw.pushmenu(self)


    def eventhandler(self, event):
        if hasattr(self, 'event_%s' % event):
            eval('self.event_%s()' % event)
            self.menuw.refresh()
            
        elif event == em.MENU_UP:
            self.event_UP()
            self.menuw.refresh()

        elif event == em.MENU_DOWN:
            self.event_DOWN()
            self.menuw.refresh()

        elif event == em.MENU_LEFT:
            self.event_LEFT()
            self.menuw.refresh()

        elif event == em.MENU_RIGHT:
            self.event_RIGHT()
            self.menuw.refresh()

        elif event == em.MENU_PAGEUP:
            self.event_PageUp()
            self.menuw.refresh()

        elif event == em.MENU_PAGEDOWN:
            self.event_PageDown()
            self.menuw.refresh()

        elif event == em.TV_START_RECORDING:
            record_video.main_menu(self.selected)

        elif event == em.MENU_SELECT or event == em.PLAY:
            self.hide()
            self.player('tv', self.selected.channel_id)
        
        elif event == em.PLAY_END:
            self.show()

        else:
            return FALSE

        return TRUE


    def show(self):
        if not self.visible:
            self.visible = 1
            self.menuw.refresh()

            
    def hide(self):
        if self.visible:
            self.visible = 0
            skin.clear()
        

    def refresh(self):
        self.menuw.refresh()


    def rebuild(self, start_time, stop_time, start_channel, selected):

        self.guide = epg.get_guide()
        channels = self.guide.GetPrograms(start=start_time+1, stop=stop_time-1)

        table = [ ]

        self.start_time    = start_time
        self.stop_time     = stop_time
        self.start_channel = start_channel
        self.selected      = selected

        self.display_up_arrow   = FALSE
        self.display_down_arrow = FALSE


        # table header
        table += [ ['Chan'] ]
        for i in range(self.n_cols):
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



    def event_RIGHT(self):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        if last_prg.stop >= stop_time:
            start_time += (self.col_time * 60)
            stop_time += (self.col_time * 60)
            
        channel = self.guide.chan_dict[last_prg.channel_id]
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
            if i < len(programs) - 1:
                prg = programs[i+1]
            else:
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
        


    def event_LEFT(self):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        if last_prg.start <= start_time:
            start_time -= (self.col_time * 60)
            stop_time -= (self.col_time * 60)
            
        channel = self.guide.chan_dict[last_prg.channel_id]
        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs        
        if programs:
            for i in range(len(programs)):
                if programs[i].title == last_prg.title and \
                   programs[i].start == last_prg.start and \
                   programs[i].stop == last_prg.stop and \
                   programs[i].channel_id == last_prg.channel_id:
                    break

            prg = None
            if i > 0:
                prg = programs[i-1]
            else:
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

        
    def event_DOWN(self):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        n = 1
        flag_start_channel = 0
        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == start_channel:
                flag_start_channel = 1                                        
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break
            if flag_start_channel == 1:
                n += 1

        if n >= self.n_items and (i-self.n_items+2) < len(self.guide.chan_list) and \
               (i-self.n_items+1 + self.n_items) < len( self.guide.chan_list ):
            start_channel = self.guide.chan_list[i-self.n_items+2].id
        else:
            channel = self.guide.chan_list[i]

        channel = None
        if i < len(self.guide.chan_list) - 1:
            channel = self.guide.chan_list[i+1]
        else:
            channel = self.guide.chan_list[i]


        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs


        prg = None
        if programs and len(programs) > 0:
            for i in range(len(programs)):
                if programs[i].stop > last_prg.start and programs[i].stop > start_time:
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





    def event_UP(self):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        if last_prg == None:
            last_prg = epg_types.TvProgram()

        n = 0
        flag_start_channel = 0
        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == start_channel:
                flag_start_channel = 1
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break
            if flag_start_channel == 1:
                n += 1


        channel = None
        if i > 0:
            channel = self.guide.chan_list[i-1]
            if n == 0:
                start_channel = self.guide.chan_list[i-1].id
                
        else:
            channel = self.guide.chan_list[i]


        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs

        if programs and len(programs) > 0:
            for i in range(len(programs)):
                if programs[i].stop > last_prg.start and programs[i].stop > start_time:
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
            prg.title = 'This channel has no data loaded'
            prg.desc = ''
            to_info = 'This channel has no data loaded'

            
        self.rebuild(start_time, stop_time, start_channel, prg)


    def event_PageUp(self):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break


        channel = None
        if i-self.n_items > 0:
            channel = self.guide.chan_list[i-self.n_items]
            start_channel = self.guide.chan_list[i-self.n_items].id
        else:
            channel = self.guide.chan_list[0]
            start_channel = self.guide.chan_list[0].id


        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs


        prg = None
        if programs and len(programs) > 0:
            for i in range(len(programs)):
                if programs[i].stop > last_prg.start and programs[i].stop > start_time:
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





    def event_PageDown(self):
        start_time    = self.start_time
        stop_time     = self.stop_time
        start_channel = self.start_channel
        last_prg      = self.selected

        n = 1
        flag_start_channel = 0
        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == start_channel:
                flag_start_channel = 1                                        
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break
            if flag_start_channel == 1:
                n += 1

        channel = None
        if i+self.n_items < len(self.guide.chan_list):
            channel = self.guide.chan_list[i+self.n_items]
            start_channel = self.guide.chan_list[i+self.n_items].id
        else:
            channel = self.guide.chan_list[i]
            start_channel = self.guide.chan_list[i].id


        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs

        prg = None
        if programs and len(programs) > 0:
            for i in range(len(programs)):
                if programs[i].stop > last_prg.start and programs[i].stop > start_time:
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
