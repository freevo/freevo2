# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, time, copy, re

# Various utilities
import util

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd
import gui
import skin
import ExtendedMenu

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The Electronic Program Guide
import epg_xmltv as epg, epg_types

rc   = rc.get_singleton()   # Create the remote control object
osd  = osd.get_singleton()  # Create the OSD object
skin = skin.get_singleton() # Create the Skin object


CHAN_NO_DATA = 'This channel has no data loaded'


class ExtendedMenu_TV(ExtendedMenu.ExtendedMenu):
    def refresh(self):
        skin.DrawTVGuide()
        self.view.refresh()
        self.info.refresh()
        self.listing.refresh()
        osd.update()


    def clear(self):
        skin.DrawTVGuide()
        # skin.DrawTVGuide_Clear()    XXX This doesn't redraw the logo, can't be right?  /Krister
        

    def eventhandler(self, event):
        if event == rc.MENU:
            if self.view.getVisible() == 1:
                self.view.setVisible(0)
            else:
                self.view.setVisible(1)

            if self.info.getVisible() == 1:
                self.info.setVisible(0)
            else:
                self.info.setVisible(1)

            if skin.DrawTVGuide_getExpand() == 1:
                skin.DrawTVGuide_setExpand(0)
            else:
                skin.DrawTVGuide_setExpand(1)

            self.refresh()
        elif event == rc.REFRESH_SCREEN:
            self.refresh()
        else:
            self.clear()
            t = self.listing.eventhandler(event)
            if t and len(t) == 2:
                to_view, to_info = t
            else:
                to_view = None
                to_info = None
            self.view.ToView(to_view)
            self.info.ToInfo(to_info)
            osd.update()
        return 0
    



class ExtendedMenuView_TV(ExtendedMenu.ExtendedMenuView):
    last_to_view = ''
    
    # Parameters:
    #    - ToView: string with cmd to view
    def ToView(self, to_view):
        self.last_to_view = to_view
        if self.getVisible() == 1:
            skin.DrawTVGuide_View(to_view)

    def refresh(self):
        self.ToView(self.last_to_view)


    
class ExtendedMenuInfo_TV(ExtendedMenu.ExtendedMenuInfo):
    last_to_info = ''
    
    # Parameters:
    #    - ToInfo: string with cmd to info
    def ToInfo(self, to_info):
        self.last_to_info = to_info
        if self.getVisible() == 1:
            skin.DrawTVGuide_Info(to_info)
                             

    def refresh(self):
        self.ToInfo(self.last_to_info)






class ExtendedMenuListing_TV(ExtendedMenu.ExtendedMenuListing):
    n_cols  = 4
    col_time = 30 # each col represents 30 minutes 
    guide = epg.get_guide()
    last_to_listing = [ None, None, None , None ]


    # Parameters:
    #    - to_listing: (start_time, stop_time, prg_start) to listing
    def ToListing(self, to_listing):
        channels = self.guide.GetPrograms(start=to_listing[0]+1, stop=to_listing[1]-1)
        self.last_to_listing = to_listing

        table = [ ]


        # table header
        table += [ ['Chan'] ]
        for i in range(self.n_cols):
            table[0] += [ to_listing[0] + self.col_time * i* 60 ]

        table += [ to_listing[3] ] # the selected program

        found_1stchannel = 0
        if to_listing[2] == None:
            found_1stchannel = 1
            
        flag_selected = 0
        n_items = skin.DrawTVGuide_ItemsPerPage()
        n = 0
        for chan in channels:
            
            if n >= n_items:
                break
            
            if to_listing[2] != None and chan.id == to_listing[2]:
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
                    if to_listing[3]:
                        if chan.programs[i].title == to_listing[3].title and chan.programs[i].start == to_listing[3].start and chan.programs[i].stop == to_listing[3].stop and chan.programs[i].channel_id == to_listing[3].channel_id:
                            self.last_to_listing[3] = chan.programs[i]
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
                            if table[i].programs[j].stop > to_listing[0]:
                                self.last_to_listing[3] = table[i].programs[j]
                                table[1] = table[i].programs[j]
                                flag_selected = 1
                                break


        if self.getVisible() == 1:
            skin.DrawTVGuide_Listing(table)


    def refresh(self):
        self.ToListing(self.last_to_listing)
    

    def eventhandler(self, event):
        if event == rc.UP:
            return self.event_ItemUp()
        elif event == rc.DOWN:
            return self.event_ItemDown()
        elif event == rc.LEFT:
            return self.event_ItemLeft()
        elif event == rc.RIGHT:
            return self.event_ItemRight()
        elif event == rc.REFRESH_SCREEN:
            self.refresh()
        elif event == rc.CHUP:
            return self.event_PageUp()
        elif event == rc.CHDOWN:
            return self.event_PageDown()
        else:
            print 'No action defined to event: "%s"' % (event)
            
        return ( 'NO VIEW', 'NO INFO' )


    def event_ItemRight(self):
        start_time = self.last_to_listing[0]
        stop_time = self.last_to_listing[1]
        start_channel = self.last_to_listing[2]
        last_prg = self.last_to_listing[3]

        if last_prg.stop >= stop_time:
            start_time += (self.col_time * 60)
            stop_time += (self.col_time * 60)
            
        channel = self.guide.chan_dict[last_prg.channel_id]
        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs        
        if programs:
            for i in range(len(programs)):
                if programs[i].title == last_prg.title and programs[i].start == last_prg.start and programs[i].stop == last_prg.stop and programs[i].channel_id == last_prg.channel_id:
                    break

            prg = None
            if i < len(programs) - 1:
                prg = programs[i+1]
            else:
                prg = programs[i]
            to_info = '\tTitle: ' + prg.title + '\n\tDescription: '+prg.desc
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA

        to_view = self.guide.chan_dict[prg.channel_id].displayname

        self.ToListing([ start_time, stop_time, start_channel, prg ])
            
        return ( to_view, to_info )
        




    def event_ItemLeft(self):
        start_time = self.last_to_listing[0]
        stop_time = self.last_to_listing[1]
        start_channel = self.last_to_listing[2]
        last_prg = self.last_to_listing[3]

        if last_prg.start <= start_time:
            start_time -= (self.col_time * 60)
            stop_time -= (self.col_time * 60)
            
        channel = self.guide.chan_dict[last_prg.channel_id]
        programs = self.guide.GetPrograms(start_time+1, stop_time-1, [ channel.id ])
        programs = programs[0].programs        
        if programs:
            for i in range(len(programs)):
                if programs[i].title == last_prg.title and programs[i].start == last_prg.start and programs[i].stop == last_prg.stop and programs[i].channel_id == last_prg.channel_id:
                    break

            prg = None
            if i > 0:
                prg = programs[i-1]
            else:
                prg = programs[i]

            to_info = '\tTitle: ' + prg.title + '\n\tDescription: '+prg.desc
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA
            
        to_view = self.guide.chan_dict[prg.channel_id].displayname

        self.ToListing([ start_time, stop_time, start_channel, prg ])
            
        return ( to_view, to_info )

        
    def event_ItemDown(self):
        start_time = self.last_to_listing[0]
        stop_time = self.last_to_listing[1]
        start_channel = self.last_to_listing[2]
        last_prg = self.last_to_listing[3]

        n_items = skin.DrawTVGuide_ItemsPerPage()
        n = 1
        flag_start_channel = 0
        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == start_channel:
                flag_start_channel = 1                                        
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break
            if flag_start_channel == 1:
                n += 1

        if n >= n_items and (i-n_items+2) < len(self.guide.chan_list):
            start_channel = self.guide.chan_list[i-n_items+2].id
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
            to_info = '\tTitle: ' + prg.title + '\n\tDescription: '+prg.desc
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA

        to_view = channel.displayname


        self.ToListing([ start_time, stop_time, start_channel, prg ])
            
        return ( to_view, to_info )





    def event_ItemUp(self):
        start_time = self.last_to_listing[0]
        stop_time = self.last_to_listing[1]
        start_channel = self.last_to_listing[2]
        last_prg = self.last_to_listing[3]

        if last_prg == None:
            last_prg = epg_types.TvProgram()

        n_items = skin.DrawTVGuide_ItemsPerPage()
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
            to_info = '\tTitle: ' + prg.title + '\n\tDescription: '+prg.desc
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = 'This channel has no data loaded'
            prg.desc = ''
            to_info = 'This channel has no data loaded'

            
        to_view = channel.displayname

        self.ToListing([ start_time, stop_time, start_channel, prg ])
            
        return ( to_view, to_info )


    def event_PageUp(self):
        start_time = self.last_to_listing[0]
        stop_time = self.last_to_listing[1]
        start_channel = self.last_to_listing[2]
        last_prg = self.last_to_listing[3]

        n_items = skin.DrawTVGuide_ItemsPerPage()
        for i in range(len(self.guide.chan_list)):
            if self.guide.chan_list[i].id == last_prg.channel_id:
                break


        channel = None
        if i-n_items > 0:
            channel = self.guide.chan_list[i-n_items]
            start_channel = self.guide.chan_list[i-n_items].id
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
            to_info = '\tTitle: ' + prg.title + '\n\tDescription: '+prg.desc
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA

        to_view = channel.displayname


        self.ToListing([ start_time, stop_time, start_channel, prg ])
            
        return ( to_view, to_info )
        






    def event_PageDown(self):
        start_time = self.last_to_listing[0]
        stop_time = self.last_to_listing[1]
        start_channel = self.last_to_listing[2]
        last_prg = self.last_to_listing[3]

        n_items = skin.DrawTVGuide_ItemsPerPage()
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
        if i+n_items < len(self.guide.chan_list):
            channel = self.guide.chan_list[i+n_items]
            start_channel = self.guide.chan_list[i+n_items].id
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
            to_info = '\tTitle: ' + prg.title + '\n\tDescription: '+prg.desc
        else:
            prg = epg_types.TvProgram()
            prg.channel_id = channel.id            
            prg.start = 0
            prg.stop = 2147483647   # Year 2038
            prg.title = CHAN_NO_DATA
            prg.desc = ''
            to_info = CHAN_NO_DATA

        to_view = channel.displayname


        self.ToListing([ start_time, stop_time, start_channel, prg ])
            
        return ( to_view, to_info )
