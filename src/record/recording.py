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
import copy

import config
import util.fxdparser as fxdparser

_time_format = '%Y%m%d.%H:%M'

def _int2time(i):
    """
    Helper function to create a time string from an int.
    """
    return time.strftime(_time_format, time.localtime(i))


def _time2int(s):
    """
    Helper function to create an int from a string created by _int2time
    """
    return int(time.mktime(time.strptime(s, _time_format)))


class Recording:
    """
    Base class for a recording.
    """
    def __init__(self, id = -1, name = 'unknown', channel = 'unknown',
                 priority = 0, start = 0, stop = 0, info = {},
                 status = 'scheduled' ):
        self.id       = id
        self.name     = name
        self.channel  = channel
        self.priority = priority
        self.start    = start
        self.stop     = stop
        self.status   = status
        self.info     = {}

        self.subtitle = ''
        self.url      = ''
        self.padding  = config.TV_RECORD_PADDING
        for i in info:
            if i in ('subtitle', 'url'):
                setattr(self, i, info[i])
            if i == 'padding':
                i.padding = int(info[i])
        self.recorder = None


    def short_list(self):
        """
        Return a short list with informations about the recording.
        """
        return self.id, self.channel, self.priority, self.start, \
               self.stop, self.status


    def long_list(self):
        """
        Return a long list with every information about the recording.
        """
        info = copy.copy(self.info)
        if self.subtitle:
            info['subtitle'] = self.subtitle
        if self.url:
            info['url'] = url
        return self.id, self.name, self.channel, self.priority, self.start, \
               self.stop, self.status, self.padding, info


    def parse_fxd(self, parser, node):
        """
        Parse informations from a fxd node and set the internal variables.
        """
        self.id = int(parser.getattr(node, 'id'))
        for child in node.children:
            for var in ('name', 'channel', 'status', 'subtitle', 'url'):
                if child.name == var:
                    setattr(self, var, parser.gettext(child))
            for var in ('priority', 'padding'):
                if child.name == var:
                    setattr(self, var, int(parser.gettext(child)))
            if child.name == 'timer':
                self.start = _time2int(parser.getattr(child, 'start'))
                self.stop  = _time2int(parser.getattr(child, 'stop'))
        parser.parse_info(node, self)


    def __str__(self):
        """
        A simple string representation for a recording for debugging in the
        recordserver.
        """
        channel = self.channel
        if len(channel) > 10:
            channel = channel[:10]
        diff = (self.stop - self.start) / 60
        name = self.name
        if len(name) > 23:
            name = name[:20] + u'...'
        name = u'"' + name + u'"'
        return '%3d %10s %-25s %4d %s-%s %s' % \
               (self.id, String(channel), String(name),
                self.priority, _int2time(self.start)[4:],
                _int2time(self.stop)[9:], self.status)


    def __fxd__(self, fxd):
        """
        Dump informations about the recording in a fxd file node.
        """
        node = fxdparser.XMLnode('recording', [ ('id', self.id ) ] )
        for var in ('name', 'channel', 'priority', 'url', 'status',
                    'subtitle', 'padding'):
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
        """
        Compare basic informations between Recording objects
        """
        if not isinstance(obj, Recording):
            return True
        return self.name != obj.name or self.channel != obj.channel or \
               self.start != obj.start or self.stop != obj.stop

