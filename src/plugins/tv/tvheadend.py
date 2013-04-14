# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# TVHeadEnd TV backend
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2013 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'init' ]

# python imports
import struct
import logging

# kaa imports
import kaa

# freevo imports
import freevo2

# get logging object
log = logging.getLogger('tv.tvheadend')


# For details how to communicate with tvheadend see
# https://www.lonelycoder.com/redmine/projects/tvheadend/wiki/Htsp

class binary(str):
    pass

class Backend(object):

    host = None

    def __init__(self):
        self._data = ''
        self._seq = 0
        self._requests = {}
        self.channels = []
        self._programs = {}
        self.connected = kaa.InProgress()

    @kaa.coroutine()
    def connect(self, host):
        self.host = host
        self.socket = kaa.Socket()
        self.socket.signals['read'].connect(self.__read)
        yield self.socket.connect((host, 9982))
        yield self.send('hello', htspversion=5, clientname='Freevo', clientversion='2.0git')
        self.send('enableAsyncMetadata', epg=1, async=False)
        yield self.connected

    @kaa.coroutine()
    def stream(self, channel):
        result = yield self.send('getTicket', channelId=channel['channelId'])
        yield 'http://%s:9981%s?ticket=%s' % (self.host, result['path'], result['ticket'])

    def send(self, command, **args):
        async = args.pop('async', True)
        self._seq += 1
        args['method'] = command
        args['seq'] = self._seq
        value = ''.join([self._encode(*i) for i in args.items()])
        if async:
            self._requests[self._seq] = kaa.InProgress()
        self.socket.write(struct.pack('>I', len(value)) + value)
        if async:
            return self._requests[self._seq]

    def _encode(self, key, value):
        # https://www.lonelycoder.com/redmine/projects/tvheadend/wiki/Htsmsgbinary
        if isinstance(value, unicode):
            value = str(value)
        if isinstance(value, binary):
            vtype = 4
        elif isinstance(value, str):
            vtype = 3
        elif isinstance(value, dict):
            value = ''.join([self._encode(*i) for i in value.items()])
            vtype = 1
        elif isinstance(value, int):
            value = struct.pack('q', value).rstrip('\00')
            vtype = 2
        else:
            raise AttributeError('unsupported type %s' % type(value))
        return struct.pack('bb', vtype, len(key)) + struct.pack('>I', len(value)) + key + value

    def _decode(self, data, result):
        # https://www.lonelycoder.com/redmine/projects/tvheadend/wiki/Htsmsgbinary
        vtype, nlen = struct.unpack('bb', data[:2])
        dlen = struct.unpack('>I', data[2:6])[0]
        key = data[6:6+nlen]
        value = data[6+nlen:6+nlen+dlen]
        if vtype == 1:
            r = {}
            while value:
                value = self._decode(value, r)
            value = r
        elif vtype == 2:
            value = struct.unpack('q', value.ljust(8, '\00'))[0]
        elif vtype == 3:
            pass
        elif vtype == 4:
            value = binary(value)
        elif vtype == 5:
            r = []
            while value:
                value = self._decode(value, r)
            value = r
        else:
            log.error('unsupported type %s', vtype)
            value = None
        if isinstance(result, list):
            result.append(value)
        else:
            result[key] = value
        return data[6+nlen+dlen:]

    def __read(self, data):
        self._data += data
        while True:
            if len(self._data) < 4:
                return
            length = struct.unpack('>I', self._data[:4])[0]
            if length > len(self._data[4:]):
                return
            data = self._data[4:4+length]
            result = {}
            while data:
                data = self._decode(data, result)
            if 'seq' in result and result['seq'] in self._requests:
                inprogress = self._requests.pop(result['seq'])
                inprogress.finish(result)
            elif 'method' in result:
                if hasattr(self, 'event_' + result['method']):
                    getattr(self, 'event_' + result.pop('method'))(result)
                else:
                    log.error('unsupported method %s', result.get('method'))
            self._data = self._data[4+length:]

    def event_eventAdd(self, result):
        self._programs[result['eventId']] = result

    def event_channelAdd(self, result):
        self.channels.append(result)

    def event_initialSyncCompleted(self, result):
        self.connected.finish(None)

def init():
    if not freevo2.config.tv.tvheadend.server:
        return None
    backend = Backend()
    backend.connect(freevo2.config.tv.tvheadend.server)
    return backend
