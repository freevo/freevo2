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

# internal regexp for time format
_time_re = re.compile('([0-9]*):([0-9]*)-([0-9]*):([0-9]*)')

class Favorite:
    """
    Base class for a favorite.
    """
    def __init__(self, id = -1, name = 'unknown', channels = [],
                 priority = 0, days = [], times = [], once = False):
        self.id       = id
        self.name     = name
        self.channels = channels
        self.priority = priority
        self.days     = days
        self.times    = []
        self.once     = once
        for t in times:
            m = _time_re.match(t).groups()
            start = int(m[0])*100 + int(m[1])
            stop  = int(m[2])*100 + int(m[3])
            self.times.append((start, stop))

    def short_list(self):
        """
        Return a short list with informations about the favorite.
        """
        return self.id, self.name, self.priority


    def long_list(self):
        """
        Return a long list with every information about the favorite.
        """
        return self.id, self.name, self.channels, self.priority, self.days, \
               self.times, self.once


    def parse_fxd(self, parser, node):
        """
        Parse informations from a fxd node and set the internal variables.
        """
        self.id = int(parser.getattr(node, 'id'))
        for child in node.children:
            for var in ('name', 'channel'):
                if child.name == var:
                    setattr(self, var, parser.gettext(child))
            if child.name == 'once':
                self.once = True
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
        """
        Return True if name, channel and start match this favorite.
        """
        if name != self.name:
            return False
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
        """
        A simple string representation for a favorite for debugging in the
        recordserver.
        """
        name = self.name
        if len(name) > 45:
            name = name[:45] + u'...'
        name = u'"' + name + u'"'
        if self.once:
            once = '(schedule once)'
        else:
            once = ''
        return '%3d %-45s %4d %s' % \
               (self.id, String(name), self.priority, once)


    def __fxd__(self, fxd):
        """
        Dump informations about the favorite in a fxd file node.
        """
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
        if self.once:
            subnode = fxdparser.XMLnode('once')
            fxd.add(subnode, node)
        return node

    def __cmp__(self, obj):
        """
        Compare basic informations between Favorite objects
        """
        if not isinstance(obj, Favorite):
            return True
        return self.name != obj.name or self.channels != obj.channels or \
               self.days != obj.days or self.times != obj.times

