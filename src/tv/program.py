# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# program.py -
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rob@infointeractive.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
#
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
# -----------------------------------------------------------------------------

# python imports
import time

# freevo imports
import config
import menu
from item import Item
from gui import AlertBox

# tv imports
import recordings
import favorite
import channels

class ProgramItem(Item):
    """
    A tv program item for the tv guide and other parts of the tv submenu.
    """
    def __init__(self, program, parent=None):
        Item.__init__(self, parent, skin_type='video')
        self.program = program
        self.title = program.title
        self.name  = program.title
        self.start = program.start
        self.stop  = program.stop

        self.channel = program.channel
        self.prog_id = program.id
        self.info['subtitle'] = program.subtitle
        self.info['description'] = program.description

        key = '%s%s%s' % (program.channel.chan_id, program.start, program.stop)
        if recordings.recordings.has_key(key):
            self.scheduled = recordings.recordings[key]
        else:
            self.scheduled = False

        # TODO: add category support (from epgdb)
        self.categories = ''
        # TODO: add ratings support (from epgdb)
        self.ratings = ''


    def __unicode__(self):
        """
        return as unicode for debug
        """
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel.name) + \
               self.title


    def __str__(self):
        """
        return as string for debug
        """
        return String(self.__unicode__())


    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not isinstance(other, (ProgramItem, channels.Program)):
            return 1

        return self.title != other.title or \
               self.start != other.start or \
               self.stop  != other.stop or \
               self.channel != other.channel


    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key == 'start':
            return Unicode(time.strftime(config.TV_TIMEFORMAT,
                                         time.localtime(self.start)))
        if key == 'stop':
            return Unicode(time.strftime(config.TV_TIMEFORMAT,
                                         time.localtime(self.stop)))
        if key == 'date':
            return Unicode(time.strftime(config.TV_DATEFORMAT,
                                         time.localtime(self.start)))
        if key == 'time':
            return self['start'] + u' - ' + self['stop']
        if key == 'channel':
            return self.channel.name
        return Item.__getitem__(self, key)


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ (self.submenu, _('Show program menu') ) ]


    def submenu(self, arg=None, menuw=None, additional_items=False):
        """
        show a submenu for this item
        """
        items = []
        if self.scheduled:
            if self.start < time.time() + 10 and \
                   self.scheduled[5] in ('recording', 'saved'):
                items.append(menu.MenuItem(_('Watch recording'), \
                                           self.watch_recording))
            if self.stop > time.time():
                if self.start < time.time():
                    items.append(menu.MenuItem(_('Stop recording'), \
                                               self.remove))
                else:
                    items.append(menu.MenuItem(_('Remove recording'), \
                                               self.remove))
        elif self.stop > time.time():
            items.append(menu.MenuItem(_('Schedule for recording'), \
                                       self.schedule))
        if additional_items:
            items.append(menu.MenuItem(_('Show complete listing for %s') % \
                                       self.channel.name,
                                       self.channel_details))
            items.append(menu.MenuItem(_('Watch %s') % self.channel.name,
                                       self.watch_channel))
            txt = _('Search for programs with a similar name')
            items.append(menu.MenuItem(txt, self.search_similar))

        items.append(menu.MenuItem(_('Add to favorites'),
                                   self.create_favorite))

        s = menu.Menu(self, items, item_types = 'tv program menu')
        s.is_submenu = True
        s.infoitem = self
        menuw.pushmenu(s)


    def schedule(self, arg=None, menuw=None):
        (result, msg) = recordings.schedule_recording(self)
        if result:
            AlertBox(text=_('"%s" has been scheduled for recording') % \
                         self.title).show()
        else:
            AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        menuw.delete_submenu


    def remove(self, arg=None, menuw=None):
        (result, msg) = recordings.remove_recording(self)
        if result:
            AlertBox(text=_('"%s" has been removed as recording') % \
                         self.title).show()
        else:
            AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        menuw.delete_submenu


    def channel_details(self, arg=None, menuw=None):
        items = []
        for prog in self.channel.get(time.time(), -1):
            items.append(prog)
        cmenu = menu.Menu(self.channel.name, items)
        # FIXME: the percent values need to be calculated
        # cmenu.table = (15, 15, 70)
        menuw.pushmenu(cmenu)


    def watch_channel(self, arg=None, menuw=None):
        AlertBox(text='Not implemented yet').show()


    def watch_recording(self, arg=None, menuw=None):
        AlertBox(text='Not implemented yet').show()


    def search_similar(self, arg=None, menuw=None):
        AlertBox(text='Not implemented yet').show()


    def create_favorite(self, arg=None, menuw=None):
        fav = favorite.FavoriteItem(self.name, self.start, self)
        fav.submenu(menuw=menuw)


    def remove_favorite(self, arg=None, menuw=None):
        AlertBox(text='Not implemented yet').show()
