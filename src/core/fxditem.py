# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxditem.py - Create items out of fxd files
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
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
# -----------------------------------------------------------------------------

__all__ = [ 'add_fxdparser' ]

# python imports
import copy
import logging
import os

# kaa imports
import kaa

# freevo core imports
import fxdparser

# freevo imports
import api as freevo

# get logging object
log = logging.getLogger()


class Container(freevo.Item):
    """
    A simple container containing for items parsed from the fxd
    """
    def __init__(self, title, image, info, parent, type):
        super(Container, self).__init__(parent)
        self.items = []
        self.name = title
        self.image = image
        self.media_type = type


    def actions(self):
        """
        Actions for this item
        """
        return [ freevo.Action(_('Browse list'), self.browse) ]


    def browse(self):
        """
        Show all items
        """
        m = freevo.Menu(self.name, self.items, type=self.media_type)
        self.get_menustack().pushmenu(m)



class PluginInterface(freevo.MediaPlugin):
    """
    Class to handle fxd files in directories
    """

    def __init__(self):
        super(PluginInterface, self).__init__()
        self._callbacks = []


    def get(self, parent, listing):
        """
        Return a list of items based on the listing
        """
        files = listing.get('fxd')
        if not files:
            return []

        # get media_type from parent
        media_type = getattr(parent, 'media_type', None)
        if media_type == 'tv':
            media_type = 'video'

        items = []
        for fxd in files:
            try:
                doc = fxdparser.Document(fxd.filename)
                items.extend(self._parse(doc, parent, listing, media_type))
            except:
                log.exception("fxd file %s corrupt" % fxd.filename)
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


    def add_parser(self, types, node, callback):
        """
        Add a node parser for fxd files.
        """
        self._callbacks.append((types, node, callback))


    def _parse(self, node, parent, listing, media_type):
        """
        Internal parser function
        """
        items = []
        dirname = node.root.dirname
        for c in node:
            c.dirname = dirname
            c.title = c.getattr('title') or ''
            c.image = None
            c.info = {}
            for attr in c.children:
                if attr.name == 'cover-img' and attr.content:
                    image = os.path.join(dirname, kaa.unicode_to_str(attr.content))
                    if os.path.isfile(image):
                        c.image = image
                if attr.name == 'info':
                    for i in attr.children:
                        c.info[str(i.name)] = i.content

            for types, tag, handler in self._callbacks:
                if media_type and types and not media_type in types:
                    # wrong type
                    continue
                if tag == c.name:
                    i = handler(c, parent, listing)
                    if i is not None:
                        items.append(i)
            if c.name == 'container':
                con = Container(c.title, c.image, c.info, parent, media_type)
                con.items = self._parse(c, con, listing, media_type)
                if con.items:
                    items.append(con)
        return items



# load the MediaPlugin
interface = PluginInterface()
add_parser = interface.add_parser
add_fxdparser = interface.add_parser
freevo.activate_plugin(interface, level=0)
