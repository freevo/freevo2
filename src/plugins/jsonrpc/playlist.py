# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# playlist.py - jsonrpc interface for XBMC-compatible remotes
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
import logging

# kaa imports
import kaa

# freevo imports
from ... import core as freevo

# jsonrpc imports
import utils

# get logging object
log = logging.getLogger('freevo')

def GetItems(playlistid, properties, limits):
    """
    JsonRPC Callback Playlist.GetItems
    """
    app = freevo.taskmanager.applications[-1]
    # Dummy playlist with current item. Fix this to use the actual
    # playlist in progress
    if app.name == 'menu':
        playlist = []
    elif app.name == 'videoplayer':
        playlist = [ freevo.taskmanager.applications[-1].item ]
    else:
        playlist = []
        log.error('unsupported application %s' % app)
    result = []
    for item in playlist:
        _properties = properties[:]
        result.append(utils.fill_basic_item_properties(app.item, _properties))
        for prop in _properties:
            if prop == 'playcount':
                value = 0
            elif prop == 'duration':
                value = app.item.info.get('length')
            else:
                log.error('no support for %s' % prop)
                value = ''
            result[-1][prop] = value
    start = limits['start']
    end = min(limits['end'], len(result))
    return {
        'limits': {'start': start, 'end': end, 'total': len(result)},
        'items': result[start:end+1] }
