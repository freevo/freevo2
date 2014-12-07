# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# jsonrpc - jsonrpc interface for XBMC-compatible remotes
# -----------------------------------------------------------------------
# $Id$
#
# JSONRPC and XBMC eventserver to be used for XBMC-compatible
# remotes. Only tested with Yatse so far. If something is not working,
# do not blame the remote, blame this plugin.
#
# Not all API calls are implemented yet.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2014 Dirk Meyer, et al.
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
# ----------------------------------------------------------------------- */

# python imports
import os
import logging
import socket
import urllib

# kaa imports
import kaa
import kaa.beacon

# freevo imports
from ... import core as freevo

# get logging object
log = logging.getLogger('freevo')

# generic functions
import utils
import eventserver

# jsonrpc callbacks
import videolibrary as VideoLibrary
import player as Player
import playlist as Playlist

class PluginInterface( freevo.Plugin ):
    """
    JSONRPC and XBMC eventserver to be used for XBMC-compatible remotes
    """

    @kaa.coroutine()
    def plugin_activate(self, level):
        """
        Activate the plugin
        """
        super(PluginInterface, self).plugin_activate(level)
        self.httpserver = freevo.get_plugin('httpserver')
        if not self.httpserver:
            raise RuntimeError('httpserver plugin not running')
        self.httpserver.server.add_json_handler('/jsonrpc', self.jsonrpc)
        self.httpserver.server.add_handler('/image/', self.provide_image)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', freevo.config.plugin.jsonrpc.eventserver))
        udp = kaa.Socket()
        udp.wrap(self._sock, kaa.IO_READ | kaa.IO_WRITE)
        udp.signals['read'].connect(eventserver.handle)
        utils.imagedir = (yield kaa.beacon.get_db_info())['directory']
        utils.cachedir = os.path.join(os.environ['HOME'], '.thumbnails')
        self.api = {}
        for module in ('VideoLibrary', 'Player', 'Playlist'):
            for name in dir(eval(module)):
                method = getattr(eval(module), name)
                if callable(method) and not name.startswith('_'):
                    self.api[module + '.' + name] = method

    @kaa.coroutine()
    def provide_image(self, path, **attributes):
        """
        HTTP callback for images
        """
        filename = ''
        if path.startswith('beacon'):
            filename = os.path.join(utils.imagedir, path[7:])
        if path.startswith('cache'):
            filename = os.path.join(utils.cachedir, path[6:])
        if path.startswith('thumbnail'):
            item = yield kaa.beacon.query(id=int(path.split('/')[2]), type=path.split('/')[1])
            if len(item) != 1:
                log.error('beacon returned wrong results')
                yield None
            thumbnail = item[0].get('thumbnail')
            if thumbnail.needs_update or 1:
                yield kaa.inprogress(thumbnail.create(priority=kaa.beacon.Thumbnail.PRIORITY_HIGH))
            filename = thumbnail.large
        if filename:
            if os.path.isfile(filename):
                yield open(filename).read(), None, None
            log.error('no file: %s' % filename)
            yield None
        else:
            yield None

    def Application_GetProperties(self, properties):
        """
        JsonRPC Callback Application.GetProperties
        """
        result = {}
        for prop in properties:
            if prop == 'version':
                result[prop] = {"major": 13,"minor": 1,"revision": "f2acae7", "tag": "stable"}
            elif prop == 'volume':
                result[prop] = 100
            elif prop == 'muted':
                result[prop] = False
            else:
                raise AttributeError('unsupported property: %s' % prop)
        return result

    def XBMC_GetInfoBooleans(self, booleans):
        """
        JsonRPC Callback XBMC.GetInfoBooleans
        """
        result = {}
        for b in booleans:
            if b == 'System.Platform.Linux':
                result[b] = True
            else:
                result[b] = False
        return result

    def XBMC_GetInfoLabels(self, labels):
        """
        JsonRPC Callback XBMC.GetInfoLabels
        """
        result = {}
        for l in labels:
            if l == 'System.BuildVersion':
                result[l] = "13.1"
            elif l == 'System.KernelVersion':
                result[l] = "Linux 3.11.0"
            else:
                raise AttributeError('unsupported label: %s' % l)
        return result

    def XBMC_Ping(self):
        """
        JsonRPC Callback XBMC.GetInfoLabels
        """
        return ''

    @kaa.coroutine()
    def jsonrpc(self, path, **attributes):
        """
        HTTP callback for /jsonrpc
        """
        if not attributes:
            # supported XBMC API version
            yield {"major": 6,"minor": 14,"patch": 3}
        method = attributes.get('method')
        params = attributes.get('params')
        result = None
        callback = self.api.get(method, None) or getattr(self, method.replace('.', '_'), None)
        if callback:
            # log.info('%s(%s)' % (method, params))
            if params is None:
                result = callback()
            else:
                result = callback(**params)
            if isinstance(result, kaa.InProgress):
                result = yield result
            # log.info('returns %s' % str(result))
        else:
            raise AttributeError('unsupported method: %s' % method)
        yield {'jsonrpc': '2.0', 'result': result, 'id': attributes.get('id')}
