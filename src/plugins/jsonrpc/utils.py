# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# utils.py - Helper functions for jsonrpc
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

# ka imports
import kaa
import kaa.beacon

cachedir = ''
imagedir = ''

# get logging object
log = logging.getLogger('freevo')

def register_image(image, item=None):
    """
    Register image for HTTP.
    """
    if not image:
        return ''
    filename = image
    if isinstance(image, kaa.beacon.Thumbnail):
        filename = image.name
    if filename.startswith(imagedir):
        return os.path.join('beacon', filename[len(imagedir)+1:])
    if filename.startswith(cachedir):
        return os.path.join('cache', filename[len(cachedir)+1:])
    if isinstance(image, kaa.beacon.Thumbnail) and item:
        return os.path.join('thumbnail', item._beacon_id[0], str(item._beacon_id[1]))
    log.error('unsupported image: %s' % image)
    return ''

PROPERTY_NOT_FOUND = object()

def fill_basic_item_properties(item, properties):
    """
    Fill basic item properties
    """
    result = { 'label': item.get('title') }
    if item.get('series') and item.get('episode'):
        result = { 'label': '%s %sx%02d - %s' % \
           (item.get('series'), item.get('season'), item.get('episode'), item.get('title')) }
    for prop in properties[:]:
        value = PROPERTY_NOT_FOUND
        if prop in ('cast', 'artist', 'director', 'genre', 'writer', 'studio'):
            value = []
        if prop == 'plot':
            value = item.get('description')
        if prop == 'showtitle':
            value = item.get('series') or ''
        if prop == 'title':
            value = item.get('title')
        if prop in ('track', 'season', 'episode'):
            value = int(item.get(prop) or -1)
        if prop in ('year', ):
            value = 0
        if prop == 'file':
            value = item.get('url') or ''
        if prop == 'rating':
            value = 0.0
        if prop == 'thumbnail':
            value = register_image(item.get('image'))
        if prop == 'tagline':
            value = ''
        if prop == 'fanart':
            value = register_image(item.background)
        if prop == 'imdbnumber':
            value = (item.webmetadata and item.webmetadata.imdb) or ''
        if prop in ('album', 'albumartist', 'originaltitle'):
            value = ''
        if prop == 'type':
            if item.get('series') and item.get('episode'):
                value = 'episode'
            else:
                log.error('unsupported type')
                value = ''
        if value != PROPERTY_NOT_FOUND:
            result[prop] = value
            properties.remove(prop)
    return result
