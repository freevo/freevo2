#if 0 /*
# -----------------------------------------------------------------------
# mover.py - Example item plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is an example how plugins work. This plugin add a move action
#        to movie items in a given directory to move the item to a second
#        given directory.
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2004/01/10 13:23:09  dischi
# use item.files to move
#
# Revision 1.6  2003/11/28 19:26:37  dischi
# renamed some config variables
#
# Revision 1.5  2003/10/16 09:18:20  dischi
# patch from Eirik Meland
#
# Revision 1.4  2003/10/14 18:15:59  dischi
# patch from Eirik Meland
#
# Revision 1.3  2003/09/13 10:08:24  dischi
# i18n support
#
# Revision 1.2  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.1  2003/04/20 11:45:42  dischi
# add an example item plugin
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


import os
import plugin

class PluginInterface(plugin.ItemPlugin):
    """
    Plugin to move video files

    Activate: 
      plugin.activate('video.mover', args=('from-dir', 'to-dir'))
   
    from_dir: from which directory the files should be moved from
    to_dir:   to which directory the files should be moved to
   
    Optional parameters:
    recursive (boolean): should the plugin work for every subdirectory of
                         the from-directory (defaults to False)
   
      This parameter can be used to make a "safe delete function":
      map(lambda dir: plugin.activate('video.mover', args=(dir[1],
                                                           '/mnt/media/trash',
                                                           True)),
          VIDEO_ITEMS)
   
   
    makedirs (boolean): should freevo create the to-dir if it doesn't exist
                        (defaults to False)
   
      This parameter can be used to move seen tv-episodes/movies
      into a subdirectory ('seen'):
   
      map(lambda dir: plugin.activate('video.mover', args=(dir[1],
                                                           'seen',
                                                           True,
                                                           True)),
          VIDEO_ITEMS) 
   
      When to-dir is not specified as an absolute path, the mover will try
      to locate it in the current dir. If makedirs==True and to-dir
      doesn't exist, it will be created in the current-dir.

    """
    def __init__(self, from_dir, to_dir, recursive=False, makedirs=False):
        plugin.ItemPlugin.__init__(self)
        self.from_dir = from_dir
        self.to_dir   = to_dir
        self.recursive = recursive
        self.makedirs =  makedirs
        
    def actions(self, item):
        self.item = item
        if ( item.type == 'video' 
             and item.mode == 'file' 
             and item.parent.type == 'dir' 
             # don't bother moving to current-dir
             and self.to_dir != os.path.dirname(self.item.filename) 
             # recursive
             and ( ( self.recursive 
                     and os.path.commonprefix( ( item.parent.dir, self.from_dir)) == self.from_dir )
                   # or absolute
                   or ( item.parent.dir == self.from_dir))):
            return [ (self.mover_to_series,
                      _('Move to [%s]') % os.path.basename(self.to_dir)) ]
        return []

    def mover_to_series(self, arg=None, menuw=None):
        # make to_dir an absolute path
        local_to_dir = self.to_dir
        if not os.path.isabs(self.to_dir):
            local_to_dir = os.path.join(os.path.dirname(self.item.filename),
                                        self.to_dir)
        

        # make to_dir if it doesn't exist and makedirs==True
        if not os.path.exists(local_to_dir):
            if os.path.exists(os.path.dirname(local_to_dir)):
                if self.makedirs:
                    os.makedirs(local_to_dir)
                else:
                    _debug_("Path doesn't exist, and makedirs=%s" % self.makedirs)
                    menuw.delete_menu(menuw=menuw)
                    return
        elif not os.path.isdir(local_to_dir):
            _debug_("%s is not a dir" % local_to_dir)
            return

        if self.items.files:
            self.items.files.move(local_to_dir)

        menuw.delete_menu(menuw=menuw)
