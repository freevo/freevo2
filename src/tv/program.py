# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# program.py -
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rob@tvcentric.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#                Rob Shortt <rob@tvcentric.com>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
import sys
import time

# kaa imports
import kaa
import kaa.epg

# freevo core imports
import freevo.ipc

# freevo imports
from freevo.ui import config
from freevo.ui.menu import Item, Action, Menu, ActionItem
from freevo.ui.application import MessageWindow

# tv imports
import favorite

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

import logging
log = logging.getLogger()

class ProgramItem(Item):
    """
    A tv program item for the tv guide and other parts of the tv submenu.
    """
    def __init__(self, program, parent):
        Item.__init__(self, parent)
        self.start = program.start
        self.stop  = program.stop

        if isinstance(program, kaa.epg.Program):
            # creation form epg Program object
            self.channel = program.channel.name
            self.title = program.title
            self.name  = program.title
            self.subtitle = program.subtitle
            self.episode = program.episode
            self.description = program.description
            # TODO: add category/genre support
            self.categories = ''
            self.genre = ''
            # TODO: add ratings support
            self.ratings = ''


        elif isinstance(program, freevo.ipc.tvserver.Recording):
            # creation form ipc Recoring object
            self.channel = program.channel
            if program.description.has_key('title'):
                self.title = program.description['title']
                self.name  = program.description['title']
            else:
                self.name = self.title = _(u'Unknown')

            if program.description.has_key('subtitle'):
                self.subtitle = program.description['subtitle']
            else:
                self.subtitle = ''
            if program.description.has_key('episode'):
                self.episode = program.description['episode']
            else:
                self.episode = ''
            # TODO: check if this is also available
            self.description = ''
            # TODO: add catergory/genre support
            self.categories = ''
            self.genre = ''
            # TODO: add ratings support
            self.rating = ''
            
        # check if this is a recording
        self.scheduled = tvserver.recordings.get(self.channel,
                                                 self.start,
                                                 self.stop)
        # check if this is a favorite
        self.favorite = tvserver.favorites.get(self.title,
                                               self.channel,
                                               self.start,
                                               self.stop)
       

    def __unicode__(self):
        """
        return as unicode for debug
        """
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel) + self.title


    def __str__(self):
        """
        return as string for debug
        """
        return kaa.unicode_to_str(self.__unicode__())


    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not isinstance(other, (ProgramItem, kaa.epg.Program)):
            return 1
        if isinstance(other, ProgramItem) and self.channel != other.channel:
            return 1
        if isinstance(other, kaa.epg.Program) and self.channel != other.channel.name:
            return 1

        return self.title != other.title or \
               self.start != other.start or \
               self.stop  != other.stop



    def get_start(self):
        """
        Return start time as formated unicode string.
        """
        return unicode(time.strftime(config.tv.timeformat, time.localtime(self.start)))


    def get_stop(self):
        """
        Return stop time as formated unicode string.
        """
        return unicode(time.strftime(config.tv.timeformat, time.localtime(self.stop)))


    def get_time(self):
        """
        Return start time and stop time as formated unicode string.
        """
        return self.get_start() + u' - ' + self.get_stop()


    def get_date(self):
        """
        Return date as formated unicode string.
        """
        return unicode(time.strftime(config.tv.dateformat, time.localtime(self.start)))


    def get_channel(self):
        """
        Return channel object.
        """
        return self.channel


    ### Submenu

    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ Action(_('Show program menu'), self.submenu) ]


    def reload_submenu(self):
        """
        reload function for the submenu
        """
        items = self.get_menuitems()
        if items:
            self.get_menustack()[-1].set_items(items)
        else:
            self.get_menustack().back_one_menu()


    def get_menuitems(self):
        """
        create a list of actions for the submenu
        """

        # empty item list
        items = []

        # scheduled for recording
        if self.scheduled and not self.scheduled.status in ('deleted','missed'):
                if self.start < time.time() + 10  \
                and self.scheduled.status in ('recording', 'saved'):
                    # start watching the recorded stream from disk
                    txt = _('Watch recording')
                    items.append(ActionItem(txt, self, self.watch_recording))
                if self.stop > time.time():
                    # not yet finished
                    if self.start < time.time():
                        # but already running
                        txt = _('Stop recording')
                        items.append(ActionItem(txt, self, self.remove))
                    else:
                        # still in the future
                        txt =  _('Remove recording')
                        items.append(ActionItem(txt, self, self.remove))

        # not scheduled for recording
        elif self.stop > time.time():
            # not in the past, can still be scheduled
            txt = _('Schedule for recording')
            items.append(ActionItem(txt, self, self.schedule))


        # this items are only shown from inside the TVGuide:
        if self.additional_items:
            # Show all programm on this channel
            txt = ('Show complete listing for %s') % self.channel
            items.append(ActionItem(txt, self, self.channel_details))
            # Start watching this channel
            txt = _('Watch %s') % self.channel
            items.append(ActionItem(txt, self, self.watch_channel))
            # Search for more of this program
            txt = _('Search for more of this program')
            items.append(ActionItem(txt, self, self.search_similar))

        # Add the menu for handling favorites
        if self.favorite:
            txt = _('Edit favorite')
            items.append(ActionItem(txt, self, self.edit_favorite))
            txt = _('Remove favorite')
            items.append(ActionItem(txt, self, self.remove_favorite))
        else:
            txt = _('Add favorite')
            items.append(ActionItem(txt, self, self.add_favorite))

        return items


    def submenu(self, additional_items=False):
        """
        show a submenu for this item

        There are some items, that are only created if 'additional_items'
        is set to TRUE, this items are useful in the TVGuide.
        """
        self.additional_items = additional_items
        # get the item list
        items = self.get_menuitems()
        # create the menu
        s = Menu(self, items,
                 type = 'tv program menu',
                 reload_func=self.reload_submenu)
        s.submenu = True
        s.infoitem = self
        # show the menu
        self.get_menustack().pushmenu(s)


    #### Actions

    @kaa.coroutine()
    def schedule(self):
        """
        schedule this item for recording
        """
        result = yield tvserver.recordings.schedule(self)
        if result == tvserver.recordings.SUCCESS:
            msg = _('"%s" has been scheduled for recording') % self.title
            #reload scheduled
            self.scheduled = tvserver.recordings.get(self.channel,
                                                     self.start,
                                                     self.stop)
        else:
            msg = _('Scheduling failed: %s') % result
        MessageWindow(msg).show()
        self.get_menustack().back_one_menu()


    @kaa.coroutine()
    def remove(self):
        """
        remove this item from schedule
        """
        result = yield tvserver.recordings.remove(self.scheduled.id)
        if result == tvserver.recordings.SUCCESS:
            msg = _('"%s" has been removed') % self.title
            #reload scheduled
            self.scheduled = tvserver.recordings.get(self.channel,
                                                     self.start,
                                                     self.stop)
        else:
            msg = _('Removing failed: %s') % result
        MessageWindow(msg).show()
        self.get_menustack().back_one_menu()


    @kaa.coroutine()
    def channel_details(self):
        """
        Browse all programs on this channel
        """
        if not kaa.epg.is_connected():
            MessageWindow(_('TVServer not running')).show()
            return
        items = []
        # time tuple representing the future
        future = (int(time.time()), sys.maxint)
        # query the epg database in background
        channel = kaa.epg.get_channel(self.channel)
        query_data = yield kaa.epg.search(channel=channel, time=future)
        for prog in query_data:
            items.append(ProgramItem(prog, self))
        cmenu = Menu(self.channel, items, type = 'tv program menu')
        # FIXME: the percent values need to be calculated
        # cmenu.table = (15, 15, 70)
        self.get_menustack().pushmenu(cmenu)


    def watch_channel(self):
        MessageWindow('Not implemented yet').show()


    def watch_recording(self):
        MessageWindow('Not implemented yet').show()


    @kaa.coroutine()
    def search_similar(self):
        """
        Search the database for more of this program
        """
        if not kaa.epg.is_connected():
            # we need the tvserver for this
            MessageWindow(_('TVServer not running')).show()
            return
        # time tuple representing the future
        future = (int(time.time()), sys.maxint)
        # create an empty list for ProgramItems
        items = []
        # query the epg database in background
        query_data = yield kaa.epg.search(title=self.title, time=future)
        # and sort is concerning its start times
        query_data.sort(lambda a,b:cmp(a.start,b.start))
        for prog in query_data:
            items.append(ProgramItem(prog, self))
        # create the submenu from this
        resmenu = Menu(self.title, items, type = 'tv program menu')
        self.get_menustack().pushmenu(resmenu)


    def add_favorite(self):
        """
        Create a new FavoriteItem and open its submenu
        """
        favorite.FavoriteItem(self, self).submenu()
        # Reload favorite
        self.favorite = tvserver.favorites.get(self.title,
                                               self.channel,
                                               self.start,
                                               self.stop)


    def edit_favorite(self):
        """
        Create a FavoriteItem for a existing favorite
        and open its submenu to edit this item
        """
        favorite.FavoriteItem(self, self.favorite).submenu()
        # Reload favorite
        self.favorite = tvserver.favorites.get(self.title,
                                               self.channel,
                                               self.start,
                                               self.stop)


    def remove_favorite(self):
        """
        Create a FavoriteItem for a existing favorite
        and delete this favorite.
        """
        favorite.FavoriteItem(self, self.favorite).remove()
        # Reload favorite
        self.favorite = tvserver.favorites.get(self.title,
                                               self.channel,
                                               self.start,
                                               self.stop)

