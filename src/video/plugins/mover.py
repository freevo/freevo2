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
# Activate: 
#   plugin.activate('video.mover', args=('from-dir', 'to-dir'))
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
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
    def __init__(self, from_dir, to_dir):
        plugin.ItemPlugin.__init__(self)
        self.from_dir = from_dir
        self.to_dir   = to_dir
        
    def actions(self, item):
        self.item = item
        if item.type == 'video' and item.mode == 'file' and \
           item.parent.type == 'dir' and item.parent.dir == self.from_dir:
            return [ (self.mover_to_series,
                      _('Move to [%s]') % os.path.basename(self.to_dir)) ]
        return []

    def mover_to_series(self, arg=None, menuw=None):
        os.system('mv "%s" "%s"' % (self.item.filename, self.to_dir))
        menuw.delete_menu(menuw=menuw)
