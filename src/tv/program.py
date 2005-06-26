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
import kaa.epg

# notifier
import notifier

# freevo imports
import config
import menu
import plugin
from item import Item
from gui.windows import MessageBox

# tv imports
from record.client import recordings
import favorite

class ProgramItem(Item):
    """
    A tv program item for the tv guide and other parts of the tv submenu.
    """
    def __init__(self, program, parent=None):
        Item.__init__(self, parent)
        self.program = program
        self.title = program.title
        self.name  = program.title
        self.start = program.start
        self.stop  = program.stop

        self.channel = program.channel
        self.prog_id = program.id
        self.subtitle = program.subtitle
        self.description = program.description
        self.episode = program.episode
        
        self.scheduled = recordings.get(program.channel.id,
                                        program.start, program.stop)

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
        if not isinstance(other, (ProgramItem, kaa.epg.Program)):
            return 1

        return Unicode(self.title) != Unicode(other.title) or \
               self.start != other.start or \
               self.stop  != other.stop or \
               Unicode(self.channel) != Unicode(other.channel)


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
        if self.scheduled and not self.scheduled.status in \
           ('deleted', 'missed'):
            print self.scheduled.status
            if self.start < time.time() + 10 and \
                   self.scheduled.status in ('recording', 'saved'):
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
        s.submenu = True
        s.infoitem = self
        menuw.pushmenu(s)


    def schedule(self, arg=None, menuw=None):
        (result, msg) = recordings.schedule(self)
        if result:
            MessageBox(text=_('"%s" has been scheduled for recording') % \
                         self.title).show()
        else:
            MessageBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        menuw.delete_submenu


    def remove(self, arg=None, menuw=None):
        (result, msg) = recordings.remove(self.scheduled.id)
        if result:
            MessageBox(text=_('"%s" has been removed as recording') % \
                         self.title).show()
        else:
            MessageBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        menuw.delete_submenu


    def channel_details(self, arg=None, menuw=None):
        items = []
        # keep the notifier alive
        notifier_counter = 0
        for prog in self.channel[time.time():]:
            if not prog.id == -1:
                items.append(ProgramItem(prog))
            notifier_counter = (notifier_counter + 1) % 500
            if not notifier_counter:
                notifier.step(False, False)
        cmenu = menu.Menu(self.channel.name, items,
                          item_types = 'tv program menu')
        # FIXME: the percent values need to be calculated
        # cmenu.table = (15, 15, 70)
        menuw.pushmenu(cmenu)


    def watch_channel(self, arg=None, menuw=None):
        p = self.channel.player(self.channel)
        if p:
            app, device, uri = p
            app.play(self.channel.id, device, uri)


    def watch_recording(self, arg=None, menuw=None):
        MessageBox(text='Not implemented yet').show()


    def search_similar(self, arg=None, menuw=None):
        MessageBox(text='Not implemented yet').show()


    def create_favorite(self, arg=None, menuw=None):
        fav = favorite.FavoriteItem(self.name, self.start, self)
        fav.submenu(menuw=menuw)


    def remove_favorite(self, arg=None, menuw=None):
        MessageBox(text='Not implemented yet').show()
