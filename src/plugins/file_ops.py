#if 0 /*
# -----------------------------------------------------------------------
# file_ops.py - Small file operations (currently only delete)
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/09/03 18:03:06  dischi
# fix crash in DEBUG
#
# Revision 1.2  2003/08/31 17:18:33  dischi
# exception handling
#
# Revision 1.1  2003/08/31 17:14:21  dischi
# Move delete file from VideoItem into a global plugin. Now it's also
# possible to remove audio and image files.
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

import os
import config
import plugin

from gui.ConfirmBox import ConfirmBox

TRUE  = 1
FALSE = 0

class PluginInterface(plugin.ItemPlugin):
    """
    small plugin to delete files
    """

    def actions(self, item):
        """
        create list of possible actions
        """
        if ((item.type == 'video' and item.mode == 'file') or \
            item.type in ( 'audio', 'image' )) and not item.media:
            self.item = item
            return [ (self.confirm_delete, 'Delete file', 'delete') ]
        return []


    def confirm_delete(self, arg=None, menuw=None):
        self.menuw = menuw
        ConfirmBox(text='Do you wish to delete\n %s?' % self.item.name,
                   handler=self.delete_file, default_choice=1).show()

    def save_unlink(self, filename):
        try:
            os.unlink(filename)
        except:
            print 'can\'t delete %s' % filename
        
    def delete_file(self):
        if config.DEBUG:
            print 'Deleting %s' % self.item.filename

        if self.item.type in ('video', 'audio'):
            base = os.path.splitext(self.item.filename)[0] + '.'
            if os.path.isfile(base + 'jpg'):
                self.save_unlink(base + 'jpg')
            if os.path.isfile(base + 'png'):
                self.save_unlink(base + 'png')

        if os.path.isfile(self.item.filename):
            self.save_unlink(self.item.filename)

        if self.item.type == 'video' and hasattr(self, 'fxd_file') and \
               os.path.isfile(self.item.fxd_file) and \
               self.item.fxd_file.find(config.MOVIE_DATA_DIR) == -1 and \
               self.item.fxd_file.find(config.TV_SHOW_DATA_DIR) == -1 and \
               self.item.fxd_file.find(config.TV_SHOW_IMAGE_DIR) == -1:
                self.save_unlink(self.item.fxd_file)
        if self.menuw:
            self.menuw.back_one_menu(arg='reload')
