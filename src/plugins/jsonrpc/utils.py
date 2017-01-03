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
import kaa.webmetadata

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


def fill_video_details(stream, metadata):
    """
    Helper function to provide video stream details
    """
    result = {
        'aspect': stream.aspect, 
        'duration': int(metadata.length),
        'height': stream.height, 
        'width': stream.width, 
        'stereomode': '',
        'codec': stream.codec.lower().replace('h.264 avc', 'h264')}
    if hasattr(metadata, 'stereo') and metadata.stereo:
        result['stereomode'] = 'left_right'
    return result

def fill_audio_details(a):
    """
    Helper function to provide audio stream details
    """
    result = {
        'bitrate': int(a.get('samplerate') or 0),
        'channels': a.get('channels') or 2,
        'codec': a.get('codec').lower() or '',
        'index': a.get('id') or 0,
        'language': a.get('langcode') or 'unknown',
        'name': a.get('language') or 'unknown'}
    if result['language'] == 'und':
        result['language'] = 'unknown'
    if result['name'] == 'Undetermined':
        result['name'] = 'unknown'
    if result['codec'].startswith('dolby dts'):
        result['codec'] = 'dca'
    return result

def fill_subtitle_details(s):
    """
    Helper function to provide subtitle stream details
    """
    return {
        'index': s.get('id') or 0,
        'language': s.get('langcode') or 'und',
        'name': s.get('language') or 'Undetermined'}

def fill_basic_item_properties(item, properties):
    """
    Fill basic item properties
    """
    if not 'type' in properties:
        properties.append('type')
    result = { 'label': item.get('title') }
    if item.get('series') and item.get('episode'):
        result = { 'label': '%s %sx%02d - %s' % \
           (item.get('series'), item.get('season'), item.get('episode'), item.get('title')) }
    for prop in properties[:]:
        value = PROPERTY_NOT_FOUND
        if prop in ('cast', 'artist', 'director', 'genre', 'writer', 'studio'):
            value = []
        if prop in ('plot', 'description'):
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
            value = register_image(hasattr(item, 'background') and item.background)
        if prop == 'imdbnumber':
            value = (hasattr(item, 'webmetadata') and item.webmetadata and item.webmetadata.imdb) or ''
        if prop in ('album', 'albumartist', 'originaltitle'):
            value = ''
        if prop in ('duration', 'runtime'):
            value = item.info.get('length')
        if prop == 'art':
            value = {}
            fanart = register_image(hasattr(item, 'background') and item.background)
            if fanart:
                value['fanart'] = fanart
            if item.get('series') and item.get('episode'):
                series = item.get('series')
                series = kaa.webmetadata.tv.series(series)
                if series:
                    if series.banner:
                        value['tvshow.banner'] = register_image(series.banner)
                    if series.image:
                        value['tvshow.fanart'] = register_image(series.image)
                        value['fanart'] = register_image(series.image)
                    if series.poster:
                        value['tvshow.poster'] = register_image(series.poster)
                        value['poster'] = register_image(series.poster)
            thumb = item.get('image')
            if thumb:
                value['thumb'] = register_image(thumb, item)
        if prop == 'type':
            if item.type == 'video':
                if item.get('series') and item.get('episode'):
                    value = 'episode'
                else:
                    value = 'movie'
            elif item.type == 'audio':
                value = 'song'
            elif item.type == 'image':
                value = 'picture'
            else:
                log.error('unsupported type')
                value = ''
        if prop in ('top250',):
            value = 0
        if prop in ('votes',):
            value = ''
        if value != PROPERTY_NOT_FOUND:
            result[prop] = value
            properties.remove(prop)
        result['id'] = 1
    return result
