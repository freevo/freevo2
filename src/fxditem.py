# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# fxditem.py - Create items out of fxd files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
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
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.15  2004/11/01 20:14:14  dischi
# fix debug
#
# Revision 1.14  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.13  2004/02/14 19:28:07  dischi
# store display_type in Container to build nicer menu
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */


import copy
import traceback

import config
import util
import item
import plugin
import os
import stat


class Mimetype(plugin.MimetypePlugin):
    """
    class to handle fxd files in directories
    """
    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        # get the list of fxd files
        fxd_files = util.find_matches(files, ['fxd'])

        # removed covered files from the list
        for f in fxd_files:
            try:
                files.remove(f)
            except:
                pass
            
        # check of directories with a fxd covering it
        for d in copy.copy(files):
            if os.path.isdir(d):
                f = os.path.join(d, os.path.basename(d) + '.fxd')
                if vfs.isfile(f):
                    fxd_files.append(f)
                    files.remove(d)

        # return items
        if fxd_files:
            return self.parse(parent, fxd_files, files)
        else:
            return []


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'fxd' ]

    
    def count(self, parent, files):
        """
        return how many items will be build on files
        """
        return len(self.get(parent, files))

    
    def parse(self, parent, fxd_files, duplicate_check=[], display_type=None):
        """
        return a list of items that belong to a fxd files
        """
        if not display_type and hasattr(parent, 'display_type'):
            display_type = parent.display_type
            if display_type == 'tv':
                display_type = 'video'

        callbacks = plugin.get_callbacks('fxditem')
        items = []
        for fxd_file in fxd_files:
            try:
                # create a basic fxd parser
                parser = util.fxdparser.FXD(fxd_file)

                # create items attr for return values
                parser.setattr(None, 'items', [])
                parser.setattr(None, 'parent', parent)
                parser.setattr(None, 'filename', fxd_file)
                parser.setattr(None, 'duplicate_check', duplicate_check)
                parser.setattr(None, 'display_type', display_type)

                for types, tag, handler in callbacks:
                    if not display_type or not types or display_type in types:
                        parser.set_handler(tag, handler)

                # start the parsing
                parser.parse()

                # return the items
                items += parser.getattr(None, 'items')

            except:
                _debug_("fxd file %s corrupt" % fxd_file, 0)
                traceback.print_exc()
        return items



# -------------------------------------------------------------------------------------

class Container(item.Item):
    """
    a simple container containing for items parsed from the fxd
    """
    def __init__(self, fxd, node):
        fxd_file = fxd.filename
        item.Item.__init__(self, fxd.getattr(None, 'parent', None))

        self.items    = []
        self.name     = fxd.getattr(node, 'title', 'no title')
        self.type     = fxd.getattr(node, 'type', '')
        self.fxd_file = fxd_file
        
        self.image    = fxd.childcontent(node, 'cover-img')
        if self.image:
            self.image = vfs.join(vfs.dirname(fxd_file), self.image)

        parent_items  = fxd.getattr(None, 'items', [])
        display_type  = fxd.getattr(None, 'display_type', None)

        # set variables new for the subtitems
        fxd.setattr(None, 'parent', self)
        fxd.setattr(None, 'items', self.items)

        callbacks = plugin.get_callbacks('fxditem')

        for child in node.children:
            for types, tag, handler in callbacks:
                if (not display_type or not types or display_type in types) and \
                       child.name == tag:
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
        return [ ( self.browse, _('Browse list')) ]


    def browse(self, arg=None, menuw=None):
        """
        show all items
        """
        import menu
        moviemenu = menu.Menu(self.name, self.items, item_types=self.display_type)
        menuw.pushmenu(moviemenu)

        

def container_callback(fxd, node):
    """
    handle <container> tags. Inside this tag all other base level tags
    like <audio>, <movie> and <container> itself will be parsed as normal.
    """
    c = Container(fxd, node)
    if c.items:
        fxd.getattr(None, 'items', []).append(c)
    


# -------------------------------------------------------------------------------------

plugin.register_callback('fxditem', None, 'container', container_callback)
mimetype = Mimetype()
plugin.activate(mimetype, level=0)

