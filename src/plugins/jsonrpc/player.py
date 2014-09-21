# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# player.py - jsonrpc interface for XBMC-compatible remotes
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
import kaa.candy
import kaa.beacon

# freevo imports
from ... import core as freevo
from ...plugins.video import VideoItem

# jsonrpc imports
import utils

# get logging object
log = logging.getLogger('freevo')

def _fill_audio_details(a):
    """
    Helper function to provide audio stream details
    """
    return {
        'bitrate': 0,
        'channels': a.get('channels') or 2,
        'codec': a.get('codec') or '',
        'index': a.get('id') or 0,
        'language': a.get('langcode') or 'und',
        'name': a.get('language') or 'Undetermined'}

def _fill_subtitle_details(s):
    """
    Helper function to provide subtitle stream details
    """
    return {
        'index': s.get('id') or 0,
        'language': s.get('langcode') or 'und',
        'name': s.get('language') or 'Undetermined'}

def GetActivePlayers():
    """
    JsonRPC Callback Player.GetActivePlayers
    """
    app = freevo.taskmanager.applications[-1].name
    if app == 'menu':
        return []
    if app == 'videoplayer':
        return [ { 'playerid': 1, 'type': 'video' }]
    log.error('unsupported application %s' % app)
    return []

def GetProperties(playerid, properties):
    """
    JsonRPC Callback Player.GetProperties
    """
    app = freevo.taskmanager.applications[-1]
    result = {}
    for prop in properties:
        if prop == 'audiostreams':
            result[prop] = []
            if app.name == 'videoplayer':
                if app.item.metadata.audio:
                    for a in app.item.metadata.audio:
                        result[prop].append(_fill_audio_details(a))
                else:
                    log.error('no audio stream')
            else:
                log.error('no audio stream')
        elif prop == 'canseek':
            result[prop] = True
        elif prop == 'currentaudiostream':
            result[prop] = {}
            if app.item.metadata.audio:
                result[prop] = _fill_audio_details(app.item.metadata.audio[0])
                if app.player.streaminfo.get('current-audio') is not None:
                    idx = app.player.streaminfo.get('current-audio')
                    if len(app.item.metadata.audio) > idx:
                        result[prop] = _fill_audio_details(app.item.metadata.audio[idx])
            else:
                log.error('no audio stream')
        elif prop == 'currentsubtitle':
            result[prop] = {}
            if app.player.streaminfo.get('current-subtitle') is not None:
                idx = app.player.streaminfo.get('current-subtitle')
                if idx >= 0 and len(app.item.metadata.subtitles) > idx:
                    result[prop] = _fill_subtitle_details(app.item.metadata.subtitles[idx])
                elif idx >= 0:
                    log.error('subtitle out of range')
        elif prop == 'partymode':
            result[prop] = False
        elif prop == 'playlistid':
            result[prop] = 1
        elif prop == 'position':
            result[prop] = 0
        elif prop == 'repeat':
            result[prop] = 'off'
        elif prop == 'shuffled':
            result[prop] = False
        elif prop == 'speed':
            if app.player.state == kaa.candy.STATE_PLAYING:
                result[prop] = 1
            else:
                result[prop] = 0
        elif prop == 'subtitleenabled':
            result[prop] = False
        elif prop == 'subtitles':
            result[prop] = []
            for s in app.item.metadata.subtitles:
                result[prop].append(_fill_subtitle_details(s))
        elif prop in ('time', 'totaltime'):
            item = getattr(app, 'item', None)
            if not item:
                val = 0
            elif prop == 'time':
                val = item.get('elapsed_secs') or 0
            else:
                val = item.info.get('length') or item.get('elapsed_secs') or 0
            result[prop] = {
                'hours': int(val) / 3600,
                'minutes': (int(val) / 60) % 60,
                'seconds': int(val) % 60,
                'milliseconds': int(val * 1000) % 1000}
        elif prop == 'type':
            result[prop] = 'video'
        else:
            raise AttributeError('unsupported property: %s' % prop)
    return result

def GetItem(playerid, properties):
    """
    JsonRPC Callback Player.GetItem
    """
    app = freevo.taskmanager.applications[-1]
    result = { 'label': app.item.get('title') }
    if app.item.get('series') and app.item.get('episode'):
        result = { 'label': '%s %sx%02d - %s' % \
           (app.item.get('series'), app.item.get('season'), app.item.get('episode'), app.item.get('title')) }
    for prop in properties:
        if prop in ('cast', 'artist', 'director', 'genre', 'writer', 'studio'):
            value = []
        elif prop == 'plot':
            value = app.item.get('description')
        elif prop == 'showtitle':
            value = app.item.get('series') or ''
        elif prop in ('title', 'showtitle', 'originaltitle'):
            value = app.item.get('title')
        elif prop == 'id':
            value = 0
        elif prop in ('track', 'season', 'episode'):
            value = int(app.item.get(prop) or -1)
        elif prop in ('year', ):
            value = 0
        elif prop == 'type':
            value = 'unknown'
        elif prop == 'file':
            value = app.item.get('url') or ''
        elif prop == 'streamdetails':
            value = {
                'audio': [],
                'subtitle': [],
                'video': [] }
            if app.name == 'videoplayer':
                for a in app.item.metadata.audio:
                    value['audio'].append({'channels': a.channels, 'codec': a.codec, 'language': a.langcode})
                for s in app.item.metadata.subtitles:
                    value['subtitle'].append(_fill_subtitle_details(s))
                for v in app.item.metadata.video:
                    value['video'].append({'aspect': v.aspect, 'duration': app.item.metadata.length,
                                           'height': v.height, 'width': v.width, 'stereomode': ''})
        elif prop == 'rating':
            value = 0.0
        elif prop == 'thumbnail':
            image = app.item.get('poster') or app.item.get('image')
            if image:
                value = utils.register_image(image)
            else:
                value = ''
        elif prop == 'tagline':
            value = ''          # FIXME
        elif prop == 'fanart':
            value = ''          # FIXME
        elif prop in ('album', 'albumartist', 'imdbnumber'):
            value = ''
        else:
            log.error('no support for %s' % prop)
            value = ''
        result[prop] = value
    return {'item': result }

def PlayPause(playerid, play):
    """
    JsonRPC Callback Player.PlayPause
    """
    app = freevo.taskmanager.applications[-1]
    if app.name == 'videoplayer':
        item = app.item
        if play == False and app.player.state == kaa.candy.STATE_PLAYING:
            freevo.Event(freevo.PAUSE).post()
            return 0
        if play == True and app.player.state == kaa.candy.STATE_PAUSED:
            freevo.Event(freevo.PLAY).post()
            return 1
    if play == False:
        return 0
    return 1

def SetSpeed(playerid, speed):
    """
    JsonRPC Callback Player.SetSpeed
    """
    return speed

def Stop(playerid):
    """
    JsonRPC Callback Player.Stop
    """
    freevo.Event(freevo.STOP).post()
    return ''

@kaa.coroutine()
def Open(item=None, options=None, shuffled=False, repeat=False, resume=False):
    """
    JsonRPC Callback Player.Open
    """
    if item and 'episodeid' in item:
        result = (yield kaa.beacon.query(id=item['episodeid'], type='video'))
        if len(result) != 1:
            log.error('bad query')
            yield ''
        VideoItem(result[0], None).play()
        yield ''
    log.error('unable to open %s' % str(item))

def SetAudioStream(playerid, stream):
    """
    JsonRPC Callback Player.SetAudioStream
    """
    app = freevo.taskmanager.applications[-1]
    app.player.set_audio(stream)

def SetSubtitle(playerid, subtitle):
    """
    JsonRPC Callback Player.SetSubtitle
    """
    app = freevo.taskmanager.applications[-1]
    if subtitle == 'off':
        app.player.set_subtitle(-1)
    if isinstance(subtitle, (int, long)):
        app.player.set_subtitle(subtitle)

def Seek(playerid, value):
    """
    JsonRPC Callback Player.Seek
    """
    app = freevo.taskmanager.applications[-1]
    app.player.seek(value, kaa.candy.SEEK_PERCENTAGE)
