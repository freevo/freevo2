# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# grabberitem.py - Basic item from grabbers
# -----------------------------------------------------------------------------
# $Id$
#
# Notes: The unicode stuff is _not_ verified!
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
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

import config
import copy
import htmlentitydefs
from types import StringTypes

class GrabberItem(object):

    def __init__(self):
        pass

    def __getitem__(self, attr):
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]

        return None


    def to_unicode(self):
        """
        Set all string attributes to unicode
        """
        for a in self.__dict__.keys():
            if isinstance(self.__dict__[a], StringTypes):
                # it's a string, convert it to unicode
                self.__dict__[a] = self.htmlenties2txt(self.__dict__[a].strip())

    def __str__(self):
        val = []
        for a in self.__dict__.keys():
            if isinstance(self.__dict__[a], StringTypes):
                val.append('%s: %s' % (a, self.__dict__[a]) )
        return '\n'.join(val)

    def htmlenties2txt(self, string):
        """
        Converts a string to a string with all html entities resolved.
        Returns the result as Unicode object (that may conatin chars outside 256
        """
        e = copy.deepcopy(htmlentitydefs.entitydefs)
        e['ndash'] = "-";
        e['bull'] = "-";
        e['rsquo'] = "'";
        e['lsquo'] = "`";
        e['hellip'] = '...'
    
        string = Unicode(string).replace("&#039", "'").replace("&#146;", "'")
    
        i = 0
        while i < len(string):
            amp = string.find("&", i) # find & as start of entity
            if amp == -1: # not found
                break
            i = amp + 1
    
            semicolon = string.find(";", amp) # find ; as end of entity
            if string[amp + 1] == "#": # numerical entity like "&#039;"
                entity = string[amp:semicolon+1]
                replacement = Unicode(unichr(int(entity[2:-1])))
            else:
                entity = string[amp:semicolon + 1]
                if semicolon - amp > 7:
                    continue
                try:
                    # the array has mappings like "Uuml" -> "ü"
                    replacement = e[entity[1:-1]]
                except KeyError:
                    continue
            string = string.replace(entity, replacement)
        return string
                