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
import time

# kaa imports
import kaa.epg

# freevo core imports
import freevo.ipc

# freevo imports
import config
import plugin
from menu import Item, Action, Menu, ActionItem
from gui.windows import MessageBox

# tv imports
import favorite

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

class ProgramItem(Item):
    """
    A tv program item for the tv guide and other parts of the tv submenu.
    """
    def __init__(self, program, parent):
        Item.__init__(self, parent)
        self.program = program
        self.title = program.title
        self.name  = program.title
        self.start = program.start
        self.stop  = program.stop

        self.channel = program.channel
        self.subtitle = program.subtitle
        self.description = program.description
        self.episode = program.episode
        
        self.scheduled = tvserver.recordings.get(program.channel.name,
                                        program.start, program.stop)

        # TODO: add category support
        self.categories = ''
        # TODO: add ratings support
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
        return [ Action(_('Show program menu'), self.submenu) ]


    def submenu(self, additional_items=False):
        """
        show a submenu for this item
        """
        items = []
        if self.scheduled and not self.scheduled.status in \
           ('deleted', 'missed'):
            print self.scheduled.status
            if self.start < time.time() + 10 and \
                   self.scheduled.status in ('recording', 'saved'):
                items.append(ActionItem(_('Watch recording'), self,
                                        self.watch_recording))
            if self.stop > time.time():
                if self.start < time.time():
                    items.append(ActionItem(_('Stop recording'), self,
                                            self.remove))
                else:
                    items.append(ActionItem(_('Remove recording'), self,
                                            self.remove))
        elif self.stop > time.time():
            items.append(ActionItem(_('Schedule for recording'), self,
                                    self.schedule))
        if additional_items:
            items.append(ActionItem(_('Show complete listing for %s') % \
                                    self.channel.name, self,
                                    self.channel_details))
            items.append(ActionItem(_('Watch %s') % self.channel.name, self,
                                    self.watch_channel))
            txt = _('Search for programs with a similar name')
            items.append(ActionItem(txt, self, self.search_similar))

        items.append(ActionItem(_('Add to favorites'), self,
                                self.create_favorite))

        s = Menu(self, items, item_types = 'tv program menu')
        s.submenu = True
        s.infoitem = self
        self.pushmenu(s)


    def schedule(self):
        (result, msg) = tvserver.recordings.schedule(self)
        if result:
            MessageBox(_('"%s" has been scheduled for recording') % \
                       self.title).show()
        else:
            MessageBox(_('Scheduling Failed')+(': %s' % msg)).show()
        self.get_menustack().delete_submenu()


    def remove(self):
        (result, msg) = tvserver.recordings.remove(self.scheduled.id)
        if result:
            MessageBox(_('"%s" has been removed as recording') % \
                       self.title).show()
        else:
            MessageBox(_('Scheduling Failed')+(': %s' % msg)).show()
        self.get_menustack().delete_submenu()


    def channel_details(self):
        items = []
        for prog in kaa.epg.search(channel=self.channel):
            items.append(ProgramItem(prog, self))
        cmenu = Menu(self.channel.name, items, item_types = 'tv program menu')
        # FIXME: the percent values need to be calculated
        # cmenu.table = (15, 15, 70)
        self.pushmenu(cmenu)


    def watch_channel(self):
        p = plugin.getbyname(plugin.TV)
        if p:
            p.play(self.channel.id)
        

    def watch_recording(self):
        MessageBox('Not implemented yet').show()


    def search_similar(self):
        MessageBox('Not implemented yet').show()


    def create_favorite(self):
        fav = favorite.FavoriteItem(self.name, self.start, self)
        fav.submenu()


    def remove_favorite(self):
        MessageBox('Not implemented yet').show()
