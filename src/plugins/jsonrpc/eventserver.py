# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# eventserver.py - XBMC-compatible eventserver
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
import struct

# freevo imports
from ... import core as freevo
from ..input.eventmap import EVENTMAP

# get logging object
log = logging.getLogger('freevo')

# keymap used for the button mapping. If a key is not found the
# plugin.input EVENTMAP is used.
keymap = {
    'menu': {
        'title': freevo.MENU_SUBMENU,
        'back': freevo.MENU_BACK_ONE_MENU,
    },
    'videoplayer': {
        'back': freevo.STOP,
        'skipminus': freevo.Event(freevo.SEEK, -60),
        'reverse': freevo.Event(freevo.SEEK, -10),
        'forward': freevo.Event(freevo.SEEK, 10),
        'skipplus': freevo.Event(freevo.SEEK, 60),
        'left': freevo.Event(freevo.SEEK, -60),
        'right': freevo.Event(freevo.SEEK, 60),
        'info': freevo.TOGGLE_OSD,
        'display': freevo.VIDEO_CHANGE_ASPECT,
        }
}

def handle(data):
    """
    Callback for UDP eventserver events
    """
    header = struct.unpack('!4c2bhLLL', data[:20])
    if header[6] == 0x03:   # BUTTON
        key = data[38:].split('\0')[1]
        app = freevo.taskmanager.applications[-1]
        if app.name in keymap and key in keymap[app.name]:
            freevo.Event(keymap[app.name][key]).post(event_source='user')
            return True
        if app.eventmap in EVENTMAP and key.upper() in EVENTMAP[app.eventmap]:
            EVENTMAP[app.eventmap][key.upper()].post(event_source='user')
            return True
        log.error('unmapped key: %s' % key)
        return True
    if header[6] == 0x0A:   # ACTION
        action = data[33:].strip()
        if action.startswith('ActivateWindow'):
            window = action[action.find('(')+1:action.find(')')]
            if window == 'Pictures':
                freevo.Event(freevo.MENU_GOTO_MEDIA).post('image', event_source='user')
            elif window == 'MusicLibrary':
                freevo.Event(freevo.MENU_GOTO_MEDIA).post('audio', event_source='user')
            elif window == 'Videos,MovieTitles':
                freevo.Event(freevo.MENU_GOTO_MEDIA).post('video', 'movie', event_source='user')
            elif window == 'Videos,TvShowTitles':
                freevo.Event(freevo.MENU_GOTO_MEDIA).post('video', 'tv', event_source='user')
            elif window == 'Home':
                freevo.Event(freevo.MENU_GOTO_MAINMENU).post(event_source='user')
            else:
                log.error('ActivateWindow: unsupported window: %s' % window)
        else:
            log.error('unsupported eventserver action: %s' % action)
    else:
        log.error('unsupported packet type: %s' % int(header[6]))
