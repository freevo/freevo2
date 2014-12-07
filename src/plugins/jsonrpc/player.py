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
    result = {
        'bitrate': int(a.get('samplerate') or 0),
        'channels': a.get('channels') or 2,
        'codec': a.get('codec').lower() or '',
        'index': a.get('id') or 0,
        'language': a.get('langcode') or 'unkown',
        'name': a.get('language') or 'unkown'}
    if result['language'] == 'und':
        result['language'] = 'unkown'
    if result['name'] == 'Undetermined':
        result['name'] = 'unkown'
    return result

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
            if app.name == 'videoplayer' and app.item.metadata.audio:
                result[prop] = _fill_audio_details(app.item.metadata.audio[0])
                if app.player.streaminfo.get('current-audio') is not None:
                    idx = app.player.streaminfo.get('current-audio')
                    if len(app.item.metadata.audio) > idx:
                        result[prop] = _fill_audio_details(app.item.metadata.audio[idx])
            else:
                log.error('no audio stream')
        elif prop == 'currentsubtitle':
            result[prop] = {}
            if app.name == 'videoplayer' and app.player.streaminfo.get('current-subtitle') is not None:
                idx = app.player.streaminfo.get('current-subtitle')
                if idx >= 0 and len(app.item.metadata.subtitles) > idx:
                    result[prop] = _fill_subtitle_details(app.item.metadata.subtitles[idx])
                elif idx >= 0:
                    log.error('subtitle out of range')
        elif prop == 'partymode':
            result[prop] = False
        elif prop == 'playlistid':
            result[prop] = 1    # FIXME
        elif prop == 'position':
            result[prop] = -1    # FIXME
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
            if app.name == 'videoplayer' and app.player.streaminfo.get('current-subtitle') is not None:
                result[prop] = True
            else:
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
            if app.name == 'videoplayer':
                if item.get('series') and item.get('episode'):
                    result[prop] = 'episode'
                else:
                    result[prop] = 'video'
            else:
                raise AttributeError('unsupported application')
        else:
            raise AttributeError('unsupported property: %s' % prop)
    return result

def GetItem(playerid, properties):
    """
    JsonRPC Callback Player.GetItem
    """
    app = freevo.taskmanager.applications[-1]
    if not 'type' in properties:
        properties.append('type')
    result = utils.fill_basic_item_properties(app.item, properties)
    result['id'] = 0
    for prop in properties:
        if prop == 'streamdetails':
            value = {
                'audio': [],
                'subtitle': [],
                'video': [] }
            if app.name == 'videoplayer':
                for a in app.item.metadata.audio:
                    value['audio'].append(_fill_audio_details(a))
                for s in app.item.metadata.subtitles:
                    value['subtitle'].append(_fill_subtitle_details(s))
                for v in app.item.metadata.video:
                    value['video'].append({'aspect': v.aspect, 'duration': int(app.item.metadata.length),
                                           'height': v.height, 'width': v.width, 'stereomode': '',
                                           'codec': v.codec.lower().replace('h.264 avc', 'h264')})
        else:
            log.error('no support for %s' % prop)
            value = ''
        result[prop] = value
    return {'item': result }

def PlayPause(playerid, play='toggle'):
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
        if play == 'toggle':
            if app.player.state == kaa.candy.STATE_PAUSED:
                freevo.Event(freevo.PLAY).post()
                return 1
            freevo.Event(freevo.PAUSE).post()
            return 0
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
