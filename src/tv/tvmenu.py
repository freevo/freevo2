# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys
import os
import time
import copy

# Various utilities
import util

import gui
import skin

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The Electronic Program Guide
import epg_xmltv as epg, epg_types

import record_video

rc   = rc.get_singleton()   # Create the remote control object
skin = skin.get_singleton() # Create the Skin object



DEBUG = config.DEBUG

CHAN_NO_DATA = 'This channel has no data loaded'


class TVmenu:
    def __init__(self):
        self.n_cols  = 4
        self.col_time = 30 # each col represents 30 minutes 
        self.all_channels = epg.get_guide().chan_list
        self.n_items = skin.DrawTVGuide_ItemsPerPage(self)


    def eventhandler(self, event):
        if hasattr(self, 'event_%s' % event):
            eval('self.event_%s()' % event)
        elif event == rc.CHUP:
            self.event_PageUp()
        elif event == rc.CHDOWN:
            self.event_PageDown()

        elif event == rc.REC:
            record_video.main_menu(self.selected)

        else:
            print 'No action defined to event: "%s"' % (event)
            return None


    def refresh(self):
        skin.DrawTVGuide(self)


    def rebuild(self, start_time, stop_time, start_channel, selected):

        self.guide = epg.get_guide()
        channels = self.guide.GetPrograms(start=start_time+1, stop=stop_time-1)

        table = [ ]

        self.start_time    = start_time
        self.stop_time     = stop_time
        self.start_channel = start_channel
        self.selected      = selected

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
                break
            
            if start_channel != None and chan.id == start_channel:
                found_1stchannel = 1            

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
        skin.DrawTVGuide(self)



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

        if n >= self.n_items and (i-self.n_items+2) < len(self.guide.chan_list):
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
