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
# Revision 1.63  2004/12/05 13:01:12  dischi
# delete old tv variables, rename some and fix detection
#
# Revision 1.62  2004/12/04 01:46:46  rshortt
# Use TV_CHANNELLIST from config.
#
# Revision 1.61  2004/11/20 18:23:04  dischi
# use python logger module for debug
#
# Revision 1.60  2004/11/17 19:41:29  dischi
# more work to make tv stable again
#
# Revision 1.59  2004/11/14 15:56:04  dischi
# try to find a strange bug
#
# Revision 1.58  2004/11/13 16:08:30  dischi
# remove some old code from tv, some tv plugins do not work anymore
#
# Revision 1.57  2004/11/12 20:40:07  dischi
# some tv crash fixes and cleanup
#
# Revision 1.56  2004/11/04 19:57:00  dischi
# deactivate coming up for now
#
# Revision 1.55  2004/10/23 14:35:02  rshortt
# Get smaller amounts of data at a time to improve speed and make our list
# of programs more realtime.  Also remove import of ProgramItem because we
# no longer need to create any ourselves.
#
# Revision 1.54  2004/10/18 01:19:05  rshortt
# Remove old ProgramItem and add some changes for new pyepg interface.
#
# Revision 1.53  2004/10/03 15:55:25  dischi
# adjust to new popup code
#
# Revision 1.52  2004/08/26 18:59:14  dischi
# bugfix
#
# Revision 1.51  2004/08/26 18:58:20  dischi
# add time to item
#
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
import traceback

import config
import util
import gui
import menu

from event import *
from application import MenuApplication
from item import Item

import logging
log = logging.getLogger('tv')

_guide_ = None

def get_singleton():
    """
    return the global tv guide
    """
    global _guide_
    if not _guide_:
        _guide_ = TVGuide()
    return _guide_



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
        self.engine = gui.AreaHandler('tv', ('screen', 'title', 'subtitle',
                                             'view', 'tvlisting', 'info'))
        self.parent = parent

        box = gui.PopupBox(text=_('Preparing the program guide'))
        box.show()

        if not config.TV_CHANNELLIST:
            box.destroy()
            gui.AlertBox(text=_('TV Guide is corrupt!')).show()
            return False

        self.current_time = int(time.time())
        start_time = self.current_time - 1800
        stop_time  = self.current_time + 3*3600
        config.TV_CHANNELLIST.import_programs(start_time, stop_time)

        self.channel  = config.TV_CHANNELLIST.get()
        self.selected = self.channel.get(self.current_time)[0]

        box.destroy()
        return True
    
        
    def show(self):
        """
        show the guide
        """
        log.info('show')
        self.update_schedules(force=True)
        self.refresh()
        MenuApplication.show(self)
        

    def hide(self):
        """
        hide the guide
        """
        log.info('hide')
        MenuApplication.hide(self)
            
        
    def update_schedules(self, force=False):
        # TODO: this will most likely change into something like
        #       epg.get_scheduled_recordings() which will in turn just
        #       select * from record_programs.  src/tv/channels.py may
        #       even translate the results into ProgramItems.
        #
        # NOT WORKING RIGHT NOW
        return

        
    def eventhandler(self, event):
        if MenuApplication.eventhandler(self, event):
            return True

        log.debug('TVGUIDE EVENT is %s' % event)

        if event == MENU_CHANGE_STYLE:
            pass
            
        if event == MENU_UP:
            config.TV_CHANNELLIST.up()
            self.channel  = config.TV_CHANNELLIST.get()
            try:
                self.selected = self.channel.get(self.current_time)[0]
            except Exception, e:
                print e
                print self.current_time
            self.refresh()

        elif event == MENU_DOWN:
            config.TV_CHANNELLIST.down()
            self.channel  = config.TV_CHANNELLIST.get()
            try:
                self.selected = self.channel.get(self.current_time)[0]
            except Exception, e:
                print e
                print self.current_time
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

        elif event == MENU_PAGEUP:
            pass

        elif event == MENU_PAGEDOWN:
            pass

        elif event == TV_SHOW_CHANNEL:
            items = []
            # channel = config.TV_CHANNELLIST.get_settings_by_id(self.chan_id)
            # for prog in channel.get(time.time(), -1):
            for prog in self.selected.get(time.time(), -1):
                items.append(prog)
            cmenu = menu.Menu(self.channel.name, items)
            # FIXME: the percent values need to be calculated
            # cmenu.table = (15, 15, 70)
            self.menuw.pushmenu(cmenu)

        elif event == TV_START_RECORDING:
            self.show_item_menu()
            self.refresh()
 
        elif event == MENU_SELECT or event == PLAY:
            tvlockfile = config.FREEVO_CACHEDIR + '/record'

            # Check if the selected program is >7 min in the future
            # if so, bring up the record dialog
            now = time.time() + (7*60)
            if self.selected.start > now:
                self.show_item_menu()
            
            elif os.path.exists(tvlockfile):
                # XXX: In the future add the options to watch what we are
                #      recording or cancel it and watch TV.
                gui.AlertBox(_('You cannot watch TV while recording. ')+ \
                             _('If this is not true then remove ') + \
                             tvlockfile + '.').show()
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


    def start_tv(self):
        """
        start the best player for the current channel
        """
        p = self.channel.player()
        if p:
            app, device, uri = p
            app.play(self.channel, device, uri)


    def show_item_menu(self):
        self.selected.submenu(menuw=self.menuw, additional_items=True)


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('tvguide')
