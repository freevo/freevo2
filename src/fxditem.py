# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxditem.py - Create items out of fxd files
# -----------------------------------------------------------------------------
# $Id$
#
# If you want to expand the fxd file with a new tag below <freevo>, you
# can register a callback here. Create a class based on FXDItem (same
# __init__ signature). The 'parser' is something from util.fxdparser, which
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
import plugin
import os
import mediadb

from menu import Item, Action, Menu

# get logging object
log = logging.getLogger()

# the parser for fxd nodes
callbacks = []

def add_parser(types, node, callback):
    """
    Add a node parser for fxd files.
    """
    callbacks.append((types, node, callback))

    
class Mimetype(plugin.MimetypePlugin):
    """
    class to handle fxd files in directories
    """
    def get(self, parent, listing):
        """
        return a list of items based on the listing
        """
        # Get the list of fxd files. Get by extention (.fxd) and
        # by type (fxd file with the same name as the dir inside it)
        fxd_files = listing.match_suffix(['fxd']) + \
                    listing.match_type('fxd')

        # return items
        if fxd_files:
            return self.parse(parent, fxd_files, listing)
        else:
            return []


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'fxd' ]


    def count(self, parent, listing):
        """
        return how many items will be build on files
        """
        return len(self.get(parent, listing))


    def parse(self, parent, fxd_files, listing, display_type=None):
        """
        return a list of items that belong to a fxd files
        """
        if not display_type and hasattr(parent, 'display_type'):
            display_type = parent.display_type
            if display_type == 'tv':
                display_type = 'video'

        items = []
        for fxd_file in fxd_files:
            try:
                # create a basic fxd parser
                parser = util.fxdparser.FXD(fxd_file.filename)

                # create items attr for return values
                parser.setattr(None, 'items', [])
                parser.setattr(None, 'parent', parent)
                parser.setattr(None, 'filename', fxd_file.filename)
                parser.setattr(None, 'listing', listing)
                parser.setattr(None, 'display_type', display_type)

                for types, tag, handler in callbacks:
                    if not display_type or not types or display_type in types:
                        parser.set_handler(tag, handler)

                # start the parsing
                parser.parse()

                # return the items
                items += parser.getattr(None, 'items')

            except:
                log.exception("fxd file %s corrupt" % fxd_file.filename)
        return items





class Container(Item):
    """
    a simple container containing for items parsed from the fxd
    """
    def __init__(self, fxd, node):
        fxd_file = fxd.filename
        Item.__init__(self, fxd.getattr(None, 'parent', None))

        self.items    = []
        self.name     = fxd.getattr(node, 'title', 'no title')
        self.type     = fxd.getattr(node, 'type', '')
        self.fxd_file = fxd_file

        self.image    = fxd.childcontent(node, 'cover-img')
        if self.image:
            self.image = os.path.join(os.path.dirname(fxd_file), self.image)

        parent_items  = fxd.getattr(None, 'items', [])
        display_type  = fxd.getattr(None, 'display_type', None)

        # set variables new for the subtitems
        fxd.setattr(None, 'parent', self)
        fxd.setattr(None, 'items', self.items)

        for child in node.children:
            for types, tag, handler in callbacks:
                if (not display_type or not types or display_type in types) \
                       and child.name == tag:
                    handler(fxd, child)
                    break

        fxd.parse_info(fxd.get_children(node, 'info', 1), self)

        # restore settings
        fxd.setattr(None, 'parent', self.parent)
        fxd.setattr(None, 'items', parent_items)

        self.display_type = display_type


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return '%s%s' % (os.stat(self.fxd_file).st_ctime, self.fxd_file)
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
        moviemenu = Menu(self.name, self.items, item_types=self.display_type)
        self.pushmenu(moviemenu)



def container_callback(fxd, node):
    """
    handle <container> tags. Inside this tag all other base level tags
    like <audio>, <movie> and <container> itself will be parsed as normal.
    """
    c = Container(fxd, node)
    if c.items:
        fxd.getattr(None, 'items', []).append(c)




# register the plugin as mimetype for fxd files
mimetype = Mimetype()
plugin.activate(mimetype, level=0)

# add fxd parser
add_parser(None, 'container', container_callback)
