#if 0 /*
# -----------------------------------------------------------------------
# __init__.py - interface between mediamenu and image
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/12/07 11:13:53  dischi
# small bugfix
#
# Revision 1.6  2003/12/06 13:44:12  dischi
# move more info to the Mimetype
#
# Revision 1.5  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
#
# Revision 1.4  2003/11/28 19:26:37  dischi
# renamed some config variables
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

# Add support for bins album files
from mmpython.image import bins

import config
import util
import plugin

from imageitem import ImageItem

class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of audio items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'image' ]

        # activate the mediamenu for image
        plugin.activate('mediamenu', level=plugin.is_active('image')[2], args='image')
        

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.IMAGE_SUFFIX


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        items = []
        for file in util.find_matches(files, config.IMAGE_SUFFIX):
            items.append(ImageItem(file, parent))
            files.remove(file)
        return items


    def update(self, parent, new_files, del_files, new_items, del_items, current_items):
        """
        update a directory. Add items to del_items if they had to be removed based on
        del_files or add them to new_items based on new_files
        """
        for item in current_items:
            for file in util.find_matches(del_files, config.IMAGE_SUFFIX):
                if item.type == 'image' and item.filename == file:
                    del_items += [ item ]
                    del_files.remove(file)

        new_items += cwd(parent, new_files)


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on album.xml
        """
        if vfs.isfile(diritem.dir + '/album.xml'):
            info  = bins.get_bins_desc(diritem.dir)
            if not info.has_key('desc'):
                return

            info = info['desc']
            if info.has_key('sampleimage') and info['sampleimage']:
                image = vfs.join(diritem.dir, info['sampleimage'])
                if vfs.isfile(image):
                    diritem.image       = image
                    diritem.handle_type = diritem.display_type

            if info.has_key('title') and info['title']:
                diritem.name = info['title']
