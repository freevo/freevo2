#if 0 /*
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
# a) add the fxd file as 'xml_file' memeber variable to the new item
# b) add the files as list _fxd_covered_ to the item
#
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/12/01 19:06:46  dischi
# better handling of the MimetypePlugin
#
# Revision 1.4  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
#
# Revision 1.3  2003/11/26 18:30:49  dischi
# <container> support
#
# Revision 1.2  2003/11/25 19:00:52  dischi
# make fxd item parser _much_ simpler
#
# Revision 1.1  2003/11/24 19:22:01  dischi
# a module with callbacks to create items out of an fxd file
#
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
#endif



import copy
import traceback

import config
import util
import item
import plugin


class Mimetype(plugin.MimetypePlugin):
    """
    class to handle fxd files in directories
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        if not hasattr(parent, 'display_type'):
            # don't know what to do here
            return []

        # get the list of fxd files
        fxd_files = util.find_matches(files, ['fxd'])
        for d in copy.copy(files):
            if vfs.isdir(d) and vfs.isfile(vfs.join(d, vfs.basename(d) + '.fxd')):
                fxd_files.append(vfs.join(d, vfs.basename(d) + '.fxd'))
                files.remove(d)

        # removed covered files from the list
        for f in fxd_files:
            if f in files:
                files.remove(f)

        # return items
        return self.parse(parent, fxd_files, files)



    def update(self, parent, new_files, del_files, new_items, del_items, current_items):
        """
        update a directory. Add items to del_items if they had to be removed based on
        del_files or add them to new_items based on new_files
        """
        if parent.type != 'dir':
            # don't know what to do here
            return

        # a fxd files may be removed, 'free' covered files
        for fxd_file in util.find_matches(del_files, ['fxd']):
            for i in current_items:
                if i.xml_file == fxd_file and hasattr(i, '_fxd_covered_'):
                    for covered in i._fxd_covered_:
                        if not covered in del_files:
                            new_files.append(covered)
                    del_items.append(i)
                    del_files.remove(fxd_file)


        # a new fxd file may cover items
        fxd_files = util.find_matches(new_files, ['fxd'])
        if fxd_files:
            for f in fxd_files:
                new_files.remove(f)
            copy_all = copy.copy(parent.all_files)
            new_items += self.parse(parent, fxd_files, copy_all)
            for f in parent.all_files:
                if not f in copy_all:
                    # covered by fxd now
                    if not f in new_files:
                        del_files.append(f)
                    else:
                        new_files.remove(f)


    def parse(self, parent, fxd_files, duplicate_check=[], display_type=None):
        """
        return a list of items that belong to a fxd files
        """
        if not display_type:
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
                print "fxd file %s corrupt" % fxd_file
                traceback.print_exc()
        return items



# -------------------------------------------------------------------------------------

class Container(item.Item):
    """
    a simple container containing for items parsed from the fxd
    """
    def __init__(self, fxd, node):
        item.Item.__init__(self, fxd.getattr(None, 'parent', None))
        self.items    = []
        self.name     = fxd.getattr(node, 'title', 'no title')
        self.type     = fxd.getattr(node, 'type', '')
        self.xml_file = fxd.getattr(None, 'filename', '')

        self.image    = fxd.childcontent(node, 'cover-img')
        if self.image:
            self.image = vfs.join(vfs.dirname(self.xml_file), self.image)

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
                
        # restore settings
        fxd.setattr(None, 'parent', self.parent)
        fxd.setattr(None, 'items', parent_items)


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return '%s%s' % (os.stat(self.xml_file).st_ctime, self.xml_file)
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
        moviemenu = menu.Menu(self.name, self.items)
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

