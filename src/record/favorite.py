# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# favorite.py -
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

import re
import time

import config
import util.fxdparser as fxdparser

_time_re = re.compile('([0-9]*):([0-9]*)-([0-9]*):([0-9]*)')

class Favorite:
    def __init__(self, id = -1, name = 'unknown', channels = [],
                 priority = 0, days = [], times = []):
        self.id = id
        self.name = name
        self.channels = channels
        self.priority = priority
        self.days = days
        self.times = []
        for t in times:
            m = _time_re.match(t).groups()
            start = int(m[0])*100 + int(m[1])
            stop  = int(m[2])*100 + int(m[3])
            self.times.append((start, stop))

    def short_list(self):
        return self.id, self.name, self.priority

    def long_list(self):
        return self.id, self.name, self.channels, self.priority, self.days, \
               self.times

    def parse_fxd(self, parser, node):
        self.id = int(parser.getattr(node, 'id'))
        for child in node.children:
            for var in ('name', 'channel'):
                if child.name == var:
                    setattr(self, var, parser.gettext(child))
            if child.name == 'channels':
                self.channels = []
                for v in parser.gettext(child).split(' '):
                    self.channels.append(v)
            if child.name == 'days':
                self.days = []
                for v in parser.gettext(child).split(' '):
                    self.days.append(int(v))
            if child.name == 'times':
                self.times = []
                for v in parser.gettext(child).split(' '):
                    m = _time_re.match(v).groups()
                    start = int(m[0])*100 + int(m[1])
                    stop  = int(m[2])*100 + int(m[3])
                    self.times.append((start, stop))
            if child.name == 'priority':
                setattr(self, 'priority', int(parser.gettext(child)))

    def match(self, name, channel, start):
        if name != self.name:
            return False
        # FIXME: correct channel in db
        for c in config.TV_CHANNELS:
            if c[0] == channel:
                channel = c[1]
                break
        if not channel in self.channels:
            return False
        timestruct = time.localtime(start)
        if not int(time.strftime('%w', timestruct)) in self.days:
            return False
        stime = int(timestruct[3]) * 100 + int(timestruct[4])
        for t1, t2 in self.times:
            if stime >= t1 and stime <= t2:
                return True
        return False


    def __str__(self):
        return String(self.short_list())


    def __fxd__(self, fxd):
        node = fxdparser.XMLnode('favorite', [ ('id', self.id ) ] )
        for var in ('name', 'priority'):
            subnode = fxdparser.XMLnode(var, [], getattr(self, var) )
            fxd.add(subnode, node)
        for var in ('channels', 'days'):
            s = ''
            for v in getattr(self, var):
                s += '%s ' % v
            subnode = fxdparser.XMLnode(var, [], s[:-1])
            fxd.add(subnode, node)
        s = ''
        for v in self.times:
            s += '%02d:%02d-%02d:%02d ' % (v[0] / 100, v[0] % 100,
                                           v[1] / 100, v[1] % 100)
            subnode = fxdparser.XMLnode('times', [], s[:-1])
            fxd.add(subnode, node)
        return node

    def __cmp__(self, obj):
        if not isinstance(obj, Favorite):
            return True
        return self.name != obj.name or self.channels != obj.channels or \
               self.days != obj.days or self.times != obj.times

