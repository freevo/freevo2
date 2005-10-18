# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# client.py - the client part of the recordserver
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

import sys
import time
import copy
import logging
import mbus
from types import *

import notifier
import mcomm
import config

# get logging object
log = logging.getLogger('record')

# status values
MISSED    = 'missed'
SAVED     = 'saved'
SCHEDULED = 'scheduled'
RECORDING = 'recording'
CONFLICT  = 'conflict'
DELETED   = 'deleted'
FAILED    = 'failed'

class Recording(object):
    """
    A recording object from the recordserver.
    """
    def __init__(self, *args):
        self.update(*args)


    def update(self, id, channel, priority, start, stop, status):
        self.id = id
        self.channel = channel
        self.priority = priority
        self.start = start
        self.stop = stop
        self.status = status
        self.description = {}


    def __unicode__(self):
        if self.description.has_key('title') and self.description['title']:
            s = self.description['title']
        else:
            s = 'No Title'
        if self.description.has_key('episode') and self.description['episode']:
            s += u' %s' % self.description['episode']
        if self.description.has_key('subtitle') and \
           self.description['subtitle']:
            s += u' - %s' % self.description['subtitle']
        return s


    def __str__(self):
        return String(self.__unicode__())


    def __getitem__(self, key):
        if hasattr(self, key) and key != 'description':
            return getattr(self, key)
        if self.description.has_key(key):
            return self.description[key]
        raise AttributeError('no attribute %s in Recording' % key)


    def has_key(self, key):
        if hasattr(self, key) and key != 'description':
            return True
        return self.description.has_key(key)
        


class Recordings(object):
    """
    Handling of recordings from the recordserver. The object will auto sync
    with the recordserver to keep the list up to date.
    """
    def __init__(self):
        self.last_update = time.time()
        self.__recordings = {}
        self.server = None
        mcomm.register_entity_notification(self.__entity_update)
        mcomm.register_event('record.list.update', self.__list_update)
        self.comingup = ''
        self.running = ''
        self.updating = 0

    def __entity_update(self, entity):
        if not entity.present and entity == self.server:
            log.info('recordserver lost')
            self.comingup = ''
            self.running = ''
            self.server = None
            return

        if entity.present and \
               entity.matches(mcomm.get_address('recordserver')):
            log.info('recordserver found')
            self.server = entity
            self.server.call('recording.list', self.__list_callback)


    def __list_callback(self, result):
        if not self.server:
            return
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return
            
        self.last_update = time.time()
        self.__recordings = {}
        self.updating = 1
        for l in result.arguments:
            self.__recordings['%s-%s-%s' % (l[1], l[3], l[4])] = Recording(*l)
        log.info('got recording list')
        self.__request_description()


    def __list_update(self, result):
        self.updating = 1
        log.info('got recording list update')
        for l in result.payload[0].args:
            if not type(l) is ListType: continue
            key = '%s-%s-%s' % (l[1], l[3], l[4])
            if key in self.__recordings:
                log.debug('update: %s: %s', l[0], l[5])
                self.__recordings[key].update(*l)
            else:
                log.debug('new: %s', l[0])
                self.__recordings[key] = Recording(*l)
        self.__request_description()
        return True


    def __describe_callback(self, result):
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return
        rec = result.arguments
        self.last_update = time.time()
        description = {}
        description['title'] = Unicode(rec[1], 'UTF-8')
        description['start_padding'] = rec[7]
        description['stop_padding'] = rec[8]
        for key, value in dict(rec[9]).items():
            description[key] = Unicode(value, 'UTF-8')
        key = '%s-%s-%s' % (rec[2], rec[4], rec[5])
        self.__recordings[key].description = description
        self.__request_description()


    def __request_description(self):
        if not self.server:
            self.updating = 0
            return

        self.updating = 2

        for key in self.__recordings:
            if not self.__recordings[key].description:
                cb = self.__describe_callback
                self.server.call('recording.describe', cb,
                                 self.__recordings[key].id)
                return

        log.info('got all recording descriptions')


        # create coming up text list
        reclist = copy.copy(self.__recordings.values())
        reclist.sort(lambda x,y: cmp(x.start, y.start))
        self.comingup = ''
        self.running = ''

        for rec in reclist:
            if rec.status == SCHEDULED:
                self.comingup += u'%s\n' % Unicode(rec)
            if rec.status == RECORDING:
                self.running += u'%s\n' % Unicode(rec)

        self.updating = 0


    def get(self, channel, start, stop):
        key = '%s-%s-%s' % (channel, start, stop)
        if key in self.__recordings:
            return self.__recordings[key]
        return None


    def list(self):
        return self.__recordings.values()


    def wait_on_list(self, timeout=5):
        self.updating = 1
        wait_start = time.time()

        while self.updating:
            if time.time() > wait_start + timeout:
                log.warning('timed out waiting for list update')
                self.updating = 0
                break

            time.sleep(0.01)
            notifier.step()

        return self.__recordings.values()


    def schedule(self, prog):
        if not self.server:
            return False, 'Recordserver unavailable'
        info = {}
        if prog.description:
            info['description'] = prog.description
        if prog.subtitle:
            info['subtitle'] = prog.subtitle
        try:
            return self.server.call('recording.add', None, prog.title,
                                    prog.channel.id, 1000, prog.start,
                                    prog.stop, info)
        except mcomm.MException, e:
            log.error(e)
            return False, 'Internal server error'
        except Exception, e:
            log.error(e)
            return False, 'Internal client error'


    def remove(self, id):
        if not self.server:
            return False, 'Recordserver unavailable'
        try:
            return self.server.call('recording.remove', None, id)
        except mcomm.MException, e:
            log.error(e)
            return False, 'Internal server error'
        except Exception, e:
            log.error(e)
            return False, 'Internal client error'





class Favorite(object):
    """
    A favorite object from the recordserver.
    """
    def __init__(self, id, title, channels, priority, day, time, one_shot,
                 substring):
        """
        The init function creates the object. The parameters are the complete
        list of the favorite.list rpc return.
        """
        self.id = id
        self.titel = title
        self.channels = channels
        self.priority = priority
        self.day = day
        self.time = time
        self.one_shot = one_shot
        self.substring = substring
        self.description = {}


class Favorites(object):
    """
    Handling of favorites from the recordserver. The object will auto sync with
    the recordserver to keep the list up to date.
    """
    def __init__(self):
        self.last_update = time.time()
        self.__favorites = []
        self.server = None
        mcomm.register_entity_notification(self.__entity_update)


    def __entity_update(self, entity):
        if not entity.present and entity == self.server:
            self.server = None
            return

        if entity.present and \
               entity.matches(mcomm.get_address('recordserver')):
            self.server = entity
            self.server.call('favorite.list', self.__list_callback)


    def __list_callback(self, result):
        if not self.server:
            return
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return

        self.last_update = time.time()
        self.__favorites = []
        for l in result.arguments:
            self.__favorites.append(Favorite(*l))
        log.info('got favorite list')


    def add(self, prog):
        if not self.server:
            return False, 'Recordserver unavailable'
        try:
            if prog.channel == 'ANY':
                channel = []
                for c in config.TV_CHANNELS:
                    channel.append(c[0])
            else:
                channel = [ prog.channel.id ]
            days = (_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'),
                    _('Sat'), _('Sun'))
            if prog.days in days:
                days = [ Unicode(days.index(prog.dow)) ]
            else:
                days = [ 0, 1, 2, 3, 4, 5, 6 ]

            return self.server.call('favorite.add', None, prog.title, channel,
                                    50, days, [ '00:00-23:59' ], False)
        except mcomm.MException, e:
            log.error(e)
            return False, 'Internal server error'
        except Exception, e:
            log.error(e)
            return False, 'Internal client error'


# the two objects handling recordings and favorites
recordings = Recordings()
favorites  = Favorites()
