#if 0 /*
# -----------------------------------------------------------------------
# manual_record.py - A plugin to manually record programs
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/04/12 14:58:38  dischi
# prevent crash for bad TV.xml
#
# Revision 1.4  2004/03/14 01:14:39  mikeruelle
# not really the same file but the name got reused for new skin version
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import time, traceback, sys
from time import gmtime, strftime

import plugin, config, menu

import util.tv_util as tv_util
import tv.record_client as record_client
import event as em

from item import Item
from gui.AlertBox import AlertBox
from gui.InputBox import InputBox
from tv.record_types import Favorite
from tv.epg_types import TvProgram

# Use the alternate strptime module which seems to handle time zones
#
# XXX Remove when we are ready to require Python 2.3
if float(sys.version[0:3]) < 2.3:
    import tv.strptime as strptime
else:
    import _strptime as strptime

DEBUG = config.DEBUG


class ManualRecordItem(Item):
    def __init__(self, parent):
        Item.__init__(self, parent, skin_type='video')

        self.name = _("Manual Record")

        # maxinum number of days we can record
        self.MAXDAYS = 7

        # minimum amount of time it would take record_server.py
        # to pick us up in seconds by default it is one minute plus
        # a few seconds just in case
        self.MINPICKUP = 70

        self.months = [ _('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May'), _('Jun'), _('Jul'), _('Aug'), _('Sep'), _('Oct'), _('Nov'), _('Dec') ]
    
    def make_newprog(self):
        self.prog = TvProgram()

        self.disp_title = self.prog.title = self.name

        self.description = ''
        self.prog.desc = ''

        self.prog.channel_id = config.TV_CHANNELS[0][0]
	self.disp_channel = config.TV_CHANNELS[0][1]

        now = time.time()
        now += 300
        starttime = time.localtime(now)
        self.start_month = starttime[1]
	self.disp_start_month = self.months[self.start_month]
        self.start_day   = starttime[2]
        self.start_time  = time.strftime(config.TV_TIMEFORMAT, starttime)
        self.prog.start  = now
	self.disp_starttime = '%s %s %s' % (self.disp_start_month, self.start_day, self.start_time)

        now += 1900
        stoptime = time.localtime(now)
        self.stop_month = stoptime[1]
	self.disp_stop_month = self.months[self.stop_month]
        self.stop_day   = stoptime[2]
        self.stop_time  = time.strftime(config.TV_TIMEFORMAT, stoptime)
        self.prog.stop  = now
	self.disp_stoptime = '%s %s %s' % (self.disp_stop_month, self.stop_day, self.stop_time)

    def actions(self):
        return [( self.display_recitem , _('Display record item') )]


    def display_recitem(self, arg=None, menuw=None):
        self.make_newprog()

        items = []

        items.append(menu.MenuItem(_('Modify name'), action=self.mod_name))
        items.append(menu.MenuItem(_('Modify channel'), action=self.mod_channel))
        items.append(menu.MenuItem(_('Modify start month'), action=self.mod_start_month))
        items.append(menu.MenuItem(_('Modify start day'), action=self.mod_start_day))
        items.append(menu.MenuItem(_('Modify start time'), action=self.mod_start_time))
        items.append(menu.MenuItem(_('Modify stop month'), action=self.mod_stop_month))
        items.append(menu.MenuItem(_('Modify stop day'), action=self.mod_stop_day))
        items.append(menu.MenuItem(_('Modify stop time'), action=self.mod_stop_time))
        items.append(menu.MenuItem(_('Save'), action=self.save_changes))

        manualrecord_menu = menu.Menu(_('Record Item Menu'), items, 
                                 item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_name(self, arg=None, menuw=None):
        self.menuw = menuw
        InputBox(text=_('Alter Name'), handler=self.alter_name).show()


    def mod_channel(self, arg=None, menuw=None):
        items = []

        for chanline in config.TV_CHANNELS:
            items.append(menu.MenuItem(chanline[1], action=self.alter_prop,
                         arg=('channel', (chanline[1],chanline[0]))))

        manualrecord_menu = menu.Menu(_('Modify Channel'), items, 
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_start_month(self, arg=None, menuw=None):
        items = []

        iter=1
        for m in self.months:
            items.append(menu.MenuItem(m, action=self.alter_prop,
                         arg=('startmonth', (m,iter))))
            iter = iter + 1

        manualrecord_menu = menu.Menu(_('Modify Day'), items,
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_start_day(self, arg=None, menuw=None):
        items = []

        iter=1
        while iter < 32:
            items.append(menu.MenuItem(str(iter), action=self.alter_prop,
                         arg=('startday', iter)))
            iter = iter + 1

        manualrecord_menu = menu.Menu(_('Modify Day'), items,
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_start_time(self, arg=None, menuw=None):
        items = []

        for i in range(288):
            mod = i * 5
            showtime = strftime(config.TV_TIMEFORMAT, gmtime(float(mod * 60)))
            items.append(menu.MenuItem(showtime, 
                                       action=self.alter_prop,
                                       arg=('starttime', showtime)))

        manualrecord_menu = menu.Menu(_('Modify Time'), items, 
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_stop_month(self, arg=None, menuw=None):
        items = []

        iter=1
        for m in self.months:
            items.append(menu.MenuItem(m, action=self.alter_prop,
                         arg=('stopmonth', (m,iter))))
            iter = iter + 1

        manualrecord_menu = menu.Menu(_('Modify Day'), items,
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_stop_day(self, arg=None, menuw=None):
        items = []

        iter=1
        while iter < 32:
            items.append(menu.MenuItem(str(iter), action=self.alter_prop,
                         arg=('stopday', iter)))
            iter = iter + 1

        manualrecord_menu = menu.Menu(_('Modify Day'), items,
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def mod_stop_time(self, arg=None, menuw=None):
        items = []

        for i in range(288):
            mod = i * 5
            showtime = strftime(config.TV_TIMEFORMAT, gmtime(float(mod * 60)))
            items.append(menu.MenuItem(showtime, 
                                       action=self.alter_prop,
                                       arg=('stoptime', showtime)))

        manualrecord_menu = menu.Menu(_('Modify Time'), items, 
                                  item_types = 'tv manual record menu')
        manualrecord_menu.infoitem = self
        menuw.pushmenu(manualrecord_menu)
        menuw.refresh()


    def alter_name(self, name):
        if name:
            self.disp_title = self.prog.title = name

        self.menuw.refresh()


    def alter_prop(self, arg=(None,None), menuw=None):
        (prop, val) = arg

        if prop == 'channel':
            self.prog.channel_id = val[1]
	    self.disp_channel = val[0]

        if prop == 'startday':
            self.start_day = val
	    self.disp_starttime = '%s %s %s' % (self.disp_start_month, self.start_day, self.start_time)

        if prop == 'startmonth':
            self.start_month = val[1]
	    self.disp_start_month = val[0]
	    self.disp_starttime = '%s %s %s' % (self.disp_start_month, self.start_day, self.start_time)

        if prop == 'starttime':
            self.start_time = val
	    self.disp_starttime = '%s %s %s' % (self.disp_start_month, self.start_day, self.start_time)

        if prop == 'stopday':
            self.stop_day = val
	    self.disp_stoptime = '%s %s %s' % (self.disp_stop_month, self.stop_day, self.stop_time)

        if prop == 'stopmonth':
            self.stop_month = val[1]
	    self.disp_stop_month = val[0]
	    self.disp_stoptime = '%s %s %s' % (self.disp_stop_month, self.stop_day, self.stop_time)

        if prop == 'stoptime':
            self.stop_time = val
	    self.disp_stoptime = '%s %s %s' % (self.disp_stop_month, self.stop_day, self.stop_time)

        if menuw:  
            menuw.back_one_menu(arg='reload')


    def save_changes(self, arg=None, menuw=None):
        result = self.check_prog()
        if result:
            (result, msg) = record_client.scheduleRecording(self.prog)

            if not result:
                AlertBox(text=_('Save Failed, recording was lost')+(': %s' % msg)).show()
            else:
                if menuw:
                    menuw.back_one_menu(arg='reload')


    def check_prog(self):
        isgood = True
        curtime_epoch = time.time()
        curtime = time.localtime(curtime_epoch)
        startyear = curtime[0] 
        stopyear = curtime[0] 
        currentmonth = curtime[1] 
        
        # handle the year wraparound
        if int(self.stop_month) < currentmonth:
            stopyear = str(int(stopyear) + 1)
        if int(self.start_month) < currentmonth:
            startyear = str(int(startyear) + 1)
        # create utc second start time
        starttime = time.mktime(strptime.strptime(str(self.start_month)+" "+str(self.start_day)+" "+str(startyear)+" "+str(self.start_time)+":00",'%m %d %Y '+config.TV_TIMEFORMAT+':%S'))
        # create utc stop time
        stoptime = time.mktime(strptime.strptime(str(self.stop_month)+" "+str(self.stop_day)+" "+str(stopyear)+" "+str(self.stop_time)+":00",'%m %d %Y '+config.TV_TIMEFORMAT+':%S'))

        # so we don't record for more then maxdays (maxdays day * 24hr/day * 60 min/hr * 60 sec/min)
        if not abs(stoptime - starttime) < (self.MAXDAYS * 86400): 
            if self.MAXDAYS > 1:
                isgood = False
                msg = _("Program would record for more than %d days!") % self.MAXDAYS
                AlertBox(text=_('Save Failed, recording was lost')+(': %s' % msg)).show()
            else:
                isgood = False
                msg = _("Program would record for more than 1 day!") % self.MAXDAYS
                AlertBox(text=_('Save Failed, recording was lost')+(': %s' % msg)).show()

        elif not starttime < stoptime:
            isgood = False
            msg = _("start time is not before stop time." )
            AlertBox(text=_('Save Failed, recording was lost')+(': %s' % msg)).show()
        elif stoptime < curtime_epoch + self.MINPICKUP:
            isgood = False
            msg = _("Sorry, the stop time does not give enough time for scheduler to pickup the change.  Please set it to record for a few minutes longer.")
            AlertBox(text=_('Save Failed, recording was lost')+(': %s' % msg)).show()
        else:
            self.prog.start = starttime
            self.prog.stop = stoptime

        return isgood


class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin is used to display your list of favorites.

    plugin.activate('tv.view_favorites')

    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
        if config.TV_CHANNELS:
            return [ ManualRecordItem(parent) ]
        return []
