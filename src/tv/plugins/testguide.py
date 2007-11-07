# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# testguide.py - The the Freevo TV Guide
# -----------------------------------------------------------------------------
# $Id: testguide.py 9541 2007-05-01 18:46:35Z dmeyer $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
# -----------------------------------------------------------------------------


# python imports
import os
import sys
import time
import logging

import kaa.epg
import kaa.notifier

# freevo imports
from freevo.ui.event import *
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.menu import Menu, GridMenu, ActionItem
from freevo.ui.tv.program import ProgramItem
from freevo.ui.application import MessageWindow
from freevo.ui import config

# get logging object
log = logging.getLogger('tv')

ONE_HOUR_IN_TIME = (60 * 60)
ONE_DAY_IN_TIME = (24 * ONE_HOUR_IN_TIME)
COLUMN_TIME = ONE_HOUR_IN_TIME

#fix me: Use number of days from config files
MAX_DAYS = 1

class PluginInterface(MainMenuPlugin):

    def items(self, parent):
        return [ ActionItem(_('TV Guide'), parent, self.show) ]

    def show(self, parent):
        if not kaa.epg.is_connected():
            MessageWindow(_('TVServer not running')).show()
            return
        guide = TVGuide2(parent)
        parent.get_menustack().pushmenu(guide)

    
class TVGuide2(GridMenu):
    """
    TVGuide2 menu.
    """
    def __init__(self, parent):
        GridMenu.__init__(self, _('TV Guide2'), type = 'tv grid')
        self.parent = parent
        self.viewed_time = int(time.time())
        self.viewed_time = ((self.viewed_time / COLUMN_TIME) * COLUMN_TIME)
        self.prev_viewed_time = 0
        
        # current channel is the first one
        self.channels = kaa.epg.get_channels(sort=True)
        # FIXME: make it work without step()
        if isinstance(self.channels, kaa.notifier.InProgress):
            while not self.channels.is_finished:
                kaa.notifier.step()
            self.channels = self.channels()

        self.query_start_time = self.viewed_time
        self.query_stop_time = 0
        self.query_data = []
        # current program is the current running
        self.advanced_mode = True
        self.selected = None
        self.selected_start_time = self.viewed_time
        self.update()

        
    def get_item(self, row, col):
        """
        Return the data for that col, row.
        """
        try:
            item = self.choices[self.base_row+row][col]
        except:
            return None
        return item

    def get_item_state(self, row, col):
        """
        Return the state for this item
        """
        item = self.get_item(row, col)[1]
        if self.selected == item:
            return 'selected'
        elif item.scheduled:
            if item.scheduled.status in ('conflict', 'scheduled'):
                return 'scheduled'
            elif item.scheduled.status == 'recording':
                return 'recording'
            else:
                return 'default'
        else:
            return 'default'
        
    @kaa.notifier.yield_execution()
    def update(self):
        """
        update the guide information
        """
        #Find the new time to display
        if self.selected:
            self.selected_start_time = self.selected.start
            if self.selected_start_time >= (self.viewed_time + (COLUMN_TIME * self.cols)):
                #Put halfway the grid
                self.viewed_time = self.selected_start_time - (COLUMN_TIME * self.cols / 2)
            elif self.selected_start_time < self.viewed_time:
                self.viewed_time = self.selected_start_time
                
            self.viewed_time = ((self.viewed_time / COLUMN_TIME) * COLUMN_TIME)
            
        #do we need to start a new query?
        if self.viewed_time < self.query_start_time or \
           (self.viewed_time + (COLUMN_TIME * self.cols)) > self.query_stop_time:
            print 'new query'
            self.query_start_time = self.viewed_time
            self.query_stop_time = self.query_start_time + ONE_DAY_IN_TIME
        
            self.query_data = []
            for channel in self.channels:
                programs = []
                # query the epg database in background
                wait = kaa.epg.search(channel=channel, time=(self.query_start_time, self.query_stop_time))
                yield wait
                # get data from InProgress object
                query_data = wait()
                #Sort the programs
                query_data.sort(lambda x,y: cmp(x.start, y.start))
                for data in query_data:
                    data = ProgramItem(data, self)
                    programs.append(data)
        
                self.query_data.append(programs)

        #Calculate new view
        if self.prev_viewed_time != self.viewed_time:
            self.update_view = True
            self.prev_viewed_time = self.viewed_time
            items = []
            for channel in self.query_data:
                programs = []
                for data in channel:
                    #only add items which are in the view
                    if data.stop >= self.viewed_time:
                        #selected the correct first item
                        if self.selected == None and \
                           data.stop > self.viewed_time:
                            self.selected = data
                        start = max(data.start, self.viewed_time)
                        size = ((data.stop - start) *100) / COLUMN_TIME
                        i = (size , data)
                        programs.append(i)
    
                items.append(programs)
        
            self.set_items(items, selected=self.selected)


    def get_column_name(self, col):
        """
        Return the column name
        """
        #get rid of the minutes
        t = self.viewed_time
        t += (col*COLUMN_TIME)
        return unicode(time.strftime(config.tv.timeformat,
                       time.localtime(t)))

    def get_row_name(self, row):
        """
        Return the row name
        """
        return self.channels[self.base_row+row].name

    def select_program(self):
        """
        Select program for the new row
        """
        for program in self.choices[self.selected_row]:
            size, data = program
            if data.start <= self.selected_start_time and data.stop > self.selected_start_time:
                self.select(row=self.selected_row, col=self.choices[self.selected_row].index(program))

    def eventhandler(self, event):
        handled = False
        if not self.selected:
            # not ready yet
            return True

        if event == MENU_CHANGE_STYLE:
            handled = True

        elif event == MENU_UP:
            self.select(col=self.selected_col,
                        row=self.selected_row-1 )
            self.select_program()
            handled = True

        elif event == MENU_DOWN:
            self.select(col=self.selected_col,
                        row=self.selected_row+1 )
            self.select_program()
            handled = True

        elif event == MENU_LEFT:
            self.select(col=self.selected_col-1,
                        row=self.selected_row )
            self.update()
            handled = True

        elif event == MENU_RIGHT:
            self.select(col=self.selected_col+1,
                        row=self.selected_row )
            self.update()
            handled = True

        elif event == TV_SHOW_CHANNEL:
            self.selected.channel_details()
            handled = True

        elif event == MENU_SUBMENU:
            self.selected.submenu(additional_items=True)
            handled = True

        elif event == TV_START_RECORDING:
            # TODO: make this schedule or remove
            self.selected.submenu(additional_items=True)
            handled = True

        elif event == PLAY:
            self.selected.watch_channel()
            handled = True

        elif event == MENU_SELECT or event == PLAY:
            # Check if the selected program is >7 min in the future
            # if so, bring up the submenu
            now = time.time() + (7*60)
            if self.selected.start > now:
                self.selected.submenu(additional_items=True)
            else:
                self.selected.watch_channel()
            handled = True

        else:
            #If not handled try default eventhandler
            handled = GridMenu.eventhandler(self, event)

        return handled
 