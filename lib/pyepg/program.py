# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# program.py - an epg program
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
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


class Program:
    """
    A Program with informations from the EPG.
    """
    def __init__(self, id, title, start, stop, episode, subtitle,
                 description, channel):
        self.title = title
        self.name  = self.title
        self.start = start
        self.stop  = stop

        self.channel     = channel
        self.id          = id
        self.subtitle    = subtitle
        self.description = description
        self.episode     = episode

        # TODO: add category support (from epgdb)
        self.categories = ''
        # TODO: add ratings support (from epgdb)
        self.ratings = ''


    def __cmp__(self, other):
        """
        Compare function, return 0 if the objects are identical, 1 otherwise
        """
        try:
            return Unicode(self.title) != Unicode(other.title) or \
                   self.start != other.start or \
                   self.stop  != other.stop or \
                   Unicode(self.channel) != Unicode(other.channel)
        except AttributeError:
            return 1


    def __str__(self):
        return '%8d %s (%s): %s-%s' % (self.id, self.title, self.channel.id,
                                       self.start, self.stop)
    
