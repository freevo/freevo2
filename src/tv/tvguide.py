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
# Revision 1.50  2004/08/26 15:25:52  dischi
# some MenuApplication fixes
#
# Revision 1.49  2004/08/24 16:42:43  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.48  2004/08/14 16:54:47  rshortt
# Remove encode() call on program object.
#
# Revision 1.47  2004/08/14 15:12:55  dischi
# use new AreaHandler
#
# Revision 1.46  2004/08/14 12:52:31  rshortt
# Used cached channal list/epg.
#
# Revision 1.45  2004/08/10 19:37:23  dischi
# better pyepg integration
#
# Revision 1.44  2004/08/09 21:19:47  dischi
# make tv guide working again (but very buggy)
#
# Revision 1.43  2004/08/05 17:27:16  dischi
# Major (unfinished) tv update:
# o the epg is now taken from pyepg in lib
# o all player should inherit from player.py
# o VideoGroups are replaced by channels.py
# o the recordserver plugins are in an extra dir
#
# Bugs:
# o The listing area in the tv guide is blank right now, some code
#   needs to be moved to gui but it's not done yet.
# o The only player working right now is xine with dvb
# o channels.py needs much work to support something else than dvb
# o recording looks broken, too
#
# Revision 1.42  2004/07/27 11:10:11  dischi
# fix application import
#
# Revision 1.41  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
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
import util
import gui
import menu

from event import *
from application import MenuApplication

from channels import get_channels

from program_display import ProgramItem
import record_client as ri
from item import Item

_guide_ = None

def get_singleton():
    """
    return the global tv guide
    """
    global _guide_
    if not _guide_:
        _guide_ = TVGuide()
    return _guide_


class ProgrammItem(Item):
    def __init__(self, parent, prog):
        Item.__init__(self, parent)
        self.name = prog.title
        # Import all variables from the programm
        # FIXME: this needs a cleanup to be a real item
        for var in dir(prog):
            if var.startswith('_') or var == 'getattr':
                continue
            setattr(self, var, getattr(prog, var))

        

class TVGuide(MenuApplication):
    """
    TVGuide application. It is _inside_ the menu, so it is a
    MenuApplication. When inside the menuw, there is also a variable
    self.menuw.
    """
    def __init__(self):
        MenuApplication.__init__(self, 'tvguide', 'tvmenu', False)
        self.CHAN_NO_DATA = _('This channel has no data loaded')
        self.last_update  = 0
        

    def start(self, parent):
        self.engine = gui.AreaHandler('tv', ('screen', 'title', 'subtitle', 'view',
                                             'tvlisting', 'info'))
        self.parent = parent
        
        # self.n_items, hours_per_page = self.engine.items_per_page(('tv', self))
        # stop_time = start_time + hours_per_page * 60 * 60

        box = gui.PopupBox(text=_('Preparing the program guide'))
        box.show()

        try:
            channels = get_channels()
        except Exception, e:
            box.destroy()
            gui.AlertBox(text=_('TV Guide is corrupt!')).show()
            print e
            return False
        
        self.current_time = time.time()
        self.channel      = channels.get()
        self.selected     = self.channel.get(self.current_time)[0]

        self.channel_list = channels
        box.destroy()
        return True
    
        
    def show(self):
        """
        show the guide
        """
        _debug_('show')
        self.update_schedules(force=True)
        self.refresh()
        MenuApplication.show(self)
        

    def hide(self):
        """
        hide the guide
        """
        _debug_('hide')
        MenuApplication.hide(self)
            
        
    def start_tv(self):
        """
        start the bester player for the current channel
        """
        p = self.channel.player()
        if p:
            app, device, freq = p
            app.play(self.channel, device, freq)


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
        try:
            (got_schedule, schedule) = ri.getScheduledRecordings()
        except Exception, e:
            print e
            return
        
        util.misc.comingup(None, (got_schedule, schedule))

        if got_schedule:
            l = schedule.getProgramList()
            for k in l:
                self.scheduled_programs.append(l[k])

        
    def eventhandler(self, event):
        if MenuApplication.eventhandler(self, event):
            return True

        _debug_('TVGUIDE EVENT is %s' % event, 2)

#         if event == MENU_CHANGE_STYLE:
#             if self.engine.toggle_display_style('tv'):
#                 start_time    = self.start_time
#                 stop_time     = self.stop_time
#                 start_channel = self.start_channel
#                 selected      = self.selected

#                 self.n_items, hours_per_page = self.engine.items_per_page(('tv', self))

#                 before = -1
#                 after  = -1
#                 for c in self.guide.chan_list:
#                     if before >= 0 and after == -1:
#                         before += 1
#                     if after >= 0:
#                         after += 1
#                     if c.id == start_channel:
#                         before = 0
#                     if c.id == selected.channel_id:
#                         after = 0
                    
#                 if self.n_items <= before:
#                     start_channel = selected.channel_id

#                 if after < self.n_items:
#                     up = min(self.n_items -after, len(self.guide.chan_list)) - 1
#                     for i in range(len(self.guide.chan_list) - up):
#                         if self.guide.chan_list[i+up].id == start_channel:
#                             start_channel = self.guide.chan_list[i].id
#                             break
                    
#                 stop_time = start_time + hours_per_page * 60 * 60

#                 self.n_cols  = (stop_time - start_time) / 60 / self.col_time
#                 self.rebuild(start_time, stop_time, start_channel, selected)
#                 self.refresh()
            
        if event == MENU_UP:
            self.channel_list.up()
            self.channel  = self.channel_list.get()
            self.selected = self.channel.get(self.current_time)[0]
            self.refresh()

        elif event == MENU_DOWN:
            self.channel_list.down()
            self.channel  = self.channel_list.get()
            self.selected = self.channel.get(self.current_time)[0]
            self.refresh()

        elif event == MENU_LEFT:
            self.selected = self.channel.prev(self.selected)
            if self.selected.start:
                self.current_time = self.selected.start + 1
            else:
                self.current_time -= 60 * 30
            self.refresh()

        elif event == MENU_RIGHT:
            self.selected = self.channel.next(self.selected)
            if self.selected.start:
                self.current_time = self.selected.start + 1
            else:
                self.current_time -= 60 * 30
            self.refresh()

#         elif event == MENU_PAGEUP:
#             self.event_change_channel(-self.n_items)
#             self.refresh()

#         elif event == MENU_PAGEDOWN:
#             self.event_change_channel(self.n_items)
#             self.refresh()

        elif event == TV_SHOW_CHANNEL:
            _debug_('show channel')
            items = []
            for prog in self.channel.epg.get(time.time(), time.time() + 10*24*60*60)[:-1]:
                items.append(ProgrammItem(self.parent, prog))
            cmenu = menu.Menu(self.channel.name, items)
            self.menuw.pushmenu(cmenu)

        elif event == TV_START_RECORDING:
            self.event_RECORD()
            self.refresh()
 
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
                #      recording or cancel it and watch TV.
                gui.AlertBox(text=_('Sorry, you cannot watch TV while recording. ')+ \
                             _('If this is not true then remove ') + \
                             tvlockfile + '.', height=200).show()
                return True
            else:
                self.start_tv()
        
        elif event == PLAY_END:
            self.show()

        else:
            return False

        return True


    def refresh(self):
        self.engine.draw(self)



    def event_RECORD(self):
        if self.selected.scheduled:
            pi = ProgramItem(self.parent, prog=self.selected, context='schedule')
        else:
            pi = ProgramItem(self.parent, prog=self.selected, context='guide')
        pi.display_program(menuw=self.menuw)


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('tvguide')
