# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recording.py -
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

import time

import util.fxdparser as fxdparser

_time_format = '%Y%m%d.%H:%M'

def _int2time(i):
    return time.strftime(_time_format, time.localtime(i))

def _time2int(s):
    return int(time.mktime(time.strptime(s, _time_format)))


class Recording:
    def __init__(self, id = -1, name = 'unknown', channel = 'unknown',
                 priority = 0, start = 0, stop = 0, filename = '/dev/null',
                 info = {}, status = 'scheduled' ):
        self.id       = id
        self.name     = name
        self.channel  = channel
        self.priority = priority
        self.start    = start
        self.stop     = stop
        self.filename = filename
        self.info     = info
        self.status   = status

    def short_list(self):
        return self.id, self.channel, self.priority, self.start, \
               self.stop, self.status


    def long_list(self):
        return self.id, self.name, self.channel, self.priority, self.start, \
               self.stop, self.filename, self.status, self.info


    def parse_fxd(self, parser, node):
        self.id = int(parser.getattr(node, 'id'))
        for child in node.children:
            for var in ('name', 'channel', 'status'):
                if child.name == var:
                    setattr(self, var, parser.gettext(child))
            if child.name == 'priority':
                self.priority = int(parser.gettext(child))
            if child.name == 'timer':
                self.start = _time2int(parser.getattr(child, 'start'))
                self.stop  = _time2int(parser.getattr(child, 'stop'))
        parser.parse_info(node, self)


    def __str__(self):
        return String(self.short_list())


    def __fxd__(self, fxd):
        node = fxdparser.XMLnode('recording', [ ('id', self.id ) ] )
        for var in ('name', 'channel', 'priority', 'filename', 'status'):
            subnode = fxdparser.XMLnode(var, [], getattr(self, var) )
            fxd.add(subnode, node)
        timer = fxdparser.XMLnode('timer', [ ('start', _int2time(self.start)),
                                             ('stop', _int2time(self.stop)) ])
        fxd.add(timer, node)
        info = fxdparser.XMLnode('info')
        for i in self.info:
            subnode = fxdparser.XMLnode(i, [], self.info[i] )
            fxd.add(subnode, info)
        fxd.add(info, node)
        return node

    def __cmp__(self, obj):
        if not isinstance(obj, Recording):
            return True
        return self.name != obj.name or self.channel != obj.channel or \
               self.start != obj.start or self.stop != obj.stop

