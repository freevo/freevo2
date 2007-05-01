# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------------
# $Id: directory.py 9248 2007-02-19 20:06:25Z dmeyer $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Jose <jose4freevo@chello.nl>
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
import time

# kaa imports
import kaa.notifier
from kaa.strutils import unicode_to_str

# freevo core imports
import freevo.ipc

# freevo ui imports
from freevo.ui import config
from freevo.ui.menu import Menu, ActionItem, Action, Item
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.application import MessageWindow

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

class RecordingItem(Item):
    """
    A recording item to remove/watch a scheduled recording.
    """
    def __init__(self, channel, start, stop, parent):
        Item.__init__(self, parent)

        self.scheduled = tvserver.recordings.get(channel, start, stop)
        if self.scheduled.description.has_key('title'):
            self.title = self.scheduled.description['title']
            self.name  = self.scheduled.description['title']
        else:
            self.name  = self.title = ''
        self.channel = channel
        self.start = start
        self.stop = stop


    def __unicode__(self):
        """
        return as unicode for debug
        """
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel) + \
               self.title


    def __str__(self):
        """
        return as string for debug
        """
        return unicode_to_str(self.__unicode__())


    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not isinstance(other, (RecordingItem)):
            return 1

        return self.start != other.start or \
               self.stop  != other.stop or \
               self.channel != other.channel


    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key == 'start':
            return unicode(time.strftime(config.tv.timeformat,
                                         time.localtime(self.start)))
        if key == 'stop':
            return unicode(time.strftime(config.tv.timeformat,
                                         time.localtime(self.stop)))
        if key == 'date':
            return unicode(time.strftime(config.tv.dateformat,
                                         time.localtime(self.start)))
        if key == 'time':
            return self['start'] + u' - ' + self['stop']
        if key == 'channel':
            return self.channel

        return Item.__getitem__(self, key)


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ Action(_('Show recording menu'), self.submenu) ]


    def submenu(self):
        """
        show a submenu for this item
        """
        items = []
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

        s = Menu(self, items, type = 'tv program menu')
        s.submenu = True
        s.infoitem = self
        self.get_menustack().pushmenu(s)


    def watch_recording(self):
        MessageWindow('Not implemented yet').show()


    @kaa.notifier.yield_execution()
    def remove(self):
        result = tvserver.recordings.remove(self.scheduled.id)
        if isinstance(result, kaa.notifier.InProgress):
            yield result
            result = result()
        if result != tvserver.recordings.SUCCESS:
            MessageWindow(_('Scheduling Failed')+(': %s' % result)).show()
        self.get_menustack().delete_submenu()


class PluginInterface(MainMenuPlugin):
    """
    This plugin is used to display your scheduled recordings.
    """
    def scheduled(self, parent):
        """
        Show all scheduled recordings.
        """
        self.parent = parent
        items = self.get_items(parent)
        if items:
            self.menu = Menu(_('View scheduled recordings'), items,
                             type='tv program menu',
                             reload_func = self.reload_scheduled)
            parent.get_menustack().pushmenu(self.menu)
        else:
            MessageWindow(_('There are no scheduled recordings.')).show()


    def reload_scheduled(self):
        items = self.get_items(self.parent)
        if items:
            self.menu.set_items(items)
        else:
            self.parent.get_menustack().back_one_menu()

    def get_items(self, parent):
        items = []
        rec = tvserver.recordings.list()
        for p in rec:
            scheduled = tvserver.recordings.get(p.channel, p.start, p.stop)
            if scheduled and not scheduled.status in ('deleted', 'missed'):
                items.append(RecordingItem(parent=parent, channel=p.channel,
                                           start=p.start, stop=p.stop))

        return items

    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ActionItem(_('View scheduled recordings'), parent, self.scheduled) ]
