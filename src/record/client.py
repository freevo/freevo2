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
import logging

import mcomm
import config

# get logging object
log = logging.getLogger('record')

from types import *

class Recording:
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
        
class Recordings:
    def __init__(self):
        self.last_update = time.time()
        self.__recordings = {}
        self.server = None
        mcomm.register_entity_notification(self.__entity_update)
        mcomm.register_event('record.list.update', self.__list_update)
        

    def __entity_update(self, entity):
        if not entity.present and entity == self.server:
            log.info('recordserver lost')
            self.server = None
            return

        if entity.present and \
               entity.matches(mcomm.get_address('recordserver')):
            log.info('recordserver found')
            self.server = entity
            self.server.recording_list(callback=self.__list_callback)


    def __list_callback(self, result):
        if not self.server:
            return
        try:
            status, listing = result[0][1:]
        except ValueError:
            return
        if status[0] == 'FAILED' or status[1] != 'OK':
            log.error(str(status))
            return

        self.last_update = time.time()
        self.__recordings = {}
        for l in listing:
            self.__recordings['%s-%s-%s' % (l[1], l[3], l[4])] = Recording(*l)
        log.info('got recording list')
        self.__request_description()
        

    def __list_update(self, result):
        log.info('got recording list update')
        for l in result.payload[0].args:
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
        try:
            status, rec = result[0][1:]
        except ValueError:
            return
        if status[0] == 'FAILED' or status[1] != 'OK':
            log.error(str(status))
            return
        self.last_update = time.time()
        description = dict(rec[9])
        description['title'] = rec[1]
        description['start_padding'] = rec[7]
        description['stop_padding'] = rec[8]
        key = '%s-%s-%s' % (rec[2], rec[4], rec[5])
        self.__recordings[key].description = description
        self.__request_description()


    def __request_description(self):
        if not self.server:
            return
        for key in self.__recordings:
            if not self.__recordings[key].description:
                cb = self.__describe_callback
                self.server.recording_describe(self.__recordings[key].id,
                                               callback=cb)
                return
        log.info('got all recording descriptions')
        return
        
        
    def get(self, channel, start, stop):
        key = '%s-%s-%s' % (channel, start, stop)
        if key in self.__recordings:
            return self.__recordings[key]
        return None


    def schedule(self, prog):
        if not self.server:
            return False, 'Recordserver unavailable'
        info = {}
        if prog['description']:
            info['description'] = prog['description']
        if prog['subtitle']:
            info['subtitle'] = prog['subtitle']
        try:
            return self.server.recording_add(prog.title, prog.channel.id, 1000,
                                             prog.start, prog.stop, info)
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
            return self.server.recording_remove(id)
        except mcomm.MException, e:
            log.error(e)
            return False, 'Internal server error'
        except Exception, e:
            log.error(e)
            return False, 'Internal client error'





class Favorite:
    def __init__(self, id, title, channels, priority, day, time, one_shot):
        self.id = id
        self.titel = title
        self.channels = channels
        self.priority = priority
        self.day = day
        self.time = time
        self.one_shot = one_shot
        self.description = {}


class Favorites:
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
            self.server.favorite_list(callback=self.__list_callback)


    def __list_callback(self, result):
        if not self.server:
            return
        try:
            status, listing = result[0][1:]
        except ValueError:
            return
        if status[0] == 'FAILED' or status[1] != 'OK':
            log.error(str(status))
            return

        self.last_update = time.time()
        self.__favorites = []
        for l in listing:
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

            return self.server.favorite_add(prog.title, channel, 50, days,
                                            [ '00:00-23:59' ], False)
        except mcomm.MException, e:
            log.error(e)
            return False, 'Internal server error'
        except Exception, e:
            log.error(e)
            return False, 'Internal client error'


recordings = Recordings()
favorites  = Favorites()
