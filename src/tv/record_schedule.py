#if 0 /*
# -----------------------------------------------------------------------
# record_schedule.py - Recording Schedule Menu
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is the menu routine which can be accessed by pressing DISPLAY from 
# the record_video menu.  It allows you to view scheduled recordings and to delete
# a scheduled item.  It also displays a message if an item is currently recording.
# For now when you access the view scheduled recordings menu the program systemat
# ically deletes all old items from the file /tmp/freevo_record.lst.  When you 
# delete an item that is currently recording, all recordings are stopped by killing
# all mencoder processes and the item is deleted from the file
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/09/13 10:08:23  dischi
# i18n support
#
# Revision 1.8  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
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

import os
import time
import string

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# The menu widget class
import menu

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The TV application
import tv

# Recording daemon
import record_daemon
import record_video

from gui.AlertBox import AlertBox

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

from item import Item

menuwidget = menu.get_singleton()

killflag = 0

class ScheduleEdit(Item):

    def __init__ (self):
        Item.__init__(self)
        self.type = 'tv'
   

    def main_menu(self):
        recmenu = self.generate_main()
    
        menuwidget.pushmenu(recmenu)
        menuwidget.refresh()
    
    
    def generate_main(self):
        items = []
        items += [menu.MenuItem(_('View Recording Schedule'),
                                self.view_schedule,0)]
        items += [menu.MenuItem(_('Delete Scheduled Item'),
                                self.view_schedule,1)]
        recmenu = menu.Menu(_('RECORDING SCHEDULE'), items,
                             reload_func=self.generate_main, item_types = 'tv')
        rc.app(None)
        return recmenu
    
    
    def view_schedule(self,arg=None, menuw=None):
        '''Set up the view recording menu or the delete scheduled
        item menu'''
    
        items = []
        line = '0'
        itemcount = 0
        global killflag
   
        if not os.path.isfile(record_daemon.SCHEDULE):
            return None
                
        fd = open(record_daemon.SCHEDULE,'r')
    
        #delete old scheduled items from the file since we wont need them
        #this could be done more efficiently from record_daemon
        if arg == 0:
            newstringlist = fd.readline()
            oldchecker = fd.readlines()
    	    fd.close()
            fd = open(record_daemon.SCHEDULE,'w')
    
            for st in oldchecker:
                #check if item is recording
                timecomp= st[st.find('-'): st.rfind(',')].split(',')
    	        timecomp[0] = timecomp[0].replace('-','').replace(':','').replace(' ','')
    	        length = string.atoi(timecomp[1])
                currenttime = string.atoi(time.strftime('%m%d%H%M%S', time.localtime()))
    	        recording = currenttime < self.addtime(string.atoi(timecomp[0]),length)
    
    	        #delete old items that are not recording
    	        if st.find('#') == -1 or (recording and killflag != 1):
    	            newstringlist += st
    	    killflag = 0
            fd.write(newstringlist)
            fd.close()
    	    fd = open(record_daemon.SCHEDULE,'r')
    
        fd.readline()
    
        while line != '':
            oldline = line
    	    line = fd.readline()
    	    if line.find('#') != -1:
    	        recordingflag = 1
    	    else:
    	        recordingflag = 0
    
    	    #get only the title, the record time and the channel
    	    #line = line[ line.rfind('/') +1: line.find('.avi')]
            line = line[ line.rfind('/') +1: line.find('.mpg')]
    	    line = line.replace('_',' ')
            line = line.replace(',','\t\t ')
   
            recicon = os.path.join(config.ICON_DIR, 'themes/blurr/recordinglater.png')
            #skip multiple occurences of the same thing
            if oldline != line and line != '':
                itemline = line
                if recordingflag:
    	            recicon = os.path.join(config.ICON_DIR, 'themes/blurr/recordingnow.png')
    	        if arg == 0:                
    	            items += [ menu.MenuItem(itemline, icon=recicon)]
    	        elif arg == 1:
    	            items += [ menu.MenuItem(itemline, self.delete_selection,itemline)]
        fd.close()
    
        if arg == 0:
            submenu = menu.Menu(_('VIEW RECORDING SCHEDULE'), items,
                                 reload_func=self.view_schedule, item_types='tv')
        else:
            submenu = menu.Menu(_('DELETE SCHEDULED ITEM'), items,
                                 reload_func=self.view_schedule, item_types='tv')
        menuwidget.pushmenu(submenu)
        if killflag and arg == 1:
            AlertBox(text=_('All Currently Recording Items Have Been Killed!')).show()
            killflag = 0
    
    
    
    
    def delete_selection(self,arg=None, menuw=None):
      
        global killflag
        #stop all recordings if needed
        if arg.find(' (currently recording)') != -1:
            os.system('pkill mencoder')
            killflag = 1 #blood has been spilt today
    
        arg = arg.replace(' (currently recording)','').replace(' ','_')
        fd = open(record_daemon.SCHEDULE,'r')
    
        stringlist = fd.readlines()
        fd.close()
    
        fd = open(record_daemon.SCHEDULE,'w')
        newstringlist = ''
    
        for item in stringlist:
            if item.find(arg) == -1:
    	        print item
    	        print arg
    	        newstringlist += item
        fd.write(newstringlist)
        fd.close()
        menuwidget.back_one_menu()
        self.view_schedule(1)
    
    
    
     
    
    
    def addtime(self,rtime,length):
        '''This function will add two time integers together
        where one is in localtime and the other is a length in
        seconds,
        example:
        rtime = 0305235900
        length = 3650
        addtime(rtime,length)
        will return 0306005950'''
    
        lhour =  (length / 3600)*10000
        lminute = ((length % 3600) / 60)*100
        lsecond = length % 60
        
        rmonth = (rtime / 100000000)*100000000
        rday = (rtime % 100000000 / 1000000)*1000000
        rhour =( rtime % 1000000 / 10000)*10000
        rminute = (rtime % 10000 / 100)*100
        rsecond = rtime % 100
        
        months = 0
        days = 0
        hours = 0
        minutes = 0
        seconds = 0
        
        if lsecond + rsecond >= 60:
            minutes += 100
        seconds = (lsecond + rsecond) % 60
    
        minutes += lminute + rminute
        if minutes >= 6000:
            hours += 10000
            minutes = minutes % 6000
    
        hours += lhour + rhour
        if hours >= 240000:
            days += 1000000
            hours = hours % 240000
    
        days += rday
    
        return  rmonth + days + hours + minutes + seconds
    
        
