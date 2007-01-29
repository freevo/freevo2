# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxditem.py - Create items out of fxd files
# -----------------------------------------------------------------------------
# $Id$
#
# If you want to expand the fxd file with a new tag below <freevo>, you
# can register a callback here. Create a class based on FXDItem (same
# __init__ signature). The 'parser' is something from freevo.fxdparser, which
# gets the real callback. After parsing, the variable 'items' from the
# objects will be returned.
#
# Register your handler with the register function. 'types' is a list of
# display types (e.g. 'audio', 'video', 'images'), handler is the class
# (not an object of this class) which is a subclass of FXDItem.
#
# If the fxd files 'covers' a real item like the movie information cover
# real movie files, please do
# a) add the fxd file as 'fxd_file' memeber variable to the new item
# b) add the files as list _fxd_covered_ to the item
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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


# python imports
import copy
import logging

import util
from freevo.ui import plugin
import os
import freevo.fxdparser

from menu import Item, Action, Menu

# get logging object
log = logging.getLogger()

# the parser for fxd nodes
_callbacks = []

def add_parser(types, node, callback):
    """
    Add a node parser for fxd files.
    """
    _callbacks.append((types, node, callback))

    
class Mimetype(plugin.MimetypePlugin):
    """
    Class to handle fxd files in directories
    """
    def get(self, parent, listing):
        """
        Return a list of items based on the listing
        """
        fxd_files = listing.get('fxd')
        if not fxd_files:
            return []

        type = parent.display_type
        if type == 'tv':
            type = 'video'

        items = []
        for fxd_file in fxd_files:
            try:
                doc = freevo.fxdparser.FXD(fxd_file.filename)
                items.extend(self._parse(doc, doc, parent, listing, type))
            except:
                log.exception("fxd file %s corrupt" % fxd_file.filename)
                continue
        return items


    def suffix(self):
        """
        Return the list of suffixes this class handles
        """
        return [ 'fxd' ]


    def count(self, parent, listing):
        """
        Return how many items will be build on files
        """
        return len(self.get(parent, listing))


    def _parse(self, doc, node, parent, listing, display_type):
        """
        Internal parser function
        """
        items = []
        for c in doc.get_content(node):
            for types, tag, handler in _callbacks:
                if display_type and types and not display_type in types:
                    # wrong type
                    continue
                if tag == c.name:
                    i = handler(c, parent, listing)
                    if i is not None:
                        items.append(i)
            if c.name == 'container':
                con = Container(c.title, c.image, c.info, parent)
                con.items = self._parse(doc, c, con, listing, display_type)
                if con.items:
                    items.append(con)
        return items



class Container(Item):
    """
    a simple container containing for items parsed from the fxd
    """
    def __init__(self, title, image, info, parent):
        Item.__init__(self, parent)
        self.items = []
        self.name = title
        self.image = image
        self.display_type = parent.display_type
        

    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return '0'
        return self.name


    def actions(self):
        """
        actions for this item
        """
        return [ Action(_('Browse list'), self.browse) ]


    def browse(self):
        """
        show all items
        """
        moviemenu = Menu(self.name, self.items, type=self.display_type)
        self.pushmenu(moviemenu)



# register the plugin as mimetype for fxd files
mimetype = Mimetype()
plugin.activate(mimetype, level=0)
