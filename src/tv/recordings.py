# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recordings.py -
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
import mcomm
import config

server = None

def add_favorite(prog):
    if not server:
        return False, 'Recordserver unavailable'
    try:
        if prog.channel == 'ANY':
            channel = []
            for c in config.TV_CHANNELS:
                channel.append(c[0])
        else:
            channel = [ prog.channel.chan_id ]
        days = (_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'),
                _('Sat'), _('Sun'))
        if prog.days in days:
            days = [ Unicode(days.index(prog.dow)) ]
        else:
            days = [ 0, 1, 2, 3, 4, 5, 6 ]

        return server.favorite_add(prog.title, channel, 50, days,
                                   [ '00:00-23:59' ], False)
    except mcomm.MException, e:
        print e
        return False, 'Internal server error'
    except Exception, e:
        print 'recordings.add_favorite:', e
        return False, 'Internal client error'


def schedule_recording(prog):
    if not server:
        return False, 'Recordserver unavailable'
    info = {}
    if prog['description']:
        info['description'] = prog['description']
    if prog['subtitle']:
        info['subtitle'] = prog['subtitle']
    try:
        return server.recording_add(prog.title, prog.channel.chan_id, 1000,
                                    prog.start, prog.stop, info)
    except mcomm.MException, e:
        print e
        return False, 'Internal server error'
    except Exception, e:
        print 'recordings.schedule_recording:', e
        return False, 'Internal client error'


def remove_recording(prog):
    if not server:
        return False, 'Recordserver unavailable'
    try:
        return server.recording_remove(prog.scheduled[0])
    except mcomm.MException, e:
        print e
        return False, 'Internal server error'
    except Exception, e:
        print 'recordings.schedule_recording:', e
        return False, 'Internal client error'


recordings = {}

def record_describe_callback(result):
    status, rec = result[0][1:]
    if status[0] == 'FAILED' or status[1] != 'OK':
        print status
        return

    key = '%s%s%s' % (rec[2], rec[4], rec[5])
    recordings[key] = rec


def record_list_callback(result):
    if not server:
        return

    status, listing = result[0][1:]
    if status[0] == 'FAILED' or status[1] != 'OK':
        print status
        return

    for l in listing:
        server.recording_describe(l[0], callback=record_describe_callback)


recordings = {}

def favorite_list_callback(result):
    if not server:
        return

    status, listing = result[0][1:]
    if status[0] == 'FAILED' or status[1] != 'OK':
        print status
        return


def notification(entity):
    global server
    if not entity.present and entity == server:
        print 'recordserver lost'
        server = None
        return

    if entity.present and entity.matches(mcomm.get_address('recordserver')):
        print 'recordserver found'
        server = entity
        server.recording_list(callback=record_list_callback)
        server.favorite_list(callback=favorite_list_callback)

mcomm.register_entity_notification(notification)
